@echo off
chcp 65001 >nul
setlocal
for %%I in ("%~dp0..") do set "PROJECT=%%~fI"
echo.
echo ============================================
echo   ATUALIZAR BONECO DO ABISMO - WINDOWS
echo ============================================
echo Feche primeiro a janela do servidor do Boneco.
echo Seus assets, configuracoes privadas e logs serao preservados.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ATUALIZAR.ps1" -ProjectDir "%PROJECT%"
if errorlevel 1 (
  echo.
  echo A atualizacao falhou. Leia a mensagem acima.
  pause
  exit /b 1
)
echo.
echo Atualizacao concluida. Iniciando o Boneco...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\start_boneco_windows.ps1"
pause
