@echo off
echo ========================================
echo   BloodFlow AI - Starting Frontend
echo ========================================
echo.

echo Starting Streamlit Dashboard...
echo Dashboard will be available at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run app.py

pause
