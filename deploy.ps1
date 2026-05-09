# ============================================================
# deploy.ps1 — Task 4 | CS2-IN-NCB | Knowledge Hub
# Full end-to-end deployment for Windows (PowerShell)
# Deploys: Bicep infrastructure + Flask API code
#
# Requirements:
#   - Azure CLI        : winget install Microsoft.AzureCLI
#   - Bicep CLI        : az bicep install
#   - Python 3.11      : winget install Python.Python.3.11
#   - ODBC Driver 18   : winget install Microsoft.ODBCDriverForSQLServer
#
# Usage:
#   .\deploy.ps1
#   .\deploy.ps1 -SkipBicep    (code deploy only)
#   .\deploy.ps1 -SkipCode     (Bicep only)
# ============================================================

param(
    [string]$ResourceGroup = "rg-knowledgehub-spoke1",
    [string]$WebAppName    = "app-knowledgehub-api",
    [string]$ApiDir        = ".\monitoring-api",
    [switch]$SkipBicep,
    [switch]$SkipCode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$BicepFile  = ".\bicep\appservice.bicep"
$ParamsFile = ".\bicep\appservice.parameters.json"
$ZipPath    = "$env:TEMP\monitoring-api.zip"

function Write-Step($n, $msg) {
    Write-Host ""
    Write-Host "==> [$n] $msg" -ForegroundColor Cyan
}
function Write-OK($msg)   { Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "    $msg"      -ForegroundColor White }
function Write-Note($msg) { Write-Host "    NOTE: $msg" -ForegroundColor Yellow }

# ─────────────────────────────────────────────────────────────
# Step 1 — Azure login check
# ─────────────────────────────────────────────────────────────
Write-Step 1 "Checking Azure login..."
$account = az account show --query "name" -o tsv 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Info "Not logged in. Launching az login..."
    az login
    $account = az account show --query "name" -o tsv
}
Write-OK "Logged in — subscription: $account"

# ─────────────────────────────────────────────────────────────
# Step 2 — Deploy Bicep (infrastructure)
# ─────────────────────────────────────────────────────────────
if (-not $SkipBicep) {
    Write-Step 2 "Deploying App Service infrastructure via Bicep..."

    if (-not (Test-Path $BicepFile))  { Write-Error "File not found: $BicepFile";  exit 1 }
    if (-not (Test-Path $ParamsFile)) { Write-Error "File not found: $ParamsFile"; exit 1 }

    $deployName = "deploy-appservice-$(Get-Date -Format 'yyyyMMddHHmm')"

    az deployment group create `
        --resource-group $ResourceGroup `
        --template-file  $BicepFile `
        --parameters     $ParamsFile `
        --name           $deployName `
        --verbose

    if ($LASTEXITCODE -ne 0) { Write-Error "Bicep deployment failed."; exit 1 }
    Write-OK "Bicep deployment complete — name: $deployName"
} else {
    Write-Note "Skipping Bicep (-SkipBicep flag set)"
}

# ─────────────────────────────────────────────────────────────
# Step 3 — Package Flask application (ZIP)
# ─────────────────────────────────────────────────────────────
if (-not $SkipCode) {
    Write-Step 3 "Packaging Flask API..."

    if (-not (Test-Path $ApiDir)) {
        Write-Error "API directory not found: $ApiDir`nSet -ApiDir to your monitoring-api path"
        exit 1
    }

    if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

    # Stage files excluding secrets, cache, and test artifacts
    $stagingDir = "$env:TEMP\monitoring-api-staging"
    if (Test-Path $stagingDir) { Remove-Item $stagingDir -Recurse -Force }
    New-Item -ItemType Directory -Path $stagingDir | Out-Null

    $excludePatterns = @("\.env$", "__pycache__", "\.pyc$", "\.pyo$",
                         "\\\.git\\", "\\venv\\", "\\\.venv\\", "\\tests\\",
                         "\.zip$", "\.tar\.gz$")

    Get-ChildItem -Path $ApiDir -Recurse -File | ForEach-Object {
        $rel  = $_.FullName.Substring((Resolve-Path $ApiDir).Path.Length + 1)
        $skip = $false
        foreach ($pat in $excludePatterns) {
            if ($rel -match $pat) { $skip = $true; break }
        }
        if (-not $skip) {
            $dest    = Join-Path $stagingDir $rel
            $destDir = Split-Path $dest -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item $_.FullName -Destination $dest
        }
    }

    Compress-Archive -Path "$stagingDir\*" -DestinationPath $ZipPath -Force
    Remove-Item $stagingDir -Recurse -Force

    $sizeMB = [math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
    Write-OK "Package ready: $ZipPath ($sizeMB MB)"
} else {
    Write-Note "Skipping code packaging (-SkipCode flag set)"
}

# ─────────────────────────────────────────────────────────────
# Step 4 — Deploy Flask code to App Service
# ─────────────────────────────────────────────────────────────
if (-not $SkipCode) {
    Write-Step 4 "Deploying Flask code to App Service..."

    az webapp deploy `
        --resource-group $ResourceGroup `
        --name           $WebAppName `
        --src-path       $ZipPath `
        --type           zip `
        --async          false

    if ($LASTEXITCODE -ne 0) { Write-Error "Code deployment failed."; exit 1 }
    Write-OK "Flask API deployed successfully"
}

# ─────────────────────────────────────────────────────────────
# Step 5 — Summary
# ─────────────────────────────────────────────────────────────
Write-Step 5 "Deployment summary"

$hostname = az webapp show `
    --resource-group $ResourceGroup `
    --name           $WebAppName `
    --query          "defaultHostName" -o tsv

Write-Host ""
Write-Host "  +---------------------------------------------------------+" -ForegroundColor DarkCyan
Write-Host "  |  App Service Deployment - Knowledge Hub Task 4          |" -ForegroundColor DarkCyan
Write-Host "  +---------------------------------------------------------+" -ForegroundColor DarkCyan
Write-Host "  |  Web App  : $WebAppName" -ForegroundColor White
Write-Host "  |  Hostname : $hostname" -ForegroundColor White
Write-Host "  |  Public   : DISABLED (Private Endpoint only)            |" -ForegroundColor Yellow
Write-Host "  +---------------------------------------------------------+" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "  Test from Monitoring VM (VLAN10) after VPN is active:"
Write-Host "  curl https://$hostname/api/v1/health/status" -ForegroundColor Gray
Write-Host ""
Write-Host "==> Done!" -ForegroundColor Green