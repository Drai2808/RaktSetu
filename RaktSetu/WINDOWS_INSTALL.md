# Windows Installation Guide

## Option 1: Easy Install (Recommended for Windows)

### Step 1: Install Python packages individually
```bash
# Install in this order to avoid build issues
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

### Step 2: Verify installation
```bash
python -c "import sklearn, pandas, numpy, fastapi; print('✓ All packages installed successfully!')"
```

### Step 3: Run the application
```bash
python main.py
```

---

## Option 2: Use Anaconda (Easiest - Highly Recommended)

Anaconda comes with pre-compiled packages that work on Windows without C++ compiler issues.

### Download Anaconda
https://www.anaconda.com/download

### Install packages with Conda
```bash
# Create a new environment
conda create -n bloodflow python=3.11

# Activate environment
conda activate bloodflow

# Install packages
conda install numpy pandas scikit-learn joblib
pip install fastapi uvicorn pydantic python-multipart requests

# Run the app
python main.py
```

---

## Option 3: Install Microsoft C++ Build Tools

If you want to use pip with requirements.txt:

1. **Download Microsoft C++ Build Tools**
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. **Install with these options selected:**
   - Desktop development with C++
   - MSVC v143 - VS 2022 C++ x64/x86 build tools
   - Windows SDK

3. **Restart your computer**

4. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

---

## Option 4: Use Pre-built Wheels

Download pre-compiled wheels from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/

Search for and download:
- numpy
- pandas  
- scikit-learn

Install with:
```bash
pip install path/to/downloaded/wheel.whl
pip install fastapi uvicorn pydantic python-multipart joblib requests
```

---

## Troubleshooting

### Error: "Microsoft Visual C++ 14.0 required"
→ Use Option 1 (install individually) or Option 2 (Anaconda)

### Error: "No module named 'sklearn'"
```bash
pip install scikit-learn
```

### Error: Port 8000 already in use
Edit main.py, change last line to:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Import errors after installation
```bash
pip uninstall scikit-learn numpy pandas
pip install numpy pandas scikit-learn --no-cache-dir
```

---

## Quick Test

After installation, test if everything works:

```bash
python test_demo.py
```

You should see the demo running without errors!

---

## ✅ Recommended Approach for Windows Users

**EASIEST: Use Anaconda (Option 2)**
- No compiler issues
- Pre-built packages
- Everything just works
- Takes 5 minutes

**ALTERNATIVE: Install packages one by one (Option 1)**
- No Anaconda needed
- Slightly slower
- Usually works fine
