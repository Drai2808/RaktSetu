"""
Kaggle Dataset Loader
Downloads and imports blood donation datasets from Kaggle
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (
    Donor, Donation, BloodInventory, DemandHistory, 
    BloodUnit, init_database, get_session
)


class KaggleDataLoader:
    """
    Load blood donation data from Kaggle datasets or CSV files
    
    Supports:
    1. Blood Transfusion Service Center Dataset
    2. Custom blood donation CSVs
    3. Synthetic data generation (if no Kaggle data available)
    """
    
    def __init__(self, db_path="sqlite:///bloodflow.db"):
        self.engine = init_database(db_path)
        self.Session = sessionmaker(bind=self.engine)
    
    def load_from_csv(self, csv_path: str):
        """
        Load data from CSV file
        
        Expected columns:
        - donor_id, blood_type, age, gender, location, donation_date
        """
        print(f"Loading data from {csv_path}...")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"✓ Loaded {len(df)} records from CSV")
            return df
        except FileNotFoundError:
            print(f"❌ File not found: {csv_path}")
            return None
        except Exception as e:
            print(f"❌ Error loading CSV: {str(e)}")
            return None
    
    def load_blood_transfusion_dataset(self, csv_path="transfusion.csv"):
        """
        Load Blood Transfusion Service Center Dataset from Kaggle
        
        Dataset: https://www.kaggle.com/datasets/whenamancodes/blood-transfusion-dataset
        
        Columns: Recency, Frequency, Monetary, Time, whether donated
        """
        print("Loading Blood Transfusion Dataset...")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Map to our schema
            # Recency = months since last donation
            # Frequency = total donations
            # Time = months since first donation
            
            donors = []
            blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
            blood_type_probs = [0.38, 0.34, 0.09, 0.03, 0.07, 0.06, 0.02, 0.01]
            
            for idx, row in df.iterrows():
                donor_data = {
                    'donor_id': f'D{idx+1:05d}',
                    'blood_type': np.random.choice(blood_types, p=blood_type_probs),
                    'age': random.randint(18, 65),
                    'gender': random.choice(['M', 'F']),
                    'location': random.choice(['north', 'south', 'east', 'west', 'central']),
                    'recency_months': row.get('Recency (months)', row.iloc[0] if len(row) > 0 else 6),
                    'total_donations': row.get('Frequency (times)', row.iloc[1] if len(row) > 1 else 5),
                    'months_active': row.get('Time (months)', row.iloc[3] if len(row) > 3 else 24)
                }
                donors.append(donor_data)
            
            print(f"✓ Processed {len(donors)} donor records")
            return pd.DataFrame(donors)
            
        except FileNotFoundError:
            print(f"⚠️  Kaggle dataset not found at {csv_path}")
            print("   Generating synthetic data instead...")
            return self.generate_synthetic_data()
        except Exception as e:
            print(f"⚠️  Error loading Kaggle data: {str(e)}")
            print("   Generating synthetic data instead...")
            return self.generate_synthetic_data()
    
    def generate_synthetic_data(self, num_donors=500, num_days_history=365):
        """
        Generate realistic synthetic blood donation data
        (Used when Kaggle data is not available)
        """
        print(f"Generating synthetic data: {num_donors} donors, {num_days_history} days history...")
        
        blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
        blood_type_probs = [0.38, 0.34, 0.09, 0.03, 0.07, 0.06, 0.02, 0.01]
        locations = ['north', 'south', 'east', 'west', 'central']
        
        donors_data = []
        
        for i in range(num_donors):
            blood_type = np.random.choice(blood_types, p=blood_type_probs)
            total_donations = random.randint(1, 25)
            recency_months = random.randint(0, 24)
            
            donor = {
                'donor_id': f'D{i+1:05d}',
                'blood_type': blood_type,
                'age': random.randint(18, 65),
                'gender': random.choice(['M', 'F', 'O']),
                'location': random.choice(locations),
                'contact_preference': random.choice(['sms', 'email', 'app', 'whatsapp']),
                'emergency_available': random.choice([True, False]),
                'recency_months': recency_months,
                'total_donations': total_donations,
                'months_active': random.randint(recency_months, 60)
            }
            donors_data.append(donor)
        
        print(f"✓ Generated {len(donors_data)} synthetic donor records")
        return pd.DataFrame(donors_data)
    
    def import_donors_to_db(self, df):
        """Import donor data to database"""
        session = self.Session()
        
        try:
            print("Importing donors to database...")
            
            # Clear existing donors (for fresh import)
            session.query(Donor).delete()
            session.query(Donation).delete()
            session.commit()
            
            donors_added = 0
            donations_added = 0
            
            for _, row in df.iterrows():
                # Create donor
                donor = Donor(
                    donor_id=row['donor_id'],
                    blood_type=row['blood_type'],
                    age=row.get('age', 30),
                    gender=row.get('gender', 'M'),
                    location=row.get('location', 'central'),
                    contact_preference=row.get('contact_preference', 'email'),
                    emergency_available=row.get('emergency_available', False)
                )
                session.add(donor)
                session.flush()  # Get the donor ID
                
                donors_added += 1
                
                # Create donation history
                total_donations = int(row.get('total_donations', 5))
                recency_months = int(row.get('recency_months', 3))
                
                for i in range(total_donations):
                    # Calculate donation date
                    months_ago = recency_months + (i * 4)  # Every ~4 months
                    donation_date = datetime.now() - timedelta(days=months_ago * 30)
                    
                    donation = Donation(
                        donor_id=donor.id,
                        donation_date=donation_date,
                        blood_type=row['blood_type'],
                        volume_ml=450,
                        location=row.get('location', 'Main Blood Bank')
                    )
                    session.add(donation)
                    donations_added += 1
            
            session.commit()
            print(f"✓ Imported {donors_added} donors")
            print(f"✓ Imported {donations_added} donation records")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error importing donors: {str(e)}")
        finally:
            session.close()
    
    def generate_demand_history(self, days=365):
        """Generate historical demand data for ML training"""
        session = self.Session()
        
        try:
            print(f"Generating {days} days of demand history...")
            
            # Clear existing history
            session.query(DemandHistory).delete()
            session.commit()
            
            blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
            base_demands = {
                "O+": 40, "A+": 35, "B+": 25, "O-": 15,
                "A-": 12, "AB+": 10, "B-": 8, "AB-": 5
            }
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            records_added = 0
            
            for blood_type in blood_types:
                base_demand = base_demands[blood_type]
                current_date = start_date
                
                while current_date <= end_date:
                    # Calculate demand with variations
                    demand = base_demand
                    
                    # Day of week effect
                    if current_date.weekday() < 5:  # Weekday
                        demand *= random.uniform(1.1, 1.3)
                    else:  # Weekend
                        demand *= random.uniform(0.7, 0.9)
                    
                    # Monthly seasonal effect
                    month = current_date.month
                    if month in [6, 7, 8]:  # Monsoon
                        demand *= random.uniform(1.2, 1.4)
                    elif month in [10, 11]:  # Festival season
                        demand *= random.uniform(1.15, 1.35)
                    
                    # Random events (5% chance of spike)
                    if random.random() < 0.05:
                        demand *= random.uniform(1.5, 2.5)
                    
                    # General variation
                    demand *= random.uniform(0.85, 1.15)
                    demand = max(1, int(round(demand)))
                    
                    # Create record
                    record = DemandHistory(
                        date=current_date,
                        blood_type=blood_type,
                        demand=demand,
                        actual_usage=int(demand * random.uniform(0.8, 1.0)),
                        day_of_week=current_date.weekday(),
                        month=current_date.month,
                        is_weekend=current_date.weekday() >= 5,
                        is_holiday=False
                    )
                    session.add(record)
                    records_added += 1
                    
                    current_date += timedelta(days=1)
            
            session.commit()
            print(f"✓ Generated {records_added} demand history records")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error generating demand history: {str(e)}")
        finally:
            session.close()
    
    def update_inventory_from_donations(self):
        """Update current inventory based on recent donations"""
        session = self.Session()
        
        try:
            print("Updating inventory from donations...")
            
            blood_types = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
            
            for blood_type in blood_types:
                # Count recent donations (last 30 days)
                thirty_days_ago = datetime.now() - timedelta(days=30)
                
                recent_donations = session.query(Donation).filter(
                    Donation.blood_type == blood_type,
                    Donation.donation_date >= thirty_days_ago
                ).count()
                
                # Update inventory
                inventory = session.query(BloodInventory).filter(
                    BloodInventory.blood_type == blood_type
                ).first()
                
                if inventory:
                    # Simulate current stock (recent donations - usage)
                    usage_rate = 0.7  # 70% of donations are used
                    inventory.current_stock = int(recent_donations * (1 - usage_rate))
                    inventory.last_updated = datetime.now()
            
            session.commit()
            print("✓ Inventory updated")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error updating inventory: {str(e)}")
        finally:
            session.close()
    
    def import_all_data(self, kaggle_csv_path=None):
        """
        Complete data import process
        
        Steps:
        1. Load donor data (from Kaggle or generate synthetic)
        2. Import donors to database
        3. Generate demand history
        4. Update inventory
        """
        print("\n" + "="*60)
        print("BLOODFLOW AI - DATA IMPORT")
        print("="*60 + "\n")
        
        # Step 1: Load donor data
        if kaggle_csv_path:
            df = self.load_from_csv(kaggle_csv_path)
            if df is None:
                df = self.generate_synthetic_data()
        else:
            # Try to load standard Kaggle dataset
            df = self.load_blood_transfusion_dataset()
        
        # Step 2: Import donors
        self.import_donors_to_db(df)
        
        # Step 3: Generate demand history
        self.generate_demand_history(days=365)
        
        # Step 4: Update inventory
        self.update_inventory_from_donations()
        
        print("\n" + "="*60)
        print("✅ DATA IMPORT COMPLETE!")
        print("="*60)
        print("\n📊 Database Summary:")
        
        session = self.Session()
        print(f"   Donors: {session.query(Donor).count()}")
        print(f"   Donations: {session.query(Donation).count()}")
        print(f"   Demand Records: {session.query(DemandHistory).count()}")
        print(f"   Inventory Items: {session.query(BloodInventory).count()}")
        session.close()
        
        print("\n🚀 Ready to start the application!")
        print("   Run: python main.py\n")


if __name__ == "__main__":
    # Run data import
    loader = KaggleDataLoader()
    
    # You can specify a Kaggle CSV path here, or leave None for synthetic data
    kaggle_csv = None  # e.g., "transfusion.csv" or "blood_donation.csv"
    
    loader.import_all_data(kaggle_csv)
