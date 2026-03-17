@echo off
echo ========================================
echo Crop Advisory System Backend Startup
echo ========================================
echo.
echo Checking Python installation...
py --version
echo.
echo Installing/Verifying Flask...
py -m pip install flask flask-cors flask-jwt-extended flask-bcrypt python-dotenv numpy pandas scikit-learn requests --quiet
echo.
echo Starting backend server...
echo.
py app.py
pause
