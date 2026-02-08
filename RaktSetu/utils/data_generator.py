"""
Data Generator
Generates realistic synthetic blood demand data for training and testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_historical_data(blood_type: str, days: int = 365) -> pd.DataFrame:
    """
    Generate realistic synthetic historical blood demand data
    
    Args:
        blood_type: Blood type to generate data for
        days: Number of historical days to generate
    
    Returns:
        DataFrame with columns: date, demand, day_of_week, month, is_weekend, etc.
    """
    
    # Base demand levels by blood type
    base_demands = {
        "O+": 40,
        "A+": 35,
        "B+": 25,
        "O-": 15,
        "A-": 12,
        "AB+": 10,
        "B-": 8,
        "AB-": 5
    }
    
    base_demand = base_demands.get(blood_type, 20)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    for date in date_range:
        # Base demand
        demand = base_demand
        
        # Day of week effect (higher on weekdays)
        if date.weekday() < 5:  # Monday to Friday
            demand *= random.uniform(1.1, 1.3)
        else:  # Weekend
            demand *= random.uniform(0.7, 0.9)
        
        # Monthly seasonal patterns
        month = date.month
        if month in [6, 7, 8]:  # Monsoon season - more accidents
            demand *= random.uniform(1.2, 1.4)
        elif month in [10, 11]:  # Festival season - increased activity
            demand *= random.uniform(1.15, 1.35)
        elif month in [12, 1, 2]:  # Winter - slightly lower
            demand *= random.uniform(0.9, 1.0)
        
        # Add some random events (accidents, emergencies)
        if random.random() < 0.05:  # 5% chance of spike
            demand *= random.uniform(1.5, 2.5)
        
        # General random variation
        demand *= random.uniform(0.85, 1.15)
        
        # Ensure positive integer
        demand = max(1, int(round(demand)))
        
        data.append({
            'date': date,
            'demand': demand,
            'day_of_week': date.weekday(),
            'month': date.month,
            'day': date.day,
            'is_weekend': 1 if date.weekday() >= 5 else 0,
            'is_monsoon': 1 if month in [6, 7, 8] else 0,
            'is_festival': 1 if month in [10, 11] else 0,
            'blood_type': blood_type
        })
    
    df = pd.DataFrame(data)
    return df


def generate_multi_location_data(locations: list, blood_types: list, days: int = 180) -> pd.DataFrame:
    """
    Generate data for multiple locations and blood types
    
    Args:
        locations: List of location names
        blood_types: List of blood types
        days: Number of days
    
    Returns:
        Combined DataFrame
    """
    all_data = []
    
    for location in locations:
        for blood_type in blood_types:
            df = generate_historical_data(blood_type, days)
            df['location'] = location
            
            # Location-specific multiplier
            if 'hospital' in location.lower():
                df['demand'] = (df['demand'] * 1.2).astype(int)
            elif 'rural' in location.lower():
                df['demand'] = (df['demand'] * 0.7).astype(int)
            
            all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df


def add_event_data(df: pd.DataFrame, events: list) -> pd.DataFrame:
    """
    Add specific events to the data (accidents, outbreaks, etc.)
    
    Args:
        df: DataFrame with historical data
        events: List of event dicts with 'date', 'type', 'impact'
    
    Returns:
        DataFrame with events incorporated
    """
    df = df.copy()
    
    for event in events:
        event_date = pd.to_datetime(event['date'])
        event_type = event['type']
        impact = event.get('impact', 1.5)
        
        # Find rows around event date
        mask = (df['date'] >= event_date - timedelta(days=1)) & \
               (df['date'] <= event_date + timedelta(days=2))
        
        # Apply impact
        if event_type == 'accident':
            # Increase O+, O- demand significantly
            df.loc[mask & df['blood_type'].isin(['O+', 'O-']), 'demand'] *= impact
        elif event_type == 'dengue':
            # Increase all blood types
            df.loc[mask, 'demand'] *= impact
        elif event_type == 'festival':
            # Moderate increase all types
            df.loc[mask, 'demand'] *= (impact * 0.8)
    
    return df


def generate_donor_data(num_donors: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic donor database
    
    Args:
        num_donors: Number of donors to generate
    
    Returns:
        DataFrame with donor information
    """
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    blood_type_distribution = [0.35, 0.06, 0.09, 0.02, 0.03, 0.01, 0.38, 0.06]
    
    donors = []
    
    for i in range(num_donors):
        # Generate donor
        blood_type = np.random.choice(blood_types, p=blood_type_distribution)
        
        last_donation = datetime.now() - timedelta(days=random.randint(0, 365))
        total_donations = random.randint(1, 20)
        
        # Determine donor status
        days_since_last = (datetime.now() - last_donation).days
        if days_since_last > 90:
            status = 'eligible'
        else:
            status = 'ineligible'
        
        donor = {
            'donor_id': f'D{i+1:05d}',
            'blood_type': blood_type,
            'last_donation_date': last_donation,
            'total_donations': total_donations,
            'status': status,
            'days_since_last_donation': days_since_last,
            'contact_preference': random.choice(['sms', 'email', 'app']),
            'location': random.choice(['north', 'south', 'east', 'west', 'central']),
            'reliability_score': random.uniform(0.5, 1.0)
        }
        
        donors.append(donor)
    
    df = pd.DataFrame(donors)
    return df


def generate_inventory_snapshot() -> pd.DataFrame:
    """
    Generate current inventory snapshot for all blood types
    
    Returns:
        DataFrame with current inventory levels
    """
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    inventory = []
    
    for blood_type in blood_types:
        # Base stock levels with some variation
        base_stocks = {
            "O+": 45, "A+": 38, "B+": 28, "O-": 12,
            "A-": 15, "AB+": 18, "B-": 10, "AB-": 6
        }
        
        stock = base_stocks.get(blood_type, 20)
        
        # Add some units with different expiry dates
        for i in range(random.randint(3, 8)):
            inventory.append({
                'blood_type': blood_type,
                'unit_id': f'{blood_type}-{random.randint(1000, 9999)}',
                'collection_date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'expiry_date': datetime.now() + timedelta(days=random.randint(5, 35)),
                'status': 'available',
                'location': 'main_bank'
            })
    
    df = pd.DataFrame(inventory)
    df['days_until_expiry'] = (df['expiry_date'] - datetime.now()).dt.days
    
    return df


# Example usage and testing
if __name__ == "__main__":
    print("Generating sample data...")
    
    # Generate historical demand data
    df = generate_historical_data("O+", days=365)
    print(f"\nGenerated {len(df)} days of historical data for O+")
    print(df.head())
    print(f"\nDemand statistics:")
    print(df['demand'].describe())
    
    # Generate donor database
    donors = generate_donor_data(500)
    print(f"\n\nGenerated {len(donors)} donor records")
    print(donors.head())
    
    # Generate inventory
    inventory = generate_inventory_snapshot()
    print(f"\n\nGenerated {len(inventory)} inventory units")
    print(inventory.groupby('blood_type').size())
