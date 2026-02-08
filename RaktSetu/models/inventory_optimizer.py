"""
Inventory Optimizer
Smart recommendations for blood stock management
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import random


class InventoryOptimizer:
    """
    AI-powered inventory optimization system
    
    Features:
    - Stock level optimization
    - Expiry management
    - Multi-location redistribution
    - Wastage reduction
    """
    
    def __init__(self):
        self.blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        # Simulated current inventory (in production, this comes from database)
        self.current_inventory = {
            "O+": 45,
            "A+": 38,
            "B+": 28,
            "O-": 12,  # Low stock
            "A-": 15,
            "AB+": 18,
            "B-": 10,
            "AB-": 6    # Very low
        }
        
        # Safety stock levels (minimum required)
        self.safety_stock = {
            "O+": 50,
            "A+": 40,
            "B+": 30,
            "O-": 25,  # Universal donor - higher safety stock
            "A-": 20,
            "AB+": 15,
            "B-": 12,
            "AB-": 10
        }
        
        # Optimal stock levels
        self.optimal_stock = {
            "O+": 80,
            "A+": 70,
            "B+": 50,
            "O-": 40,
            "A-": 35,
            "AB+": 25,
            "B-": 20,
            "AB-": 15
        }
        
        # Blood shelf life (days)
        self.shelf_life = 35
        
    def get_inventory_status(self, blood_type: str) -> Dict:
        """
        Get comprehensive inventory status with AI recommendations
        
        Returns:
            Status dict with current stock, predictions, and recommendations
        """
        current = self.current_inventory.get(blood_type, 0)
        safety = self.safety_stock.get(blood_type, 0)
        optimal = self.optimal_stock.get(blood_type, 0)
        
        # Calculate predicted demand (simplified - in production use the predictor)
        predicted_demand_7days = self._estimate_weekly_demand(blood_type)
        
        # Calculate days until shortage
        daily_demand = predicted_demand_7days / 7
        days_until_shortage = int(current / daily_demand) if daily_demand > 0 else None
        
        # Determine urgency level
        if current < safety * 0.5:
            urgency = "critical"
        elif current < safety:
            urgency = "high"
        elif current < optimal * 0.7:
            urgency = "medium"
        else:
            urgency = "low"
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            blood_type, current, safety, optimal, predicted_demand_7days
        )
        
        return {
            "blood_type": blood_type,
            "current_stock": current,
            "safety_stock": safety,
            "optimal_stock": optimal,
            "predicted_demand": predicted_demand_7days,
            "days_until_shortage": days_until_shortage,
            "recommendation": recommendation,
            "urgency_level": urgency,
            "stock_percentage": round((current / optimal) * 100, 1)
        }
    
    def _estimate_weekly_demand(self, blood_type: str) -> int:
        """Estimate 7-day demand (simplified version)"""
        base_demands = {
            "O+": 280,
            "A+": 245,
            "B+": 175,
            "O-": 105,
            "A-": 84,
            "AB+": 70,
            "B-": 56,
            "AB-": 35
        }
        
        base = base_demands.get(blood_type, 100)
        variation = random.uniform(0.9, 1.1)
        return int(base * variation)
    
    def _generate_recommendation(self, blood_type: str, current: int, 
                                  safety: int, optimal: int, predicted_demand: int) -> str:
        """Generate actionable recommendation"""
        if current < safety:
            units_needed = optimal - current
            return (f"🚨 URGENT: Stock {units_needed} units of {blood_type} immediately. "
                   f"Current stock below safety level.")
        
        elif current < optimal * 0.7:
            units_needed = optimal - current
            return (f"⚠️ RECOMMEND: Stock {units_needed} units of {blood_type} soon. "
                   f"Predicted demand: {predicted_demand} units/week.")
        
        elif current > optimal * 1.3:
            return (f"📊 OPTIMIZE: Consider redistributing excess {blood_type} stock "
                   f"to other locations or prioritize usage to prevent wastage.")
        
        else:
            return f"✅ GOOD: {blood_type} stock levels are optimal."
    
    def calculate_overall_health(self, statuses: List[Dict]) -> str:
        """Calculate overall inventory health score"""
        critical_count = len([s for s in statuses if s["urgency_level"] == "critical"])
        high_count = len([s for s in statuses if s["urgency_level"] == "high"])
        
        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "warning"
        elif high_count > 0:
            return "caution"
        else:
            return "healthy"
    
    def get_redistribution_suggestions(self) -> List[Dict]:
        """
        Generate smart redistribution suggestions between locations
        
        Simulates multi-location optimization
        """
        suggestions = []
        
        # Simulated other locations inventory
        locations = {
            "Main Blood Bank": self.current_inventory,
            "City Hospital Blood Bank": {
                "O+": 25, "A+": 20, "B+": 55, "O-": 30,
                "A-": 25, "AB+": 8, "B-": 15, "AB-": 12
            },
            "Regional Medical Center": {
                "O+": 65, "A+": 55, "B+": 15, "O-": 8,
                "A-": 10, "AB+": 22, "B-": 18, "AB-": 5
            }
        }
        
        for blood_type in self.blood_types:
            # Find locations with excess and shortage
            excess_locations = []
            shortage_locations = []
            
            for location, inventory in locations.items():
                current = inventory.get(blood_type, 0)
                optimal = self.optimal_stock.get(blood_type, 0)
                safety = self.safety_stock.get(blood_type, 0)
                
                if current > optimal * 1.2:
                    excess_locations.append({
                        "location": location,
                        "excess": current - optimal
                    })
                elif current < safety:
                    shortage_locations.append({
                        "location": location,
                        "shortage": safety - current
                    })
            
            # Generate transfer suggestions
            for shortage in shortage_locations:
                for excess in excess_locations:
                    if excess["excess"] > 0:
                        transfer_amount = min(shortage["shortage"], excess["excess"])
                        
                        if transfer_amount >= 5:  # Only suggest if meaningful
                            suggestions.append({
                                "blood_type": blood_type,
                                "from_location": excess["location"],
                                "to_location": shortage["location"],
                                "units": transfer_amount,
                                "priority": "high" if shortage["shortage"] > safety * 0.5 else "medium",
                                "reason": f"Balance stock levels - {shortage['location']} below safety threshold"
                            })
                            
                            # Update for next iteration
                            excess["excess"] -= transfer_amount
                            shortage["shortage"] -= transfer_amount
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: (priority_order[x["priority"]], -x["units"]))
        
        return suggestions
    
    def calculate_waste_reduction(self, suggestions: List[Dict]) -> Dict:
        """Calculate potential waste reduction from redistribution"""
        total_units = sum([s["units"] for s in suggestions])
        
        # Estimate waste prevention (simplified)
        waste_prevented = int(total_units * 0.7)  # Assume 70% would have expired
        cost_per_unit = 50  # dollars
        cost_savings = waste_prevented * cost_per_unit
        
        return {
            "units_redistributed": total_units,
            "waste_units_prevented": waste_prevented,
            "estimated_cost_savings": cost_savings,
            "percentage_waste_reduction": round((waste_prevented / max(total_units, 1)) * 100, 1)
        }
    
    def get_expiry_alerts(self) -> List[Dict]:
        """
        Get alerts for blood units nearing expiry
        
        Simulates expiry tracking
        """
        alerts = []
        
        # Simulated expiry data
        for blood_type in self.blood_types:
            # Random units nearing expiry
            if random.random() > 0.6:
                units_expiring = random.randint(3, 15)
                days_until_expiry = random.randint(1, 7)
                
                urgency = "critical" if days_until_expiry <= 2 else "high" if days_until_expiry <= 5 else "medium"
                
                alerts.append({
                    "blood_type": blood_type,
                    "units": units_expiring,
                    "days_until_expiry": days_until_expiry,
                    "urgency": urgency,
                    "recommendation": self._get_expiry_recommendation(blood_type, units_expiring, days_until_expiry)
                })
        
        return sorted(alerts, key=lambda x: x["days_until_expiry"])
    
    def _get_expiry_recommendation(self, blood_type: str, units: int, days: int) -> str:
        """Generate recommendation for expiring blood"""
        if days <= 2:
            return (f"🚨 URGENT: {units} units of {blood_type} expiring in {days} day(s). "
                   f"Contact high-demand hospitals immediately or mark for platelet extraction.")
        elif days <= 5:
            return (f"⚠️ PRIORITY: {units} units of {blood_type} expiring in {days} days. "
                   f"Prioritize for scheduled surgeries or transfer to high-use facility.")
        else:
            return (f"📋 PLAN: {units} units of {blood_type} expiring in {days} days. "
                   f"Monitor usage patterns and consider redistribution if needed.")
    
    def optimize_collection_schedule(self, blood_type: str) -> Dict:
        """
        Optimize blood collection drives based on predicted demand
        
        Returns recommended collection schedule
        """
        current = self.current_inventory.get(blood_type, 0)
        optimal = self.optimal_stock.get(blood_type, 0)
        predicted_weekly = self._estimate_weekly_demand(blood_type)
        
        deficit = max(0, optimal - current)
        weekly_deficit = max(0, predicted_weekly - current)
        
        # Determine collection urgency
        if current < self.safety_stock.get(blood_type, 0):
            schedule = "immediate"
            target_donors = int(deficit / 0.8)  # Assume 80% success rate
            days_to_organize = 1
        elif deficit > predicted_weekly:
            schedule = "this_week"
            target_donors = int(deficit / 0.8)
            days_to_organize = 3
        else:
            schedule = "next_week"
            target_donors = int(weekly_deficit / 0.8)
            days_to_organize = 7
        
        return {
            "blood_type": blood_type,
            "schedule": schedule,
            "target_donors": target_donors,
            "target_units": deficit if deficit > 0 else predicted_weekly,
            "recommended_date": (datetime.now() + timedelta(days=days_to_organize)).strftime("%Y-%m-%d"),
            "priority": "high" if schedule == "immediate" else "medium" if schedule == "this_week" else "low"
        }
