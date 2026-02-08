"""
BloodFlow AI - API Testing Script
Quick tests for the FastAPI endpoints
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the root endpoint"""
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_prediction():
    """Test blood demand prediction"""
    print("\n2. Testing Blood Demand Prediction...")
    
    payload = {
        "blood_type": "O+",
        "days_ahead": 7,
        "location": "main_bank"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/predict", json=payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Blood Type: {data['blood_type']}")
        print(f"   Predictions: {len(data['predictions'])} days")
        print(f"   First prediction: {data['predictions'][0]}")
        print(f"   Alerts: {len(data['alerts'])}")
        print(f"   Confidence: {data['confidence_score']:.1f}%")
    else:
        print(f"   Error: {response.text}")
    
    return response.status_code == 200


def test_inventory_status():
    """Test inventory status endpoint"""
    print("\n3. Testing Inventory Status...")
    
    response = requests.get(f"{BASE_URL}/api/v1/inventory/status")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total blood types: {len(data['inventory_status'])}")
        print(f"   Critical items: {data['critical_count']}")
        print(f"   Overall health: {data['overall_health']}")
        
        # Show one example
        if data['inventory_status']:
            example = data['inventory_status'][0]
            print(f"\n   Example - {example['blood_type']}:")
            print(f"     Current stock: {example['current_stock']}")
            print(f"     Urgency: {example['urgency_level']}")
    else:
        print(f"   Error: {response.text}")
    
    return response.status_code == 200


def test_alerts():
    """Test alerts endpoint"""
    print("\n4. Testing Alerts System...")
    
    response = requests.get(f"{BASE_URL}/api/v1/alerts")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total alerts: {data['total_alerts']}")
        
        # Group by urgency
        if data['alerts']:
            urgencies = {}
            for alert in data['alerts']:
                urgency = alert['urgency']
                urgencies[urgency] = urgencies.get(urgency, 0) + 1
            
            print(f"   By urgency: {urgencies}")
    else:
        print(f"   Error: {response.text}")
    
    return response.status_code == 200


def test_simulation():
    """Test scenario simulation"""
    print("\n5. Testing Emergency Simulation...")
    
    params = {
        "scenario": "highway_accident",
        "severity": "high"
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/simulation", params=params)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Scenario: {data['scenario']}")
        print(f"   Severity: {data['severity']}")
        print(f"   Blood types analyzed: {len(data['results'])}")
        print(f"   Recommendations: {len(data['recommendations'])}")
        
        # Show O+ impact
        if 'O+' in data['results']:
            o_plus = data['results']['O+']
            print(f"\n   O+ Impact:")
            print(f"     Baseline: {o_plus['baseline_demand']} units")
            print(f"     Surge: {o_plus['surge_demand']} units")
            print(f"     Increase: +{o_plus['percentage_increase']}%")
    else:
        print(f"   Error: {response.text}")
    
    return response.status_code == 200


def test_redistribution():
    """Test redistribution suggestions"""
    print("\n6. Testing Redistribution Optimizer...")
    
    response = requests.get(f"{BASE_URL}/api/v1/optimization/redistribute")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Suggestions: {len(data['suggestions'])}")
        
        if data['suggestions']:
            print(f"\n   Top suggestion:")
            top = data['suggestions'][0]
            print(f"     {top['blood_type']}: {top['from_location']} → {top['to_location']}")
            print(f"     Units: {top['units']}")
            print(f"     Priority: {top['priority']}")
        
        print(f"\n   Waste reduction:")
        wr = data['potential_waste_reduction']
        print(f"     Units saved: {wr['waste_units_prevented']}")
        print(f"     Cost savings: ${wr['estimated_cost_savings']}")
    else:
        print(f"   Error: {response.text}")
    
    return response.status_code == 200


def test_training():
    """Test model training endpoint"""
    print("\n7. Testing Model Training...")
    
    payload = {
        "blood_type": "O+",
        "retrain": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/train", json=payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Training status: {data['status']}")
        
        if 'training_metrics' in data:
            metrics = data['training_metrics']
            print(f"   MAE: {metrics['mae']:.2f}")
            print(f"   RMSE: {metrics['rmse']:.2f}")
            print(f"   R² Score: {metrics['r2_score']:.3f}")
    else:
        print(f"   Error: {response.text}")
    
    return response.status_code == 200


def run_all_tests():
    """Run all API tests"""
    print("=" * 70)
    print("  BLOODFLOW AI - API TEST SUITE")
    print("=" * 70)
    print(f"\n  Testing API at: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Prediction", test_prediction),
        ("Inventory Status", test_inventory_status),
        ("Alerts", test_alerts),
        ("Simulation", test_simulation),
        ("Redistribution", test_redistribution),
        ("Training", test_training)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except requests.exceptions.ConnectionError:
            print(f"\n   ❌ ERROR: Cannot connect to API at {BASE_URL}")
            print("   Make sure the server is running: python main.py")
            return
        except Exception as e:
            print(f"\n   ❌ ERROR: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST RESULTS SUMMARY")
    print("=" * 70 + "\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}  {name}")
    
    print(f"\n  Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n  🎉 All tests passed! API is working correctly.")
    else:
        print("\n  ⚠️  Some tests failed. Check the errors above.")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    print("\n⚠️  NOTE: Make sure the API server is running!")
    print("   Start it with: python main.py\n")
    
    input("Press Enter to start testing...")
    
    run_all_tests()
