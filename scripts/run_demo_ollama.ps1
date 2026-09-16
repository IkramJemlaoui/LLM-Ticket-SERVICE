$ErrorActionPreference = "Stop"

$env:LLM_PROVIDER = "ollama"
$env:OLLAMA_BASE_URL = "http://localhost:11434/v1"
$env:OLLAMA_MODEL = "qwen2.5:latest"
$env:OLLAMA_API_KEY = "ollama"
$env:LLM_TIMEOUT_SECONDS = "180"
$env:ALLOW_MOCK_FALLBACK = "false"

try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
}
catch {
    throw "Ollama is not running. Open Ollama first, then run this command again."
}

$availableModels = (Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5).models.name
if ($availableModels -notcontains $env:OLLAMA_MODEL) {
    throw "Model '$($env:OLLAMA_MODEL)' is not installed. Run: ollama pull $($env:OLLAMA_MODEL)"
}

Write-Host "Using local Ollama model $($env:OLLAMA_MODEL). No paid API key is needed." -ForegroundColor Cyan
& (Join-Path $PSScriptRoot "run_demo.ps1")
