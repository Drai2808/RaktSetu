# 🩸 BloodFlow AI - ULTRA QUICK START

## 🚀 **Just Run ONE Command!**

### Windows:
```bash
run.bat
```

### Mac/Linux:
```bash
python start.py
```

**OR simply:**
```bash
python main.py
```

---

## ✨ **That's It!**

The system will automatically:
1. ✅ Check and install missing dependencies
2. ✅ Create and initialize database
3. ✅ Load 500 donors with historical data
4. ✅ Start backend API (port 8000)
5. ✅ Start frontend dashboard (port 8501)
6. ✅ Open browser to http://localhost:8501

**Everything happens automatically!**

---

## 📊 **What You Get:**

When you run the command, you'll see:

```
🩸 BloodFlow AI - Starting...
✓ Database found - using existing data
  Donors: 500
  Donations: 2500
  Demand Records: 2920
✓ Initializing AI models...
✓ All systems ready!

🚀 Starting Backend API...
   Backend: http://localhost:8000
   Frontend: http://localhost:8501 (launching...)
   API Docs: http://localhost:8000/docs

🎨 Launching Streamlit dashboard...
✓ Frontend started!
✓ Opening browser...
```

Then your browser opens automatically showing the beautiful dashboard!

---

## 🎯 **First Time Setup:**

**Only if you don't have dependencies:**

```bash
pip install fastapi uvicorn pydantic streamlit plotly sqlalchemy numpy pandas scikit-learn joblib python-multipart requests
```

Or use:
```bash
pip install -r requirements.txt
```

---

## 🎨 **Using the Dashboard:**

The dashboard has 6 tabs:

1. **📊 Dashboard** - Real-time inventory
2. **🔮 Demand Prediction** - AI forecasting
3. **⛓️ Blockchain Tracking** - Blood unit traceability
4. **👥 Donor Intelligence** - Analytics
5. **🚨 Emergency Mode** - One-click response
6. **🔔 Notifications** - Alert system

---

## 🛑 **To Stop:**

Press **Ctrl+C** in the terminal

Both backend and frontend will shut down together!

---

## 💾 **Your Data Persists!**

- Database file: `bloodflow.db`
- Contains 500 donors, 2500+ donations
- Data survives restarts!
- Restart anytime - data is still there

---

## 🔄 **Reset Database (if needed):**

```bash
# Delete database
rm bloodflow.db  # Mac/Linux
del bloodflow.db  # Windows

# Run again - will recreate
python main.py
```

---

## 🎉 **That's Everything!**

**One command. Complete system. Ready to demo!**

---

## 📚 **More Info:**

- **START_HERE.md** - Complete setup guide
- **DATABASE_GUIDE.md** - Database documentation
- **FRONTEND_GUIDE.md** - Frontend features
- **FEATURES.md** - All 30+ features

---

## 🏆 **You're Ready for Your Hackathon!**

Just run: `python main.py`

Good luck! 🩸🤖
