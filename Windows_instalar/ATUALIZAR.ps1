param(
  [Parameter(Mandatory=$true)][string]$ProjectDir
)
$ErrorActionPreference = "Stop"
$Repo = "Pablo672-sys/Live-do-Abismo-Thiago-Reyeres2"
$Api = "https://api.github.com/repos/$Repo/commits/main"
$ZipUrl = "https://github.com/$Repo/archive/refs/heads/main.zip"
$Temp = Join-Path ([IO.Path]::GetTempPath()) ("boneco-update-" + [guid]::NewGuid().ToString("N"))
$Zip = Join-Path $Temp "main.zip"
$Extract = Join-Path $Temp "extract"
$Protected = @(".git", ".venv", "assets", "private", "runs", "logs", "config", "__pycache__")
try {
  if (-not (Test-Path (Join-Path $ProjectDir "start_boneco_windows.ps1"))) {
    throw "Pasta do projeto nao reconhecida: $ProjectDir"
  }
  New-Item -ItemType Directory -Path $Temp -Force | Out-Null
  Write-Host "[1/4] Consultando versao no GitHub..." -ForegroundColor Cyan
  $commit = Invoke-RestMethod -Uri $Api -Headers @{ "User-Agent" = "Boneco-do-Abismo-Updater" } -TimeoutSec 25
  $sha = [string]$commit.sha
  if ($sha.Length -ne 40) { throw "O GitHub nao retornou uma versao valida." }
  Write-Host ("Versao remota: " + $sha.Substring(0,8))
  Write-Host "[2/4] Baixando pacote oficial..." -ForegroundColor Cyan
  Invoke-WebRequest -Uri $ZipUrl -OutFile $Zip -Headers @{ "User-Agent" = "Boneco-do-Abismo-Updater" } -TimeoutSec 180
  Expand-Archive -LiteralPath $Zip -DestinationPath $Extract -Force
  $Root = Get-ChildItem -LiteralPath $Extract -Directory | Select-Object -First 1
  if (-not $Root) { throw "O ZIP baixado nao contem a pasta do projeto." }
  Write-Host "[3/4] Atualizando codigo sem apagar dados pessoais..." -ForegroundColor Cyan
  Get-ChildItem -LiteralPath $Root.FullName -Force | ForEach-Object {
    $name = $_.Name
    if ($Protected -contains $name -or $name -in @(".env", ".env.local", ".env.production")) {
      Write-Host ("Preservado: " + $name) -ForegroundColor DarkGray
      return
    }
    $destination = Join-Path $ProjectDir $name
    if ($_.PSIsContainer) {
      Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse -Force
    } else {
      Copy-Item -LiteralPath $_.FullName -Destination $destination -Force
    }
  }
  $runs = Join-Path $ProjectDir "runs"
  New-Item -ItemType Directory -Path $runs -Force | Out-Null
  Set-Content -LiteralPath (Join-Path $runs "zip_update_commit.txt") -Value $sha -Encoding ASCII
  Write-Host "[4/4] Atualizando dependencias Python..." -ForegroundColor Cyan
  $python = Join-Path $ProjectDir ".venv\Scripts\python.exe"
  if (-not (Test-Path $python)) {
    py -3.12 -m venv (Join-Path $ProjectDir ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Nao consegui criar o ambiente Python. Verifique se o Python 3.12 esta instalado." }
  }
  & $python -m pip install -r (Join-Path $ProjectDir "requirements.txt")
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar requirements.txt." }
  & $python -m pip install -e $ProjectDir --no-deps
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar o projeto." }
  Write-Host "Atualizacao concluida com sucesso." -ForegroundColor Green
} catch {
  Write-Host ("ERRO: " + $_.Exception.Message) -ForegroundColor Red
  exit 1
} finally {
  if (Test-Path $Temp) { Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue }
}
