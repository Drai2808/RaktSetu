"""
Blood Demand Predictor
Uses multiple ML techniques for accurate forecasting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')


class BloodDemandPredictor:
    """
    AI-based blood demand prediction system
    
    Features:
    - Time series forecasting
    - Seasonal pattern detection
    - Event-based surge prediction
    - Multi-model ensemble
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_history = {}
        self.blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        # Blood type demand patterns (baseline)
        self.baseline_demand = {
            "O+": 40,  # Most common, highest demand
            "A+": 35,
            "B+": 25,
            "O-": 15,  # Universal donor, critical
            "A-": 12,
            "AB+": 10,
            "B-": 8,
            "AB-": 5   # Rarest
        }
        
        # Seasonal multipliers
        self.seasonal_factors = {
            "monsoon": 1.3,      # More accidents
            "festival": 1.25,    # Increased activity
            "exam_season": 1.1,  # Stress-related
            "winter": 0.95,
            "summer": 1.05
        }
        
    def create_features(self, date: datetime, blood_type: str) -> np.ndarray:
        """
        Engineer features for prediction
        
        Features include:
        - Day of week
        - Month
        - Is weekend
        - Is holiday season
        - Seasonal indicators
        - Blood type specific patterns
        """
        features = []
        
        # Temporal features
        features.append(date.weekday())  # 0-6
        features.append(date.month)      # 1-12
        features.append(date.day)        # 1-31
        features.append(1 if date.weekday() >= 5 else 0)  # is_weekend
        
        # Seasonal indicators
        month = date.month
        features.append(1 if month in [6, 7, 8] else 0)  # monsoon
        features.append(1 if month in [10, 11] else 0)   # festival season
        features.append(1 if month in [3, 4, 5, 11, 12] else 0)  # exam season
        
        # Cyclical encoding for month (captures seasonality better)
        features.append(np.sin(2 * np.pi * month / 12))
        features.append(np.cos(2 * np.pi * month / 12))
        
        # Cyclical encoding for day of week
        dow = date.weekday()
        features.append(np.sin(2 * np.pi * dow / 7))
        features.append(np.cos(2 * np.pi * dow / 7))
        
        # Blood type rarity indicator (affects demand patterns)
        rarity = list(self.baseline_demand.keys()).index(blood_type) / 8
        features.append(rarity)
        
        return np.array(features)
    
    def train(self, blood_type: str, data: pd.DataFrame) -> Dict:
        """
        Train prediction model for specific blood type
        
        Args:
            blood_type: Blood type to train for
            data: Historical data with columns: date, demand
        
        Returns:
            Training metrics
        """
        print(f"Training model for {blood_type}...")
        
        # Prepare features
        X = []
        y = []
        
        for idx, row in data.iterrows():
            features = self.create_features(row['date'], blood_type)
            X.append(features)
            y.append(row['demand'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split train/test
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train ensemble of models
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        
        rf_model.fit(X_train_scaled, y_train)
        gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        rf_pred = rf_model.predict(X_test_scaled)
        gb_pred = gb_model.predict(X_test_scaled)
        
        # Ensemble prediction (average)
        ensemble_pred = (rf_pred + gb_pred) / 2
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, ensemble_pred)
        rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
        r2 = r2_score(y_test, ensemble_pred)
        
        # Store models
        self.models[blood_type] = {
            'rf': rf_model,
            'gb': gb_model
        }
        self.scalers[blood_type] = scaler
        
        # Store metrics
        metrics = {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2_score': float(r2),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        self.training_history[blood_type] = metrics
        
        print(f"✓ Training complete for {blood_type}")
        print(f"  MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.3f}")
        
        return metrics
    
    def predict(self, blood_type: str, days_ahead: int = 7, location: str = "main_bank") -> List[Dict]:
        """
        Predict blood demand for upcoming days
        
        Args:
            blood_type: Blood type to predict
            days_ahead: Number of days to forecast
            location: Blood bank location
        
        Returns:
            List of predictions with dates and confidence intervals
        """
        # Check if model exists, if not use baseline
        if blood_type not in self.models:
            print(f"No trained model for {blood_type}, using baseline predictions")
            return self._baseline_predict(blood_type, days_ahead)
        
        predictions = []
        start_date = datetime.now()
        
        for day in range(days_ahead):
            pred_date = start_date + timedelta(days=day)
            
            # Create features
            features = self.create_features(pred_date, blood_type)
            features_scaled = self.scalers[blood_type].transform([features])
            
            # Get predictions from both models
            rf_pred = self.models[blood_type]['rf'].predict(features_scaled)[0]
            gb_pred = self.models[blood_type]['gb'].predict(features_scaled)[0]
            
            # Ensemble prediction
            demand = (rf_pred + gb_pred) / 2
            
            # Apply location-specific adjustments (if needed)
            demand = self._apply_location_factor(demand, location)
            
            # Ensure non-negative
            demand = max(0, demand)
            
            # Calculate confidence interval (simple approach)
            std_dev = abs(rf_pred - gb_pred) / 2
            confidence_lower = max(0, demand - 1.96 * std_dev)
            confidence_upper = demand + 1.96 * std_dev
            
            predictions.append({
                "date": pred_date.strftime("%Y-%m-%d"),
                "day_name": pred_date.strftime("%A"),
                "predicted_demand": int(round(demand)),
                "confidence_lower": int(round(confidence_lower)),
                "confidence_upper": int(round(confidence_upper)),
                "confidence_interval": f"{int(round(confidence_lower))}-{int(round(confidence_upper))}"
            })
        
        return predictions
    
    def _baseline_predict(self, blood_type: str, days_ahead: int) -> List[Dict]:
        """Fallback prediction using baseline patterns"""
        predictions = []
        start_date = datetime.now()
        base_demand = self.baseline_demand[blood_type]
        
        for day in range(days_ahead):
            pred_date = start_date + timedelta(days=day)
            
            # Apply day-of-week variation
            dow_factor = 1.2 if pred_date.weekday() < 5 else 0.8  # Higher on weekdays
            
            # Apply monthly variation
            month_factor = 1.1 if pred_date.month in [6, 7, 8, 10, 11] else 1.0
            
            # Random variation
            random_factor = np.random.uniform(0.9, 1.1)
            
            demand = base_demand * dow_factor * month_factor * random_factor
            
            predictions.append({
                "date": pred_date.strftime("%Y-%m-%d"),
                "day_name": pred_date.strftime("%A"),
                "predicted_demand": int(round(demand)),
                "confidence_lower": int(round(demand * 0.85)),
                "confidence_upper": int(round(demand * 1.15)),
                "confidence_interval": f"{int(round(demand * 0.85))}-{int(round(demand * 1.15))}"
            })
        
        return predictions
    
    def _apply_location_factor(self, demand: float, location: str) -> float:
        """Apply location-specific demand multiplier"""
        location_factors = {
            "main_bank": 1.0,
            "city_hospital": 1.2,
            "rural_center": 0.7,
            "trauma_center": 1.5
        }
        return demand * location_factors.get(location, 1.0)
    
    def generate_alerts(self, predictions: List[Dict], blood_type: str) -> List[str]:
        """
        Generate actionable alerts based on predictions
        
        Returns:
            List of alert messages
        """
        alerts = []
        
        # Check for high demand days
        for pred in predictions:
            if pred['predicted_demand'] > self.baseline_demand[blood_type] * 1.5:
                alerts.append(
                    f"⚠️ HIGH DEMAND ALERT: {blood_type} demand predicted to reach "
                    f"{pred['predicted_demand']} units on {pred['date']} ({pred['day_name']})"
                )
        
        # Check for sustained high demand
        avg_demand = np.mean([p['predicted_demand'] for p in predictions])
        if avg_demand > self.baseline_demand[blood_type] * 1.3:
            alerts.append(
                f"📈 SUSTAINED HIGH DEMAND: {blood_type} average demand "
                f"{int(avg_demand)} units over next {len(predictions)} days"
            )
        
        # Check for upcoming weekend
        weekend_preds = [p for p in predictions if p['day_name'] in ['Saturday', 'Sunday']]
        if weekend_preds:
            weekend_avg = np.mean([p['predicted_demand'] for p in weekend_preds])
            if weekend_avg < self.baseline_demand[blood_type] * 0.7:
                alerts.append(
                    f"📉 WEEKEND DIP: {blood_type} demand expected to drop "
                    f"to {int(weekend_avg)} units on weekends"
                )
        
        # Add shortage warning if needed
        total_predicted = sum([p['predicted_demand'] for p in predictions[:3]])
        if total_predicted > self.baseline_demand[blood_type] * 3 * 1.4:
            alerts.append(
                f"🚨 SHORTAGE RISK: {blood_type} predicted demand of {total_predicted} "
                f"units in next 3 days - consider stock increase"
            )
        
        return alerts
    
    def get_confidence_score(self, blood_type: str) -> float:
        """Get model confidence score based on training metrics"""
        if blood_type in self.training_history:
            r2 = self.training_history[blood_type]['r2_score']
            # Convert R² to confidence percentage
            return min(max(r2 * 100, 0), 100)
        return 70.0  # Default baseline confidence
    
    def determine_urgency(self, alert: str) -> str:
        """Determine urgency level from alert message"""
        if "🚨" in alert or "SHORTAGE" in alert:
            return "critical"
        elif "⚠️" in alert or "HIGH DEMAND" in alert:
            return "high"
        elif "📈" in alert or "SUSTAINED" in alert:
            return "medium"
        else:
            return "low"
    
    def simulate_scenario(self, scenario: str, severity: str) -> Dict:
        """
        Simulate what-if scenarios
        
        Scenarios: highway_accident, festival, dengue_outbreak, monsoon
        """
        multipliers = {
            "low": 1.2,
            "medium": 1.5,
            "high": 2.0
        }
        
        base_multiplier = multipliers.get(severity, 1.5)
        
        scenario_impacts = {
            "highway_accident": {
                "O+": base_multiplier * 1.5,
                "O-": base_multiplier * 2.0,  # Universal donor critical
                "A+": base_multiplier * 1.3,
                "A-": base_multiplier * 1.3,
                "B+": base_multiplier * 1.2,
                "B-": base_multiplier * 1.2,
                "AB+": base_multiplier * 1.1,
                "AB-": base_multiplier * 1.1
            },
            "dengue_outbreak": {
                blood_type: base_multiplier * 1.8 for blood_type in self.blood_types
            },
            "festival": {
                blood_type: base_multiplier * 1.3 for blood_type in self.blood_types
            },
            "monsoon": {
                blood_type: base_multiplier * 1.4 for blood_type in self.blood_types
            }
        }
        
        impact = scenario_impacts.get(scenario, {})
        
        results = {}
        for blood_type in self.blood_types:
            baseline = self.baseline_demand[blood_type]
            surge_demand = int(baseline * impact.get(blood_type, base_multiplier))
            
            results[blood_type] = {
                "baseline_demand": baseline,
                "surge_demand": surge_demand,
                "additional_units_needed": surge_demand - baseline,
                "percentage_increase": round(((surge_demand / baseline) - 1) * 100, 1)
            }
        
        return results
    
    def get_scenario_recommendations(self, simulation_results: Dict) -> List[str]:
        """Generate recommendations based on simulation"""
        recommendations = []
        
        critical_types = []
        for blood_type, data in simulation_results.items():
            if data['additional_units_needed'] > 20:
                critical_types.append((blood_type, data['additional_units_needed']))
        
        if critical_types:
            critical_types.sort(key=lambda x: x[1], reverse=True)
            recommendations.append(
                f"🚨 PRIORITY: Increase stock for {', '.join([bt[0] for bt in critical_types[:3]])}"
            )
        
        recommendations.append("📞 Activate emergency donor notification system")
        recommendations.append("🏥 Alert nearby hospitals of potential shortage")
        recommendations.append("🚚 Consider inter-facility blood transfer arrangements")
        
        return recommendations
