"""
BloodFlow AI - Database Setup Script
Initializes database and loads data
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import init_database, populate_initial_data, get_session
from database.kaggle_loader import KaggleDataLoader

def setup_database():
    """
    Complete database setup
    
    Steps:
    1. Create database and tables
    2. Populate initial configuration
    3. Load donor data (Kaggle or synthetic)
    4. Generate demand history
    5. Update inventory
    """
    
    print("\n" + "="*70)
    print("  🩸 BLOODFLOW AI - DATABASE SETUP")
    print("="*70 + "\n")
    
    # Step 1: Create database
    print("Step 1: Creating database and tables...")
    engine = init_database()
    session = get_session(engine)
    
    # Step 2: Initial configuration
    print("\nStep 2: Adding initial configuration...")
    populate_initial_data(session)
    session.close()
    
    # Step 3-5: Load all data
    print("\nStep 3-5: Loading data...")
    loader = KaggleDataLoader()
    
    # You can specify a Kaggle CSV here if you have one
    # Example: kaggle_csv = "transfusion.csv"
    kaggle_csv = None
    
    loader.import_all_data(kaggle_csv)
    
    print("\n" + "="*70)
    print("  ✅ DATABASE SETUP COMPLETE!")
    print("="*70)
    
    print("\n📝 Next Steps:")
    print("  1. Start the backend: python main.py")
    print("  2. Start the frontend: streamlit run app.py")
    print("  3. Open browser: http://localhost:8501\n")


if __name__ == "__main__":
    setup_database()
