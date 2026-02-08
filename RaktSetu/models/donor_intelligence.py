"""
Advanced Donor Intelligence & Analytics System
Donor segmentation, retention analysis, and engagement optimization
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np


class DonorIntelligence:
    """
    Advanced analytics for donor management
    
    Features:
    - Donor segmentation
    - Retention analysis
    - Engagement scoring
    - Drop-off prediction
    - Geographic heatmaps
    """
    
    def __init__(self):
        self.blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        # Simulated donor database (in production, this comes from DB)
        self.donors = self._generate_donor_database()
    
    def _generate_donor_database(self, num_donors: int = 500) -> pd.DataFrame:
        """Generate simulated donor data"""
        donors = []
        
        blood_type_dist = {
            "O+": 0.38, "A+": 0.34, "B+": 0.09, "AB+": 0.03,
            "O-": 0.07, "A-": 0.06, "B-": 0.02, "AB-": 0.01
        }
        
        locations = ["north", "south", "east", "west", "central"]
        
        for i in range(num_donors):
            # Random blood type based on distribution
            blood_type = np.random.choice(
                list(blood_type_dist.keys()),
                p=list(blood_type_dist.values())
            )
            
            last_donation = datetime.now() - timedelta(days=random.randint(0, 730))
            total_donations = random.randint(1, 25)
            
            days_since_last = (datetime.now() - last_donation).days
            
            donors.append({
                "donor_id": f"D{i+1:05d}",
                "blood_type": blood_type,
                "age": random.randint(18, 65),
                "gender": random.choice(["M", "F", "O"]),
                "location": random.choice(locations),
                "total_donations": total_donations,
                "last_donation_date": last_donation,
                "days_since_last_donation": days_since_last,
                "eligible": days_since_last >= 90,
                "contact_preference": random.choice(["sms", "email", "app", "whatsapp"]),
                "reliability_score": random.uniform(0.5, 1.0),
                "emergency_available": random.choice([True, False]),
                "donated_in_last_year": days_since_last <= 365
            })
        
        return pd.DataFrame(donors)
    
    def segment_donors(self) -> Dict[str, List[Dict]]:
        """
        Segment donors into strategic groups
        
        Segments:
        - Champions: High frequency, recent donors
        - Regular: Consistent donors
        - At-Risk: Haven't donated recently
        - Lost: Inactive for >2 years
        - Rare Blood: Rare blood type donors
        - Emergency Ready: Available for emergencies
        """
        segments = {
            "champions": [],
            "regular": [],
            "at_risk": [],
            "lost": [],
            "rare_blood": [],
            "emergency_ready": []
        }
        
        for _, donor in self.donors.iterrows():
            donor_dict = donor.to_dict()
            
            # Champions: 5+ donations, donated in last 6 months
            if donor["total_donations"] >= 5 and donor["days_since_last_donation"] <= 180:
                segments["champions"].append(donor_dict)
            
            # Regular: 2+ donations, donated in last year
            elif donor["total_donations"] >= 2 and donor["donated_in_last_year"]:
                segments["regular"].append(donor_dict)
            
            # At-Risk: Donated before but not in last year
            elif donor["total_donations"] >= 2 and not donor["donated_in_last_year"]:
                segments["at_risk"].append(donor_dict)
            
            # Lost: No donation in 2+ years
            elif donor["days_since_last_donation"] > 730:
                segments["lost"].append(donor_dict)
            
            # Rare blood types
            if donor["blood_type"] in ["AB-", "B-", "AB+", "O-"]:
                segments["rare_blood"].append(donor_dict)
            
            # Emergency ready
            if donor["emergency_available"] and donor["eligible"]:
                segments["emergency_ready"].append(donor_dict)
        
        return segments
    
    def get_donor_retention_rate(self) -> Dict:
        """Calculate donor retention metrics"""
        total_donors = len(self.donors)
        active_donors = len(self.donors[self.donors["donated_in_last_year"]])
        
        # Donors who donated in last year vs previous year
        last_year = self.donors["donated_in_last_year"].sum()
        
        retention_rate = (active_donors / total_donors) * 100
        
        return {
            "total_donors": total_donors,
            "active_donors": active_donors,
            "inactive_donors": total_donors - active_donors,
            "retention_rate": round(retention_rate, 2),
            "average_donations_per_donor": round(self.donors["total_donations"].mean(), 2),
            "eligible_donors": len(self.donors[self.donors["eligible"]]),
            "emergency_ready_donors": len(self.donors[self.donors["emergency_available"] & self.donors["eligible"]])
        }
    
    def analyze_drop_off(self) -> Dict:
        """
        Analyze why donors stop donating
        
        Identifies patterns in donor churn
        """
        # Donors who donated before but stopped
        dropped_off = self.donors[
            (self.donors["total_donations"] >= 2) & 
            (self.donors["days_since_last_donation"] > 365)
        ]
        
        # Analyze patterns
        avg_donations_before_dropout = dropped_off["total_donations"].mean()
        avg_days_inactive = dropped_off["days_since_last_donation"].mean()
        
        # Age analysis
        age_groups = {
            "18-25": len(dropped_off[dropped_off["age"] <= 25]),
            "26-35": len(dropped_off[(dropped_off["age"] > 25) & (dropped_off["age"] <= 35)]),
            "36-50": len(dropped_off[(dropped_off["age"] > 35) & (dropped_off["age"] <= 50)]),
            "51+": len(dropped_off[dropped_off["age"] > 50])
        }
        
        return {
            "total_dropped_donors": len(dropped_off),
            "average_donations_before_dropout": round(avg_donations_before_dropout, 2),
            "average_days_inactive": int(avg_days_inactive),
            "dropout_by_age_group": age_groups,
            "recommendations": self._get_retention_recommendations(dropped_off)
        }
    
    def _get_retention_recommendations(self, dropped_donors: pd.DataFrame) -> List[str]:
        """Generate recommendations to improve retention"""
        recommendations = []
        
        if len(dropped_donors) > 0:
            # Check if many young donors dropped
            young_dropout = len(dropped_donors[dropped_donors["age"] <= 30])
            if young_dropout / len(dropped_donors) > 0.4:
                recommendations.append("📱 Target younger demographics with mobile app and social media engagement")
            
            # Check average donations before dropout
            avg_donations = dropped_donors["total_donations"].mean()
            if avg_donations < 5:
                recommendations.append("🎁 Implement first-time donor retention program with incentives")
            
            recommendations.append("📧 Launch re-engagement campaign for inactive donors")
            recommendations.append("🏆 Create loyalty program for donors with 5+ donations")
            recommendations.append("📊 Survey dropped donors to understand pain points")
        
        return recommendations
    
    def get_blood_type_scarcity_index(self) -> Dict:
        """
        Calculate scarcity index for each blood type
        
        Based on:
        - Number of available donors
        - Population distribution
        - Recent donation rates
        """
        scarcity_scores = {}
        
        for blood_type in self.blood_types:
            donors_of_type = self.donors[self.donors["blood_type"] == blood_type]
            eligible_donors = donors_of_type[donors_of_type["eligible"]]
            
            # Calculate scarcity (lower donors = higher scarcity)
            total_count = len(donors_of_type)
            eligible_count = len(eligible_donors)
            
            # Scarcity score (0-100, higher = more scarce)
            if total_count > 0:
                scarcity = 100 - (eligible_count / max(total_count, 1) * 100)
            else:
                scarcity = 100
            
            scarcity_scores[blood_type] = {
                "total_donors": total_count,
                "eligible_donors": eligible_count,
                "scarcity_score": round(scarcity, 2),
                "urgency": "critical" if scarcity > 75 else "high" if scarcity > 50 else "medium" if scarcity > 25 else "low"
            }
        
        return scarcity_scores
    
    def get_geographic_heatmap(self) -> Dict:
        """
        Generate geographic distribution of donors
        
        Shows donor density by location
        """
        location_stats = {}
        
        for location in self.donors["location"].unique():
            location_donors = self.donors[self.donors["location"] == location]
            eligible = location_donors[location_donors["eligible"]]
            
            location_stats[location] = {
                "total_donors": len(location_donors),
                "eligible_donors": len(eligible),
                "average_donations": round(location_donors["total_donations"].mean(), 2),
                "emergency_ready": len(location_donors[location_donors["emergency_available"]]),
                "blood_type_distribution": location_donors["blood_type"].value_counts().to_dict()
            }
        
        return location_stats
    
    def get_donor_reliability_scores(self, top_n: int = 50) -> List[Dict]:
        """
        Get top reliable donors
        
        Based on:
        - Donation frequency
        - Consistency
        - Response to emergency calls
        """
        # Calculate reliability score
        self.donors["composite_score"] = (
            self.donors["total_donations"] * 0.4 +
            self.donors["reliability_score"] * 100 * 0.3 +
            (100 - self.donors["days_since_last_donation"].clip(0, 365) / 3.65) * 0.3
        )
        
        top_donors = self.donors.nlargest(top_n, "composite_score")
        
        return [
            {
                "donor_id": row["donor_id"],
                "blood_type": row["blood_type"],
                "total_donations": row["total_donations"],
                "reliability_score": round(row["reliability_score"], 2),
                "composite_score": round(row["composite_score"], 2),
                "eligible": row["eligible"],
                "location": row["location"]
            }
            for _, row in top_donors.iterrows()
        ]
    
    def get_targeted_donor_list(self, blood_type: str, max_donors: int = 20, 
                                emergency: bool = False) -> List[Dict]:
        """
        Get targeted list of donors to contact
        
        Args:
            blood_type: Blood type needed
            max_donors: Maximum number of donors to return
            emergency: If True, only return emergency-ready donors
        
        Returns:
            List of donors to contact, sorted by priority
        """
        # Filter by blood type and eligibility
        candidates = self.donors[
            (self.donors["blood_type"] == blood_type) &
            (self.donors["eligible"])
        ]
        
        if emergency:
            candidates = candidates[candidates["emergency_available"]]
        
        # Sort by reliability and recency
        candidates = candidates.sort_values(
            by=["reliability_score", "total_donations"],
            ascending=[False, False]
        )
        
        top_candidates = candidates.head(max_donors)
        
        return [
            {
                "donor_id": row["donor_id"],
                "blood_type": row["blood_type"],
                "contact_preference": row["contact_preference"],
                "total_donations": row["total_donations"],
                "days_since_last_donation": row["days_since_last_donation"],
                "reliability_score": round(row["reliability_score"], 2),
                "location": row["location"],
                "emergency_available": row["emergency_available"]
            }
            for _, row in top_candidates.iterrows()
        ]
    
    def get_donation_trends(self) -> Dict:
        """Analyze donation trends over time"""
        # Simulated trend analysis
        return {
            "weekly_average": round(self.donors["total_donations"].sum() / 52, 2),
            "monthly_average": round(self.donors["total_donations"].sum() / 12, 2),
            "peak_donation_months": ["January", "October", "November"],  # Post-holidays, festivals
            "low_donation_months": ["June", "July", "August"],  # Summer
            "trend": "increasing" if random.random() > 0.5 else "stable"
        }
