@echo off
setlocal
chcp 65001 >nul
title Boneco do Abismo - Painel
cd /d "%~dp0"
set "BONECO_GAME_DIR=%CD%"
set "BONECO_GAME_ASSETS_DIR=%CD%\assets"
set "BONECO_GAME_HOST=0.0.0.0"
set "BONECO_GAME_PORT=9292"
set "PYTHON=%CD%\.venv\Scripts\python.exe"

echo.
echo ==========================================
echo       BONECO DO ABISMO - INICIAR
echo ==========================================
echo.

if not exist "%PYTHON%" (
  echo Ambiente Python nao encontrado.
  echo Execute primeiro Windows_instalar\INSTALAR.bat.
  pause
  exit /b 1
)

echo Abrindo o painel...
start "" /b cmd /c "timeout /t 3 /nobreak ^>nul ^& start http://127.0.0.1:9292"
"%PYTHON%" -m uvicorn boneco_game.main:app --host 0.0.0.0 --port 9292
echo.
echo O servidor foi encerrado.
pause
