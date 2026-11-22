$ErrorActionPreference = "Stop"
Write-Host "=== Diagnostico Ollama - Boneco do Abismo ===" -ForegroundColor Cyan
try {
    $version = ollama --version
    Write-Host "Ollama: $version" -ForegroundColor Green
} catch {
    Write-Host "Ollama nao encontrado. Instale em https://ollama.com/download" -ForegroundColor Red
    exit 1
}
try {
    $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5
    Write-Host "Servico local: OK" -ForegroundColor Green
    $models = @($tags.models | ForEach-Object { $_.name })
    if ($models -contains "llama3.2:3b") {
        Write-Host "Modelo llama3.2:3b: instalado" -ForegroundColor Green
    } else {
        Write-Host "Modelo llama3.2:3b ausente. Execute: ollama pull llama3.2:3b" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Servico nao respondeu em 127.0.0.1:11434." -ForegroundColor Red
    Write-Host "Tente abrir o aplicativo Ollama ou executar 'ollama serve' em outra janela."
    exit 1
}
