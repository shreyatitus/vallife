@echo off
echo ========================================
echo Starting LifeLink Frontend Server
echo ========================================
echo.
echo Frontend will be available at:
echo http://localhost:8000
echo.
cd valkyire\lifelink_frontend\lifelink_frontend
python -m http.server 8000
pause
