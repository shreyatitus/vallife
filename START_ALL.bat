@echo off
echo ========================================
echo Starting LifeLink - Backend and Frontend
echo ========================================

start "LifeLink Backend" cmd /k "cd valkyire\lifelink_backend\lifelink_backend && python app_firebase.py"

timeout /t 3 /nobreak

start "LifeLink Frontend" cmd /k "cd valkyire\lifelink_frontend\lifelink_frontend && python -m http.server 8000"

echo.
echo ========================================
echo Backend: http://localhost:5000
echo Frontend: http://localhost:8000
echo ========================================
