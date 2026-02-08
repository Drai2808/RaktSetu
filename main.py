from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import os
import sys
import time
import subprocess

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.demand_predictor import BloodDemandPredictor
from models.inventory_optimizer import InventoryOptimizer
from models.blockchain_traceability import blood_blockchain, BloodUnitBlockchain
from models.donor_intelligence import DonorIntelligence
from models.notification_system import SmartNotificationSystem, NotificationType
from utils.data_generator import generate_historical_data

# Database imports
from database.models import init_database, populate_initial_data, get_session
from database.kaggle_loader import KaggleDataLoader
from database.db_manager import db_manager


def initialize_database():
    """
    Auto-initialize database on first run
    """
    db_file = "bloodflow.db"
    
    if not os.path.exists(db_file):
        print("\n" + "="*70)
        print("  🗄️  DATABASE NOT FOUND - INITIALIZING...")
        print("="*70 + "\n")
        
        # Create database
        print("Step 1: Creating database and tables...")
        engine = init_database()
        session = get_session(engine)
        
        # Initial configuration
        print("Step 2: Adding initial configuration...")
        populate_initial_data(session)
        session.close()
        
        # Load data
        print("Step 3: Loading donor data and history...")
        loader = KaggleDataLoader()
        loader.import_all_data(kaggle_csv=None)  # Uses synthetic data
        
        print("\n" + "="*70)
        print("  ✅ DATABASE INITIALIZED SUCCESSFULLY!")
        print("="*70 + "\n")
    else:
        print("✓ Database found - using existing data")
        # Verify database
        stats = db_manager.get_database_stats()
        print(f"  Donors: {stats['total_donors']}")
        print(f"  Donations: {stats['total_donations']}")
        print(f"  Demand Records: {stats['total_demand_records']}")


# Initialize database before app starts
print("\n🩸 RaktSetu - Starting...")
initialize_database()

app = FastAPI(
    title=" RaktSetu AI",
    description="AI-Based Predictive Blood Inventory Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
print("✓ Initializing AI models...")
predictor = BloodDemandPredictor()
optimizer = InventoryOptimizer()
donor_intel = DonorIntelligence()
notification_system = SmartNotificationSystem()
print("✓ All systems ready!\n")


# Pydantic Models
class BloodType(BaseModel):
    blood_type: str = Field(..., description="Blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)")


class PredictionRequest(BaseModel):
    blood_type: str
    days_ahead: int = Field(default=7, ge=1, le=30, description="Number of days to predict")
    location: Optional[str] = Field(default="main_bank", description="Blood bank location")


class PredictionResponse(BaseModel):
    blood_type: str
    predictions: List[Dict[str, Any]]
    alerts: List[str]
    confidence_score: float
    generated_at: datetime


class InventoryStatus(BaseModel):
    blood_type: str
    current_stock: int
    predicted_demand: int
    days_until_shortage: Optional[int]
    recommendation: str
    urgency_level: str  # low, medium, high, critical


class TrainingRequest(BaseModel):
    blood_type: str
    retrain: bool = True


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "BloodFlow AI - Predictive Inventory Management",
        "version": "1.0.0",
        "features": [
            "AI-Based Demand Prediction",
            "Blockchain Traceability",
            "Donor Intelligence & Analytics",
            "Smart Notification System",
            "Emergency Mode",
            "Inventory Optimization"
        ],
        "endpoints": {
            "prediction": {
                "predict": "/api/v1/predict",
                "inventory": "/api/v1/inventory/status",
                "alerts": "/api/v1/alerts",
                "train": "/api/v1/train",
                "simulation": "/api/v1/simulation",
                "redistribution": "/api/v1/optimization/redistribute"
            },
            "blockchain": {
                "create_unit": "/api/v1/blockchain/unit/create",
                "get_history": "/api/v1/blockchain/unit/{unit_id}",
                "add_test": "/api/v1/blockchain/unit/test",
                "transfer": "/api/v1/blockchain/unit/transfer",
                "info": "/api/v1/blockchain/info"
            },
            "donor_intelligence": {
                "segments": "/api/v1/donors/segments",
                "retention": "/api/v1/donors/retention",
                "dropout_analysis": "/api/v1/donors/dropout-analysis",
                "scarcity_index": "/api/v1/donors/scarcity-index",
                "geographic_heatmap": "/api/v1/donors/geographic-heatmap",
                "top_donors": "/api/v1/donors/top-reliable",
                "target_list": "/api/v1/donors/target-list"
            },
            "notifications": {
                "urgency": "/api/v1/notifications/urgency",
                "event": "/api/v1/notifications/event",
                "thank_you": "/api/v1/notifications/thank-you",
                "analytics": "/api/v1/notifications/analytics"
            },
            "emergency": {
                "activate": "/api/v1/emergency/activate",
                "status": "/api/v1/emergency/status"
            }
        },
        "documentation": "/docs"
    }


@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_demand(request: PredictionRequest):
    """
    Predict blood demand for specified blood type and time period
    
    Uses historical data, seasonal trends, and ML models to forecast demand
    """
    try:
        # Validate blood type
        valid_blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if request.blood_type not in valid_blood_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid blood type. Must be one of: {', '.join(valid_blood_types)}"
            )
        
        # Generate predictions
        predictions = predictor.predict(
            blood_type=request.blood_type,
            days_ahead=request.days_ahead,
            location=request.location
        )
        
        # Generate alerts based on predictions
        alerts = predictor.generate_alerts(predictions, request.blood_type)
        
        # Calculate confidence score
        confidence = predictor.get_confidence_score(request.blood_type)
        
        return PredictionResponse(
            blood_type=request.blood_type,
            predictions=predictions,
            alerts=alerts,
            confidence_score=confidence,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/api/v1/inventory/status")
async def get_inventory_status(blood_type: Optional[str] = None):
    """
    Get current inventory status with AI-powered recommendations
    
    Returns stock levels, predicted demand, and actionable recommendations
    """
    try:
        all_blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        blood_types_to_check = [blood_type] if blood_type else all_blood_types
        
        statuses = []
        
        for bt in blood_types_to_check:
            status = optimizer.get_inventory_status(bt)
            statuses.append(status)
        
        return {
            "timestamp": datetime.now(),
            "inventory_status": statuses,
            "critical_count": len([s for s in statuses if s["urgency_level"] == "critical"]),
            "overall_health": optimizer.calculate_overall_health(statuses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inventory status error: {str(e)}")


@app.get("/api/v1/alerts")
async def get_alerts(urgency: Optional[str] = None):
    """
    Get all active alerts and warnings
    
    Filters by urgency level: low, medium, high, critical
    """
    try:
        all_alerts = []
        blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        for bt in blood_types:
            predictions = predictor.predict(bt, days_ahead=7)
            alerts = predictor.generate_alerts(predictions, bt)
            
            for alert in alerts:
                all_alerts.append({
                    "blood_type": bt,
                    "message": alert,
                    "urgency": predictor.determine_urgency(alert),
                    "timestamp": datetime.now()
                })
        
        # Filter by urgency if specified
        if urgency:
            all_alerts = [a for a in all_alerts if a["urgency"] == urgency.lower()]
        
        # Sort by urgency
        urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_alerts.sort(key=lambda x: urgency_order.get(x["urgency"], 4))
        
        return {
            "total_alerts": len(all_alerts),
            "alerts": all_alerts,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alerts error: {str(e)}")


@app.post("/api/v1/train")
async def train_model(request: TrainingRequest):
    """
    Train or retrain the prediction model for a specific blood type
    
    Uses historical data to improve prediction accuracy
    """
    try:
        if request.retrain:
            # Generate synthetic historical data (in production, use real data)
            historical_data = generate_historical_data(
                blood_type=request.blood_type,
                days=365
            )
            
            # Train the model
            metrics = predictor.train(
                blood_type=request.blood_type,
                data=historical_data
            )
            
            return {
                "status": "success",
                "blood_type": request.blood_type,
                "training_metrics": metrics,
                "timestamp": datetime.now()
            }
        else:
            return {
                "status": "skipped",
                "message": "Retrain flag set to False"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")


@app.get("/api/v1/optimization/redistribute")
async def get_redistribution_suggestions():
    """
    AI-powered suggestions for redistributing blood units between locations
    
    Optimizes inventory across multiple blood banks
    """
    try:
        suggestions = optimizer.get_redistribution_suggestions()
        
        return {
            "suggestions": suggestions,
            "potential_waste_reduction": optimizer.calculate_waste_reduction(suggestions),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


@app.get("/api/v1/simulation")
async def run_simulation(scenario: str, severity: str = "medium"):
    """
    What-if scenario simulation
    
    Scenarios: highway_accident, festival, dengue_outbreak, monsoon
    Severity: low, medium, high
    """
    try:
        valid_scenarios = ["highway_accident", "festival", "dengue_outbreak", "monsoon"]
        if scenario not in valid_scenarios:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scenario. Choose from: {', '.join(valid_scenarios)}"
            )
        
        simulation_results = predictor.simulate_scenario(scenario, severity)
        
        return {
            "scenario": scenario,
            "severity": severity,
            "results": simulation_results,
            "recommendations": predictor.get_scenario_recommendations(simulation_results),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


# ==================== BLOCKCHAIN TRACEABILITY ====================

@app.post("/api/v1/blockchain/unit/create")
async def create_blood_unit(donor_id: str, blood_type: str, collection_date: str, location: str):
    """
    Create new blood unit on blockchain
    
    Returns unique blockchain ID for traceability
    """
    try:
        unit_id = blood_blockchain.create_blood_unit(
            donor_id=donor_id,
            blood_type=blood_type,
            collection_date=collection_date,
            location=location
        )
        
        # Mine the transaction
        blood_blockchain.mine_pending_transactions()
        
        return {
            "status": "success",
            "unit_id": unit_id,
            "blood_type": blood_type,
            "message": "Blood unit registered on blockchain",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain error: {str(e)}")


@app.get("/api/v1/blockchain/unit/{unit_id}")
async def get_unit_history(unit_id: str):
    """
    Get complete traceability history of a blood unit
    
    Returns all transactions from collection to transfusion
    """
    try:
        history = blood_blockchain.get_unit_history(unit_id)
        verification = blood_blockchain.verify_unit_authenticity(unit_id)
        
        return {
            "unit_id": unit_id,
            "history": history,
            "verification": verification,
            "total_records": len(history),
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain query error: {str(e)}")


@app.post("/api/v1/blockchain/unit/test")
async def add_testing_record(unit_id: str, test_passed: bool, tested_by: str):
    """Add testing results to blockchain"""
    try:
        blood_blockchain.add_testing_record(
            unit_id=unit_id,
            test_results={
                "passed": test_passed,
                "technician_id": tested_by,
                "tests_performed": ["HIV", "Hepatitis B", "Hepatitis C", "Syphilis"]
            }
        )
        
        return {
            "status": "success",
            "message": "Testing record added to blockchain",
            "unit_id": unit_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain update error: {str(e)}")


@app.post("/api/v1/blockchain/unit/transfer")
async def transfer_blood_unit(unit_id: str, from_location: str, to_location: str, transported_by: str):
    """Record blood unit transfer on blockchain"""
    try:
        blood_blockchain.add_transfer_record(
            unit_id=unit_id,
            from_location=from_location,
            to_location=to_location,
            transported_by=transported_by
        )
        
        return {
            "status": "success",
            "message": "Transfer recorded on blockchain",
            "unit_id": unit_id,
            "from": from_location,
            "to": to_location
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain transfer error: {str(e)}")


@app.get("/api/v1/blockchain/info")
async def get_blockchain_info():
    """Get blockchain statistics and health"""
    try:
        info = blood_blockchain.get_chain_info()
        return {
            "blockchain_info": info,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain info error: {str(e)}")


# ==================== DONOR INTELLIGENCE ====================

@app.get("/api/v1/donors/segments")
async def get_donor_segments():
    """
    Get donor segmentation analysis
    
    Returns donors grouped by engagement level
    """
    try:
        segments = donor_intel.segment_donors()
        
        return {
            "segments": {
                name: {
                    "count": len(donors),
                    "donors": donors[:5]  # Return first 5 as sample
                }
                for name, donors in segments.items()
            },
            "summary": {
                name: len(donors) for name, donors in segments.items()
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Donor segmentation error: {str(e)}")


@app.get("/api/v1/donors/retention")
async def get_retention_metrics():
    """Get donor retention statistics"""
    try:
        metrics = donor_intel.get_donor_retention_rate()
        
        return {
            "retention_metrics": metrics,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retention analysis error: {str(e)}")


@app.get("/api/v1/donors/dropout-analysis")
async def get_dropout_analysis():
    """
    Analyze why donors stop donating
    
    Provides insights and recommendations
    """
    try:
        analysis = donor_intel.analyze_drop_off()
        
        return {
            "dropout_analysis": analysis,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dropout analysis error: {str(e)}")


@app.get("/api/v1/donors/scarcity-index")
async def get_scarcity_index():
    """
    Get blood type scarcity index
    
    Shows which blood types have lowest donor availability
    """
    try:
        index = donor_intel.get_blood_type_scarcity_index()
        
        return {
            "scarcity_index": index,
            "critical_types": [bt for bt, data in index.items() if data["urgency"] == "critical"],
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scarcity index error: {str(e)}")


@app.get("/api/v1/donors/geographic-heatmap")
async def get_geographic_distribution():
    """Get geographic distribution of donors"""
    try:
        heatmap = donor_intel.get_geographic_heatmap()
        
        return {
            "geographic_distribution": heatmap,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geographic analysis error: {str(e)}")


@app.get("/api/v1/donors/top-reliable")
async def get_top_donors(top_n: int = 20):
    """Get most reliable donors"""
    try:
        top_donors = donor_intel.get_donor_reliability_scores(top_n)
        
        return {
            "top_donors": top_donors,
            "count": len(top_donors),
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Donor ranking error: {str(e)}")


@app.get("/api/v1/donors/target-list")
async def get_targeted_donors(blood_type: str, max_donors: int = 20, emergency: bool = False):
    """
    Get targeted list of donors to contact
    
    Used for donation campaigns and emergencies
    """
    try:
        donors = donor_intel.get_targeted_donor_list(blood_type, max_donors, emergency)
        
        return {
            "blood_type": blood_type,
            "targeted_donors": donors,
            "count": len(donors),
            "emergency_mode": emergency,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Donor targeting error: {str(e)}")


# ==================== NOTIFICATION SYSTEM ====================

@app.post("/api/v1/notifications/urgency")
async def send_urgency_notification(blood_type: str, units_needed: int, location: str, urgency: str = "high"):
    """Send urgent shortage notification"""
    try:
        notification = notification_system.create_urgency_notification(
            blood_type=blood_type,
            units_needed=units_needed,
            location=location,
            urgency=urgency
        )
        
        result = notification_system.send_notification(notification)
        
        return {
            "notification": notification,
            "delivery": result,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notification error: {str(e)}")


@app.post("/api/v1/notifications/event")
async def send_event_notification(event_type: str, blood_types_needed: List[str], impact_description: str):
    """
    Send event-triggered notification
    
    For accidents, disasters, outbreaks
    """
    try:
        notification = notification_system.create_event_notification(
            event_type=event_type,
            blood_types_needed=blood_types_needed,
            impact_description=impact_description
        )
        
        result = notification_system.send_notification(notification)
        
        return {
            "notification": notification,
            "delivery": result,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event notification error: {str(e)}")


@app.post("/api/v1/notifications/thank-you")
async def send_thank_you(donor_name: str, blood_type: str, donation_date: str):
    """Send thank you notification after donation"""
    try:
        notification = notification_system.create_thank_you_notification(
            donor_name=donor_name,
            blood_type=blood_type,
            donation_date=donation_date
        )
        
        result = notification_system.send_notification(notification)
        
        return {
            "notification": notification,
            "delivery": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thank you notification error: {str(e)}")


@app.get("/api/v1/notifications/analytics")
async def get_notification_analytics():
    """Get notification performance analytics"""
    try:
        analytics = notification_system.get_notification_analytics()
        
        return {
            "analytics": analytics,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")


# ==================== EMERGENCY MODE ====================

@app.post("/api/v1/emergency/activate")
async def activate_emergency_mode(event_type: str, blood_types_needed: List[str], severity: str = "high"):
    """
    Activate Emergency Mode
    
    One-click emergency response:
    - Sends urgent notifications to all eligible donors
    - Shows real-time availability
    - Fast donor matching
    - Overrides normal rules
    """
    try:
        # Get targeted donors for each blood type
        all_contacted_donors = []
        
        for blood_type in blood_types_needed:
            donors = donor_intel.get_targeted_donor_list(
                blood_type=blood_type,
                max_donors=50,
                emergency=True
            )
            all_contacted_donors.extend(donors)
            
            # Send emergency notifications
            notification = notification_system.create_event_notification(
                event_type=event_type,
                blood_types_needed=[blood_type],
                impact_description=f"Emergency mode activated - {severity} severity event"
            )
            notification_system.send_notification(notification)
        
        # Get current inventory
        inventory_status = []
        for bt in blood_types_needed:
            status = optimizer.get_inventory_status(bt)
            inventory_status.append(status)
        
        return {
            "status": "EMERGENCY_MODE_ACTIVE",
            "event_type": event_type,
            "severity": severity,
            "blood_types_needed": blood_types_needed,
            "donors_contacted": len(all_contacted_donors),
            "notifications_sent": len(blood_types_needed),
            "current_inventory": inventory_status,
            "message": f"Emergency mode activated. {len(all_contacted_donors)} donors notified.",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency activation error: {str(e)}")


@app.get("/api/v1/emergency/status")
async def get_emergency_status():
    """Get current emergency response status"""
    try:
        # Get critical inventory items
        all_statuses = []
        for blood_type in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            status = optimizer.get_inventory_status(blood_type)
            if status["urgency_level"] in ["critical", "high"]:
                all_statuses.append(status)
        
        # Get emergency-ready donors
        emergency_donors = len(donor_intel.donors[
            donor_intel.donors["emergency_available"] & 
            donor_intel.donors["eligible"]
        ])
        
        return {
            "critical_inventory": all_statuses,
            "emergency_ready_donors": emergency_donors,
            "status": "NORMAL" if len(all_statuses) == 0 else "ALERT",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency status error: {str(e)}")


if __name__ == "__main__":
    import subprocess
    import platform
    import webbrowser
    import threading
    
    print("\n" + "="*70)
    print("  🩸 RaktSetu AI - COMPLETE SYSTEM")
    print("="*70)
    
    # Function to launch Streamlit
    def launch_streamlit():
        time.sleep(3)  # Wait for backend to start
        print("\n🎨 Launching Streamlit dashboard...")
        
        try:
            # Launch Streamlit
            subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.headless", "true"
            ])
            
            # Wait a bit then open browser
            time.sleep(5)
            print("✓ Frontend started!")
            print("✓ Opening browser...")
            webbrowser.open("http://localhost:8501")
            
        except Exception as e:
            print(f"⚠️  Could not auto-launch frontend: {e}")
            print("   You can manually start it with: streamlit run app.py")
    
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=launch_streamlit, daemon=True)
    streamlit_thread.start()
    
    print("\n🚀 Starting Backend API...")
    print("   Backend: http://localhost:8000")
    print("   Frontend: http://localhost:8501 (launching...)")
    print("   API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both servers\n")
    
    # Start FastAPI
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down RaktSetu AI...")
        print("  Thank you for using RaktSetu AI! 🩸\n")
