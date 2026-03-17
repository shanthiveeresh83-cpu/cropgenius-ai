@echo off
echo Installing packages in .venv-1...
call .venv-1\Scripts\activate.bat
pip install flask flask-cors flask-jwt-extended flask-bcrypt python-dotenv numpy pandas scikit-learn requests
deactivate

echo Installing packages in .venv-2...
call .venv-2\Scripts\activate.bat
pip install flask flask-cors flask-jwt-extended flask-bcrypt python-dotenv numpy pandas scikit-learn requests
deactivate

echo Done!
pause
