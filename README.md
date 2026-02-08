# RaktSetu Ai - Predictive Blood Inventory Management

An intelligent, AI-powered blood bank management system that predicts demand, optimizes inventory, and prevents shortages before they happen.

## 🌟 Features

### 1. **AI-Based Predictive Forecasting**
- Predicts blood demand by type (A+, O-, etc.) up to 30 days ahead
- Uses machine learning with historical data, seasonal trends, and event patterns
- Provides confidence intervals and uncertainty estimates
- Ensemble model approach (Random Forest + Gradient Boosting)

### 2. **Smart Inventory Management**
- Real-time inventory status monitoring
- Safety stock level calculations
- Days-until-shortage predictions
- Automated urgency level detection

### 3. **Intelligent Alerts System**
- Context-aware notifications
- Urgency-based prioritization (critical, high, medium, low)
- Shortage predictions before they happen
- Weekend and seasonal demand adjustments

### 4. **What-If Scenario Simulation**
- Highway accident scenarios
- Disease outbreak simulations (dengue, etc.)
- Festival/event impact analysis
- Emergency planning support

### 5. **Multi-Location Optimization**
- Smart blood redistribution suggestions
- Waste reduction recommendations
- Inter-facility transfer optimization
- Cost savings calculations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone or download the project**
```bash
cd bloodflow-ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation
Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### 1. Predict Blood Demand
```bash
POST /api/v1/predict
```

**Request:**
```json
{
  "blood_type": "O+",
  "days_ahead": 7,
  "location": "main_bank"
}
```

**Response:**
```json
{
  "blood_type": "O+",
  "predictions": [
    {
      "date": "2026-02-08",
      "day_name": "Sunday",
      "predicted_demand": 38,
      "confidence_lower": 32,
      "confidence_upper": 44,
      "confidence_interval": "32-44"
    }
  ],
  "alerts": [
    "⚠️ HIGH DEMAND ALERT: O+ demand predicted to reach 52 units on 2026-02-12"
  ],
  "confidence_score": 85.3,
  "generated_at": "2026-02-07T10:30:00"
}
```

### 2. Get Inventory Status
```bash
GET /api/v1/inventory/status?blood_type=O+
```

**Response:**
```json
{
  "timestamp": "2026-02-07T10:30:00",
  "inventory_status": [
    {
      "blood_type": "O+",
      "current_stock": 45,
      "safety_stock": 50,
      "optimal_stock": 80,
      "predicted_demand": 280,
      "days_until_shortage": 11,
      "recommendation": "⚠️ RECOMMEND: Stock 35 units of O+ soon.",
      "urgency_level": "medium",
      "stock_percentage": 56.3
    }
  ],
  "critical_count": 0,
  "overall_health": "caution"
}
```

### 3. Get Active Alerts
```bash
GET /api/v1/alerts?urgency=critical
```

### 4. Train Model
```bash
POST /api/v1/train
```

**Request:**
```json
{
  "blood_type": "O+",
  "retrain": true
}
```

### 5. Run What-If Simulation
```bash
GET /api/v1/simulation?scenario=highway_accident&severity=high
```

**Scenarios:**
- `highway_accident`
- `festival`
- `dengue_outbreak`
- `monsoon`

**Response:**
```json
{
  "scenario": "highway_accident",
  "severity": "high",
  "results": {
    "O+": {
      "baseline_demand": 40,
      "surge_demand": 120,
      "additional_units_needed": 80,
      "percentage_increase": 200.0
    },
    "O-": {
      "baseline_demand": 15,
      "surge_demand": 60,
      "additional_units_needed": 45,
      "percentage_increase": 300.0
    }
  },
  "recommendations": [
    "🚨 PRIORITY: Increase stock for O-, O+, A+",
    "📞 Activate emergency donor notification system"
  ]
}
```

### 6. Get Redistribution Suggestions
```bash
GET /api/v1/optimization/redistribute
```

## 🧪 Testing the API

### Using cURL

**Predict demand:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"blood_type": "O+", "days_ahead": 7}'
```

**Get inventory status:**
```bash
curl "http://localhost:8000/api/v1/inventory/status"
```

**Run simulation:**
```bash
curl "http://localhost:8000/api/v1/simulation?scenario=dengue_outbreak&severity=high"
```

### Using Python

```python
import requests

# Predict demand
response = requests.post(
    "http://localhost:8000/api/v1/predict",
    json={
        "blood_type": "O+",
        "days_ahead": 14,
        "location": "main_bank"
    }
)
print(response.json())

# Get alerts
alerts = requests.get("http://localhost:8000/api/v1/alerts").json()
for alert in alerts['alerts']:
    print(f"{alert['urgency'].upper()}: {alert['message']}")
```

## 🏗️ Project Structure

```
bloodflow-ai/
├── main.py                          # FastAPI application
├── requirements.txt                 # Dependencies
├── README.md                        # Documentation
├── models/
│   ├── __init__.py
│   ├── demand_predictor.py         # ML prediction model
│   └── inventory_optimizer.py      # Inventory optimization
└── utils/
    ├── __init__.py
    └── data_generator.py            # Synthetic data generation
```

## 🔧 Configuration

### Blood Types Supported
- A+, A-, B+, B-, AB+, AB-, O+, O-

### Prediction Parameters
- **Max days ahead**: 30 days
- **Default prediction window**: 7 days
- **Confidence level**: 95% (±1.96 standard deviations)

### Safety Stock Levels (Configurable in `inventory_optimizer.py`)
```python
safety_stock = {
    "O+": 50,
    "A+": 40,
    "B+": 30,
    "O-": 25,
    "A-": 20,
    "AB+": 15,
    "B-": 12,
    "AB-": 10
}
```

## 🎯 Use Cases

1. **Daily Operations**
   - Monitor inventory levels
   - Get daily demand predictions
   - Receive shortage alerts

2. **Emergency Planning**
   - Simulate disaster scenarios
   - Plan emergency response
   - Optimize stock placement

3. **Resource Optimization**
   - Reduce blood wastage
   - Optimize collection schedules
   - Multi-location balancing

4. **Strategic Planning**
   - Seasonal demand forecasting
   - Long-term inventory planning
   - Budget optimization

## 📊 Model Performance

The prediction model uses ensemble learning combining:
- **Random Forest**: Captures non-linear patterns
- **Gradient Boosting**: Improves accuracy through boosting

Typical metrics (on synthetic data):
- MAE: 3-5 units
- RMSE: 5-8 units
- R² Score: 0.80-0.90

## 🚀 Next Steps for Production

1. **Database Integration**
   - Connect to PostgreSQL/MySQL
   - Store historical demand data
   - Track real inventory

2. **Enhanced ML Models**
   - Add LSTM for time series
   - Include Prophet for seasonality
   - Incorporate external data (weather, events)

3. **Notification System**
   - SMS integration (Twilio)
   - Email notifications
   - Push notifications (Firebase)

4. **Blockchain Integration**
   - Unit traceability
   - Immutable audit logs
   - Smart contracts

5. **Frontend Dashboard**
   - React/Next.js UI
   - Real-time charts
   - Interactive maps

6. **Advanced Features**
   - Donor matching algorithm
   - Blood expiry optimization
   - Mobile app integration

## 🤝 Contributing

This is a hackathon/demo project. For production use:
1. Replace synthetic data with real hospital data
2. Implement proper authentication
3. Add comprehensive error handling
4. Set up monitoring and logging
5. Deploy with proper security measures

## 📝 License

MIT License - Feel free to use for educational and commercial purposes.

## 🎓 Educational Value

This project demonstrates:
- ✅ FastAPI REST API development
- ✅ Machine Learning model deployment
- ✅ Time series forecasting
- ✅ Ensemble learning techniques
- ✅ Healthcare data modeling
- ✅ Production-ready code structure
- ✅ API documentation with Swagger/OpenAPI

## 💡 Tips for Hackathon Demo

1. **Start with**: Show the interactive docs at `/docs`
2. **Demo flow**: 
   - Predict demand → Show high demand alert
   - Check inventory → Show shortage warning
   - Run simulation → Show emergency scenario
   - Get redistribution → Show optimization savings
3. **Highlight**: AI predictions, smart alerts, what-if scenarios
4. **Emphasize**: Waste reduction, cost savings, lives saved

---

**Built for BloodFlow AI Hackathon** 🩸🤖

For questions or improvements, check the API documentation or review the code!
