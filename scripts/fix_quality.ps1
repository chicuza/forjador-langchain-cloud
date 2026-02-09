# Forjador v5 - Auto-fix Quality Issues (PowerShell)
# Purpose: Automatically fix formatting and common issues
# Version: 1.0.0
# Date: 2026-02-09

# Configuration
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $PROJECT_ROOT

Write-Host "==================================" -ForegroundColor Blue
Write-Host "Forjador v5 - Auto-fix Quality" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue
Write-Host ""

# 1. Run Ruff formatter
Write-Host "[1/3] Running Ruff formatter..." -ForegroundColor Yellow
python -m ruff format src\ tests\
Write-Host "✓ Code formatted" -ForegroundColor Green
Write-Host ""

# 2. Run Ruff auto-fix
Write-Host "[2/3] Running Ruff auto-fix..." -ForegroundColor Yellow
python -m ruff check --fix src\ tests\
Write-Host "✓ Auto-fixable issues resolved" -ForegroundColor Green
Write-Host ""

# 3. Sort imports
Write-Host "[3/3] Sorting imports..." -ForegroundColor Yellow
python -m ruff check --select I --fix src\ tests\
Write-Host "✓ Imports sorted" -ForegroundColor Green
Write-Host ""

Write-Host "==================================" -ForegroundColor Green
Write-Host "Quality fixes applied!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Run '.\scripts\check_quality.ps1' to verify all checks pass."
