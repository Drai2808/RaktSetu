# BloodFlow AI - Complete Installation Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

**On Windows:**
```bash
pip install numpy
pip install pandas
pip install scikit-learn
pip install fastapi
pip install uvicorn
pip install pydantic
pip install joblib
pip install python-multipart
pip install requests
```

**On Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

### Step 2: Navigate to the Project Folder

```bash
cd d:/bloodflow-ai
```

(Make sure you're in the folder where main.py is located)

### Step 3: Run the Server

**Option A - Double-click (Windows):**
- Double-click `run.bat`

**Option B - Command Line (Windows):**
```bash
run.bat
```

**Option C - Mac/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Option D - Direct Python:**
```bash
# Windows
set PYTHONPATH=%cd%
python main.py

# Mac/Linux
export PYTHONPATH=$(pwd)
python3 main.py
```

---

## ✅ Verify Installation

Once the server starts, you should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Open in browser:**
- Main API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Error: "No module named 'models'"

**Solution 1 - Use run.bat (Easiest):**
```bash
# Just double-click run.bat or run it from command line
run.bat
```

**Solution 2 - Set PYTHONPATH manually:**
```bash
# Windows (in Command Prompt)
set PYTHONPATH=d:\bloodflow-ai
python main.py

# Windows (in PowerShell)
$env:PYTHONPATH = "d:\bloodflow-ai"
python main.py

# Mac/Linux
export PYTHONPATH=/path/to/bloodflow-ai
python3 main.py
```

**Solution 3 - Install as package:**
```bash
pip install -e .
python main.py
```

### Error: "Microsoft Visual C++ 14.0 required"

Install packages individually (see Step 1 above) instead of using requirements.txt

### Error: "Port 8000 already in use"

Edit `main.py`, change the last line to:
```python
uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
```

Then access at http://localhost:8001

### Error: Import errors after installation

```bash
# Uninstall and reinstall
pip uninstall scikit-learn numpy pandas -y
pip install numpy pandas scikit-learn
```

---

## 📁 Project Structure

Your folder should look like this:
```
bloodflow-ai/
├── main.py                    ← Main application
├── run.bat                    ← Windows run script
├── run.sh                     ← Mac/Linux run script
├── requirements.txt           ← Dependencies
├── setup.py                   ← Package setup
├── README.md                  ← Full documentation
├── INSTALL.md                 ← This file
├── models/
│   ├── __init__.py
│   ├── demand_predictor.py
│   └── inventory_optimizer.py
└── utils/
    ├── __init__.py
    └── data_generator.py
```

---

## 🧪 Testing

### Test 1: Run the demo
```bash
python test_demo.py
```

Should show all features working.

### Test 2: Quick API test
```bash
# In browser
http://localhost:8000/docs

# Or with curl
curl http://localhost:8000/
```

### Test 3: Predict blood demand
```bash
curl -X POST "http://localhost:8000/api/v1/predict" ^
  -H "Content-Type: application/json" ^
  -d "{\"blood_type\": \"O+\", \"days_ahead\": 7}"
```

---

## 🎯 Recommended Setup for Windows

1. **Install Anaconda** (easiest, avoids all issues)
   - Download: https://www.anaconda.com/download
   - Install it
   - Open "Anaconda Prompt"
   - Run:
   ```bash
   conda create -n bloodflow python=3.11
   conda activate bloodflow
   conda install numpy pandas scikit-learn joblib
   pip install fastapi uvicorn pydantic python-multipart requests
   cd d:\bloodflow-ai
   python main.py
   ```

2. **Or use the run.bat script**
   - Just double-click `run.bat`
   - Everything should work!

---

## 📝 Alternative: Virtual Environment (Optional)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install numpy pandas scikit-learn fastapi uvicorn pydantic joblib python-multipart requests

# Run
python main.py
```

---

## ✨ Success Checklist

- [ ] All packages installed without errors
- [ ] Can run `python main.py` without "No module named" errors
- [ ] Server starts on http://localhost:8000
- [ ] Can access http://localhost:8000/docs in browser
- [ ] API responds to test requests

---

## 🆘 Still Having Issues?

1. Make sure you're in the correct directory:
   ```bash
   cd d:\bloodflow-ai
   dir
   ```
   You should see main.py in the list

2. Make sure Python is installed:
   ```bash
   python --version
   ```
   Should show Python 3.8 or higher

3. Use the run.bat script - it handles everything automatically!

4. Check PYTHONPATH is set:
   ```bash
   echo %PYTHONPATH%
   ```
   Should include your project directory

---

## 🎉 You're Ready!

Once the server is running, check out:
- **Interactive API Docs**: http://localhost:8000/docs
- **README.md** for full feature list
- **QUICKSTART.md** for API examples
