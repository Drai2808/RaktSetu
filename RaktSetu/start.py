"""
BloodFlow AI - One-Click Launcher
Just run this file to start everything!
"""

import subprocess
import sys
import time
import webbrowser
import os

def main():
    print("\n" + "="*70)
    print("  🩸 BLOODFLOW AI - ONE-CLICK LAUNCHER")
    print("="*70 + "\n")
    
    print("📦 Checking dependencies...")
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✓ Streamlit found")
    except ImportError:
        print("⚠️  Installing Streamlit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly"])
    
    # Check if sqlalchemy is installed
    try:
        import sqlalchemy
        print("✓ SQLAlchemy found")
    except ImportError:
        print("⚠️  Installing SQLAlchemy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy"])
    
    print("\n🚀 Starting BloodFlow AI...")
    print("   This will:")
    print("   1. Initialize database (if needed)")
    print("   2. Start backend API")
    print("   3. Start frontend dashboard")
    print("   4. Open browser automatically\n")
    
    time.sleep(2)
    
    # Just run main.py - it handles everything now!
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")
        print("  Thank you for using BloodFlow AI! 🩸\n")


if __name__ == "__main__":
    main()
