# BloodFlow AI - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the API Server
```bash
python main.py
```

The server will start at: **http://localhost:8000**

### Step 3: Test the API

**Option A - View Interactive Docs:**
Open your browser: http://localhost:8000/docs

**Option B - Run Demo Script:**
```bash
python test_demo.py
```

**Option C - Test with cURL:**
```bash
# Predict blood demand
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"blood_type": "O+", "days_ahead": 7}'

# Get inventory status
curl "http://localhost:8000/api/v1/inventory/status"

# Run emergency simulation
curl "http://localhost:8000/api/v1/simulation?scenario=highway_accident&severity=high"
```

## 📋 Project Structure

```
bloodflow-ai/
├── main.py                    # FastAPI application (START HERE)
├── requirements.txt           # Dependencies
├── README.md                  # Full documentation
├── test_demo.py              # Interactive demo
├── test_api.py               # API tests
├── models/
│   ├── demand_predictor.py   # AI prediction model
│   └── inventory_optimizer.py # Inventory optimization
└── utils/
    └── data_generator.py      # Synthetic data generation
```

## 🎯 Key Features to Demo

1. **AI Prediction**: `/api/v1/predict` - Forecasts blood demand 7-30 days ahead
2. **Inventory Status**: `/api/v1/inventory/status` - Real-time stock monitoring
3. **Smart Alerts**: `/api/v1/alerts` - Intelligent shortage warnings
4. **What-If Scenarios**: `/api/v1/simulation` - Emergency planning
5. **Redistribution**: `/api/v1/optimization/redistribute` - Multi-location optimization
6. **Model Training**: `/api/v1/train` - ML model retraining

## 💡 Example API Calls

### Python
```python
import requests

# Predict demand
response = requests.post("http://localhost:8000/api/v1/predict",
    json={"blood_type": "O+", "days_ahead": 7})
print(response.json())
```

### JavaScript
```javascript
fetch('http://localhost:8000/api/v1/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({blood_type: "O+", days_ahead: 7})
})
.then(r => r.json())
.then(data => console.log(data));
```

## 🎓 For Hackathon Demo

1. Start with **test_demo.py** to see all features
2. Show **interactive docs** at /docs
3. Demonstrate **prediction accuracy** and **alerts**
4. Run **emergency scenarios** (highway accident, dengue outbreak)
5. Show **cost savings** from redistribution

## 📊 Sample Output

```
Predicted Demand for O+ (next 7 days):
Date         Day        Demand   Range
2026-02-08   Sunday     38      32-44
2026-02-09   Monday     52      46-58
2026-02-10   Tuesday    48      42-54

Alerts:
⚠️ HIGH DEMAND ALERT: O+ demand predicted to reach 52 units on Monday
```

## 🔧 Troubleshooting

**Import errors?**
```bash
pip install --upgrade -r requirements.txt
```

**Port 8000 busy?**
Edit main.py, change: `uvicorn.run(app, host="0.0.0.0", port=8001)`

**Need help?**
Check README.md for full documentation

---

**Ready to build the future of blood banking! 🩸🤖**
