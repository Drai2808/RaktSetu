"""
BloodFlow AI - Demo Test Script
Demonstrates all major features of the prediction system
"""

import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.append('.')

from models.demand_predictor import BloodDemandPredictor
from models.inventory_optimizer import InventoryOptimizer
from utils.data_generator import generate_historical_data


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print section divider"""
    print(f"\n{'─'*70}")
    print(f"  {text}")
    print(f"{'─'*70}")


def demo_prediction():
    """Demo: Blood demand prediction"""
    print_header("🔮 DEMO 1: AI-Based Blood Demand Prediction")
    
    predictor = BloodDemandPredictor()
    
    # Test for O+ blood type
    blood_type = "O+"
    print(f"\n📊 Predicting demand for {blood_type} (next 7 days)...")
    
    predictions = predictor.predict(blood_type, days_ahead=7)
    
    print(f"\n{'Date':<12} {'Day':<10} {'Demand':<8} {'Range':<15}")
    print("-" * 50)
    for pred in predictions:
        print(f"{pred['date']:<12} {pred['day_name']:<10} "
              f"{pred['predicted_demand']:<8} {pred['confidence_interval']:<15}")
    
    # Generate alerts
    alerts = predictor.generate_alerts(predictions, blood_type)
    if alerts:
        print("\n🚨 ALERTS:")
        for alert in alerts:
            print(f"  • {alert}")
    
    print(f"\n✓ Confidence Score: {predictor.get_confidence_score(blood_type):.1f}%")


def demo_training():
    """Demo: Model training with historical data"""
    print_header("🎓 DEMO 2: Model Training with Historical Data")
    
    predictor = BloodDemandPredictor()
    
    blood_type = "O+"
    print(f"\n📚 Generating 365 days of historical data for {blood_type}...")
    historical_data = generate_historical_data(blood_type, days=365)
    
    print(f"✓ Generated {len(historical_data)} days of data")
    print(f"\n📈 Data statistics:")
    print(f"  • Mean demand: {historical_data['demand'].mean():.1f} units/day")
    print(f"  • Max demand: {historical_data['demand'].max()} units")
    print(f"  • Min demand: {historical_data['demand'].min()} units")
    
    print(f"\n🤖 Training ML model...")
    time.sleep(1)  # Simulate processing
    
    metrics = predictor.train(blood_type, historical_data)
    
    print(f"\n✅ Training Complete!")
    print(f"  • MAE: {metrics['mae']:.2f} units")
    print(f"  • RMSE: {metrics['rmse']:.2f} units")
    print(f"  • R² Score: {metrics['r2_score']:.3f}")
    print(f"  • Training samples: {metrics['training_samples']}")


def demo_inventory_optimization():
    """Demo: Inventory status and optimization"""
    print_header("📦 DEMO 3: Smart Inventory Management")
    
    optimizer = InventoryOptimizer()
    
    print("\n📊 Current Inventory Status (All Blood Types):")
    print(f"\n{'Type':<6} {'Stock':<7} {'Safety':<8} {'Status':<10} {'Urgency':<10}")
    print("-" * 55)
    
    all_statuses = []
    for blood_type in ["O+", "A+", "B+", "O-", "A-", "AB+", "B-", "AB-"]:
        status = optimizer.get_inventory_status(blood_type)
        all_statuses.append(status)
        
        urgency_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        print(f"{blood_type:<6} {status['current_stock']:<7} "
              f"{status['safety_stock']:<8} "
              f"{status['stock_percentage']:.1f}%{'':>5} "
              f"{urgency_emoji[status['urgency_level']]} {status['urgency_level']:<10}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for status in all_statuses:
        if status['urgency_level'] in ['critical', 'high']:
            print(f"  • {status['recommendation']}")


def demo_redistribution():
    """Demo: Smart redistribution suggestions"""
    print_header("🚚 DEMO 4: Multi-Location Redistribution")
    
    optimizer = InventoryOptimizer()
    
    print("\n🗺️  Analyzing inventory across multiple locations...")
    suggestions = optimizer.get_redistribution_suggestions()
    
    if suggestions:
        print(f"\n✓ Found {len(suggestions)} redistribution opportunities:\n")
        
        for i, sug in enumerate(suggestions[:5], 1):  # Show top 5
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            print(f"{i}. {priority_emoji[sug['priority']]} [{sug['blood_type']}] "
                  f"{sug['from_location']} → {sug['to_location']}")
            print(f"   Transfer: {sug['units']} units")
            print(f"   Reason: {sug['reason']}\n")
        
        waste_reduction = optimizer.calculate_waste_reduction(suggestions)
        print(f"💰 POTENTIAL SAVINGS:")
        print(f"  • Units redistributed: {waste_reduction['units_redistributed']}")
        print(f"  • Waste prevented: {waste_reduction['waste_units_prevented']} units")
        print(f"  • Cost savings: ${waste_reduction['estimated_cost_savings']:,}")
    else:
        print("✓ No redistribution needed - all locations well balanced")


def demo_scenario_simulation():
    """Demo: What-if scenario analysis"""
    print_header("🎯 DEMO 5: Emergency Scenario Simulation")
    
    predictor = BloodDemandPredictor()
    
    scenarios = [
        ("highway_accident", "high"),
        ("dengue_outbreak", "medium"),
        ("festival", "low")
    ]
    
    for scenario, severity in scenarios:
        print_section(f"Scenario: {scenario.replace('_', ' ').title()} (Severity: {severity})")
        
        results = predictor.simulate_scenario(scenario, severity)
        recommendations = predictor.get_scenario_recommendations(results)
        
        # Show top impacted blood types
        sorted_results = sorted(
            results.items(), 
            key=lambda x: x[1]['additional_units_needed'], 
            reverse=True
        )[:4]
        
        print(f"\n{'Type':<6} {'Baseline':<10} {'Surge':<10} {'+Units':<10} {'%Change':<10}")
        print("-" * 50)
        for blood_type, data in sorted_results:
            print(f"{blood_type:<6} {data['baseline_demand']:<10} "
                  f"{data['surge_demand']:<10} "
                  f"+{data['additional_units_needed']:<9} "
                  f"+{data['percentage_increase']:.1f}%")
        
        print(f"\n📋 Recommendations:")
        for rec in recommendations[:3]:
            print(f"  • {rec}")


def demo_alerts_system():
    """Demo: Intelligent alerts"""
    print_header("🔔 DEMO 6: Smart Alert System")
    
    predictor = BloodDemandPredictor()
    
    print("\n📢 Generating alerts for all blood types...\n")
    
    all_alerts = []
    for blood_type in ["O+", "A+", "B+", "O-"]:
        predictions = predictor.predict(blood_type, days_ahead=7)
        alerts = predictor.generate_alerts(predictions, blood_type)
        
        for alert in alerts:
            urgency = predictor.determine_urgency(alert)
            all_alerts.append({
                'blood_type': blood_type,
                'message': alert,
                'urgency': urgency
            })
    
    # Sort by urgency
    urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_alerts.sort(key=lambda x: urgency_order[x['urgency']])
    
    # Display by urgency
    for urgency_level in ['critical', 'high', 'medium']:
        level_alerts = [a for a in all_alerts if a['urgency'] == urgency_level]
        if level_alerts:
            print(f"\n{urgency_level.upper()} PRIORITY:")
            for alert in level_alerts:
                print(f"  [{alert['blood_type']}] {alert['message']}")
    
    print(f"\n✓ Total alerts generated: {len(all_alerts)}")


def run_all_demos():
    """Run all demonstration scenarios"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║              🩸 BLOODFLOW AI - SYSTEM DEMONSTRATION 🤖             ║")
    print("║                                                                    ║")
    print("║            Intelligent Blood Bank Management System                ║")
    print("║                  AI-Powered Demand Prediction                      ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\n⏱️  Demo will run through 6 key features...")
    print("   Press Ctrl+C to stop at any time\n")
    
    time.sleep(2)
    
    try:
        # Run all demos
        demo_prediction()
        time.sleep(2)
        
        demo_training()
        time.sleep(2)
        
        demo_inventory_optimization()
        time.sleep(2)
        
        demo_redistribution()
        time.sleep(2)
        
        demo_scenario_simulation()
        time.sleep(2)
        
        demo_alerts_system()
        
        # Summary
        print_header("✅ DEMO COMPLETE")
        print("\n🎉 All features demonstrated successfully!")
        print("\n📚 Key Capabilities Shown:")
        print("  ✓ AI-based demand forecasting (7-30 days)")
        print("  ✓ Machine learning model training")
        print("  ✓ Real-time inventory monitoring")
        print("  ✓ Multi-location optimization")
        print("  ✓ Emergency scenario simulation")
        print("  ✓ Intelligent alert generation")
        print("\n🚀 Next Steps:")
        print("  • Run the API: python main.py")
        print("  • View docs: http://localhost:8000/docs")
        print("  • Start building the frontend!")
        print("\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        print("✓ Partial demo complete\n")


if __name__ == "__main__":
    run_all_demos()
