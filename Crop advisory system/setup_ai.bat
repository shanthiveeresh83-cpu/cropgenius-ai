@echo off
echo ========================================
echo  AI Features Setup - Smart Farm Assistant
echo ========================================
echo.

cd backend

echo [1/3] Installing core dependencies...
pip install pillow numpy
echo.

echo [2/3] Optional: Install TensorFlow for CNN?
echo Press Y for Yes, N to skip
choice /C YN /M "Install TensorFlow"
if errorlevel 2 goto skip_tf
if errorlevel 1 goto install_tf

:install_tf
echo Installing TensorFlow (CPU version)...
pip install tensorflow-cpu
goto llm_choice

:skip_tf
echo Skipping TensorFlow (will use fallback)
echo.

:llm_choice
echo [3/3] Optional: Install Groq for FREE LLM?
echo Press Y for Yes, N to skip
choice /C YN /M "Install Groq"
if errorlevel 2 goto skip_llm
if errorlevel 1 goto install_llm

:install_llm
echo Installing Groq...
pip install groq
echo.
echo ========================================
echo  Get FREE Groq API Key:
echo  https://console.groq.com
echo.
echo  Add to .env file:
echo  GROQ_API_KEY=your_key_here
echo ========================================
goto done

:skip_llm
echo Skipping LLM (will use fallback)
echo.

:done
echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Your AI features are ready:
echo  - Disease Detection: %CD%\disease_detection.py
echo  - LLM Advisor: %CD%\llm_advisor.py
echo.
echo Demo page: ..\frontend\ai_demo.html
echo.
echo Start backend: python app.py
echo ========================================
pause
