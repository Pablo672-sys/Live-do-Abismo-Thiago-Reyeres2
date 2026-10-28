# Boneco do Abismo — iniciar no Windows 10/11
$ErrorActionPreference = "Stop"
$Project = $PSScriptRoot
$VenvPython = Join-Path $Project ".venv\Scripts\python.exe"

Set-Location $Project
$env:BONECO_GAME_DIR = $Project
$env:BONECO_GAME_ASSETS_DIR = Join-Path $Project "assets"
$env:BONECO_GAME_HOST = "0.0.0.0"
$env:BONECO_GAME_PORT = "9292"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Criando ambiente Python do Boneco..." -ForegroundColor Cyan
    py -3.12 -m venv (Join-Path $Project ".venv")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python 3.12 não encontrado. Instale Python 3.12 e marque 'Add Python to PATH'." -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

Write-Host "Atualizando ferramentas e verificando dependências..." -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Falha ao atualizar pip." }
& $VenvPython -m pip install -r (Join-Path $Project "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar requirements.txt." }
& $VenvPython -m pip install -e $Project --no-deps
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar o projeto." }

$ip = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -match '^192\.168\.|^10\.|^172\.(1[6-9]|2[0-9]|3[0-1])\.' -and $_.InterfaceOperationalStatus -eq 'Up' } |
    Select-Object -First 1 -ExpandProperty IPAddress

Write-Host ""
Write-Host "=== BONECO DO ABISMO ===" -ForegroundColor Magenta
Write-Host "No próprio PC: http://127.0.0.1:9292" -ForegroundColor Green
if ($ip) { Write-Host ("No celular (mesmo Wi-Fi): http://" + $ip + ":9292") -ForegroundColor Green }
Write-Host "Mantenha esta janela aberta enquanto usar o Boneco." -ForegroundColor Yellow
Write-Host "Se o celular não conectar, permita Python no Firewall do Windows para redes privadas." -ForegroundColor Yellow
Write-Host "Para parar o servidor, pressione Ctrl+C." -ForegroundColor Yellow
Write-Host ""

& $VenvPython -m uvicorn boneco_game.main:app --host 0.0.0.0 --port 9292
