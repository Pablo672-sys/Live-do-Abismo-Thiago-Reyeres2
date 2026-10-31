@echo off
setlocal
chcp 65001 >nul
title Instalar Boneco do Abismo
set "INSTALLER=%~dp0Windows_instalar\INSTALAR.bat"
if not exist "%INSTALLER%" (
  echo ERRO: nao encontrei Windows_instalar\INSTALAR.bat.
  echo Extraia o ZIP COMPLETO do projeto antes de executar.
  pause
  exit /b 1
)
call "%INSTALLER%"
exit /b %ERRORLEVEL%
