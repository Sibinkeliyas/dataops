# start-app.ps1

Write-Host "🔄 Starting full app setup and launch process..."

# Step 1: Build Frontend
Write-Host "📁 Navigating to frontend and installing dependencies..."
Set-Location ./frontend
npm install

Write-Host "⚙️ Building frontend..."
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed."
    exit $LASTEXITCODE
}
Write-Host "✅ Frontend build complete."

# Step 2: Set location back to root and then backend
Set-Location ../backend

# Step 3: Create virtual environment if not present
if (-not (Test-Path ".venv")) {
    Write-Host "🐍 Creating Python virtual environment..."
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    }
    & $pythonCmd.Source -m venv .venv
}

# Step 4: Install backend dependencies
Write-Host "📦 Installing backend Python dependencies..."
$venvPythonPath = Join-Path (Get-Location) ".venv/Scripts/python.exe"
if (-not (Test-Path $venvPythonPath)) {
    $venvPythonPath = Join-Path (Get-Location) ".venv/bin/python" # For Linux
}
& $venvPythonPath -m pip install -r requirements.txt

# Step 5: Start Backend (serving frontend + API)
Write-Host "🚀 Starting backend server on http://localhost:3000"
& $venvPythonPath -m quart --app main:app run --port 3000 --host 0.0.0.0 --reload
