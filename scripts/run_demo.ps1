$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$requirements = Join-Path $projectRoot "requirements.txt"
$app = Join-Path $projectRoot "app\streamlit_app.py"
$seedScript = Join-Path $projectRoot "scripts\seed_demo_data.py"

Set-Location $projectRoot

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating the project virtual environment..." -ForegroundColor Cyan
    py -3.11 -m venv (Join-Path $projectRoot ".venv")
}

& $venvPython -c "import streamlit, sklearn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing project dependencies into .venv..." -ForegroundColor Cyan
    & $venvPython -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed. Check your network connection and run: .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    }
}

& $venvPython $seedScript

$selectedPort = $null
$preferredPort = if ($env:AEGISDESK_PORT) { [int]$env:AEGISDESK_PORT } else { 8501 }
foreach ($candidatePort in $preferredPort..($preferredPort + 99)) {
    $listener = $null
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $candidatePort)
        $listener.Start()
        $selectedPort = $candidatePort
        break
    }
    catch {
        continue
    }
    finally {
        if ($listener) { $listener.Stop() }
    }
}

if (-not $selectedPort) {
    throw "No available local port was found between $preferredPort and $($preferredPort + 99)."
}

Write-Host "Starting AegisDesk at http://localhost:$selectedPort" -ForegroundColor Green
& $venvPython -m streamlit run $app --server.port $selectedPort
if ($LASTEXITCODE -ne 0) {
    throw "Streamlit stopped with exit code $LASTEXITCODE."
}
