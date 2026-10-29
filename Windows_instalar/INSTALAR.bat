@echo off
setlocal
chcp 65001 >nul
title Instalar Boneco do Abismo - Windows

for %%I in ("%~dp0..") do set "PROJECT=%%~fI"
cd /d "%PROJECT%"

echo.
echo ============================================
echo       BONECO DO ABISMO - WINDOWS
echo ============================================
echo.
echo Este instalador prepara o painel no Windows 10/11.
echo A primeira instalacao precisa de internet.
echo.

where py >nul 2>&1
if errorlevel 1 (
  echo ERRO: Python Launcher nao encontrado.
  echo Instale Python 3.12 pelo site https://www.python.org/downloads/
  echo Marque a opcao "Add python.exe to PATH" durante a instalacao.
  pause
  exit /b 1
)

py -3.12 --version >nul 2>&1
if errorlevel 1 (
  echo ERRO: Python 3.12 nao encontrado.
  echo Instale Python 3.12 e execute este arquivo novamente.
  pause
  exit /b 1
)

echo [1/2] Instalando dependencias do painel...
py -3.12 -m venv "%PROJECT%\.venv"
if errorlevel 1 goto erro

"%PROJECT%\.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto erro

"%PROJECT%\.venv\Scripts\python.exe" -m pip install -r "%PROJECT%\requirements.txt"
if errorlevel 1 goto erro

"%PROJECT%\.venv\Scripts\python.exe" -m pip install -e "%PROJECT%" --no-deps
if errorlevel 1 goto erro

echo.
echo [2/2] Instalacao do painel concluida.
echo.
echo IMPORTANTE: o motor de voz XTTS e os componentes de transmissao ao vivo
echo podem exigir configuracao adicional e nao sao garantidos por este instalador.
echo A gravacao de referencia da voz original precisa estar nos assets do projeto.
echo.
echo Abrindo o Boneco...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\start_boneco_windows.ps1"
if errorlevel 1 goto erro
exit /b 0

:erro
echo.
echo A instalacao encontrou um erro. Confira a mensagem acima e tente novamente.
pause
exit /b 1
