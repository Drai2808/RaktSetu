# BloodFlow AI - Frontend Guide

## 🎨 Beautiful Streamlit Dashboard

You now have a **complete web application** with:
- ✅ Backend API (FastAPI)
- ✅ Frontend Dashboard (Streamlit)

---

## 🚀 Quick Start (2 Steps!)

### Step 1: Install Streamlit
```bash
pip install streamlit plotly
```

### Step 2: Run Both Servers

**Open TWO Command Prompt windows:**

**Window 1 - Backend API:**
```bash
cd D:\bloodflow-ai
python main.py
```
This runs on: http://localhost:8000

**Window 2 - Frontend Dashboard:**
```bash
cd D:\bloodflow-ai
streamlit run app.py
```
This runs on: http://localhost:8501

---

## 🎯 Or Use the Batch Files (Even Easier!)

**Window 1:**
```bash
run.bat
```

**Window 2:**
```bash
run_frontend.bat
```

Your browser will automatically open the dashboard! 🎉

---

## 📊 Dashboard Features

### 1. **📊 Dashboard Tab**
- Real-time inventory status
- Visual charts (bar charts, pie charts)
- Color-coded urgency levels
- Smart recommendations
- Overall health indicator

### 2. **🔮 Demand Prediction Tab**
- Select blood type and time period
- Interactive prediction charts
- Confidence intervals
- Automated alerts
- Detailed forecast table

### 3. **⛓️ Blockchain Tracking Tab**
- Register new blood units
- Track complete unit history
- Verify authenticity
- Timeline visualization
- Immutable audit trail

### 4. **👥 Donor Intelligence Tab**
- Donor segmentation (Champions, Regular, At-Risk, Lost)
- Retention metrics
- Geographic distribution
- Interactive visualizations

### 5. **🚨 Emergency Mode Tab**
- One-click emergency activation
- Real-time donor notifications
- Current inventory snapshot
- Emergency status monitoring

### 6. **🔔 Notifications Tab**
- Send various notification types
- Notification analytics
- Performance metrics
- Distribution by type/channel

---

## 📸 What You'll See

### Dashboard Page:
- **Top Metrics:** Overall health, critical items, total units
- **Inventory Table:** All blood types with color-coded urgency
- **Charts:** Stock levels bar chart + urgency pie chart
- **Recommendations:** Smart suggestions based on current status

### Prediction Page:
- **Settings Panel:** Choose blood type and forecast period
- **Line Chart:** Demand forecast with confidence intervals
- **Alerts:** Automatic shortage warnings
- **Data Table:** Detailed daily predictions

### Blockchain Page:
- **Registration Form:** Add new blood units to blockchain
- **Tracking Interface:** View complete unit history
- **Verification:** Authenticity checks
- **Timeline:** Visual transaction history

---

## 🎮 Try It Out!

### 1. Open Dashboard
```
http://localhost:8501
```

### 2. Navigate Through Pages
Use the sidebar to switch between features:
- 📊 Dashboard
- 🔮 Demand Prediction
- ⛓️ Blockchain Tracking
- 👥 Donor Intelligence
- 🚨 Emergency Mode
- 🔔 Notifications

### 3. Test Features

**Predict Demand:**
1. Go to "Demand Prediction"
2. Select "O+" blood type
3. Choose 7 days
4. Click "Predict Demand"
5. See beautiful charts!

**Register Blood Unit:**
1. Go to "Blockchain Tracking"
2. Enter donor ID (e.g., D12345)
3. Select blood type
4. Enter location
5. Click "Register on Blockchain"
6. Get unique unit ID!

**Activate Emergency:**
1. Go to "Emergency Mode"
2. Select event type (e.g., "accident")
3. Choose blood types needed
4. Set severity to "high"
5. Click "ACTIVATE EMERGENCY MODE"
6. See donors contacted!

---

## 🎨 UI Features

### Beautiful Design:
- ✅ Professional color scheme (blood red theme)
- ✅ Responsive layout
- ✅ Interactive charts (Plotly)
- ✅ Color-coded urgency levels
- ✅ Real-time updates
- ✅ Clean, modern interface

### User Experience:
- ✅ API connection indicator
- ✅ Loading spinners
- ✅ Success/error messages
- ✅ Expandable sections
- ✅ Tabs for organization
- ✅ Tooltips and help text

---

## 🛠️ Troubleshooting

### Dashboard shows "API Offline"
Make sure the backend is running:
```bash
python main.py
```

### Charts not showing
Install Plotly:
```bash
pip install plotly
```

### Port already in use
The backend uses port 8000, frontend uses 8501.
If either is busy, you'll see an error. Stop the conflicting process.

### Page is blank
Refresh your browser (Ctrl+R or F5)

---

## 📝 File Structure

```
bloodflow-ai/
├── main.py              ← Backend API (FastAPI)
├── app.py               ← Frontend Dashboard (Streamlit) ⭐ NEW!
├── run.bat              ← Run backend
├── run_frontend.bat     ← Run frontend ⭐ NEW!
├── models/              ← AI models
└── utils/               ← Utilities
```

---

## 🎯 Complete Demo Flow

**Perfect 5-Minute Hackathon Demo:**

1. **Start with Dashboard** (30 sec)
   - Show real-time inventory
   - Point out critical items
   - Highlight beautiful charts

2. **Predict Demand** (1 min)
   - Select O+ blood type
   - Generate 7-day forecast
   - Show prediction chart with confidence intervals
   - Point out automated alerts

3. **Emergency Scenario** (1 min)
   - Go to Emergency Mode
   - Select "highway accident"
   - Choose O+, O-, A+ blood types
   - Activate emergency
   - Show donors contacted (e.g., "50 donors notified!")

4. **Blockchain Demo** (1 min)
   - Register new blood unit
   - Get unique ID
   - Track the unit
   - Show immutable history

5. **Donor Intelligence** (1 min)
   - Show donor segments
   - Display retention metrics
   - Geographic heatmap

6. **Wrap Up** (30 sec)
   - "Complete end-to-end system"
   - "AI + Blockchain + Analytics"
   - "Ready for production!"

---

## 🎉 You Now Have:

✅ **Backend API** - 30+ REST endpoints
✅ **Frontend Dashboard** - Beautiful Streamlit UI
✅ **AI Predictions** - Machine learning models
✅ **Blockchain** - Immutable traceability
✅ **Analytics** - Donor intelligence
✅ **Emergency Mode** - One-click response
✅ **Notifications** - Smart alerts

**This is a COMPLETE, production-ready system!** 🏆

---

## 💡 Tips for Best Experience

1. **Keep both servers running** - Don't close either window
2. **Refresh if stuck** - Sometimes Streamlit needs a refresh
3. **Use Chrome/Edge** - Best browser compatibility
4. **Full screen** - Press F11 for immersive experience
5. **Dark mode** - Settings → Theme → Dark (looks amazing!)

---

## 🚀 Ready to Present!

Your BloodFlow AI system is **complete and ready for your hackathon presentation**!

Good luck! 🩸🤖🏆
