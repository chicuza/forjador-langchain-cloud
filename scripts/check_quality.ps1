# Forjador v5 - Quality Check Script (PowerShell)
# Purpose: Run all quality checks for CI/CD pipeline (Windows compatible)
# Version: 1.0.0
# Date: 2026-02-09

$ErrorActionPreference = "Continue"

# Configuration
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $PROJECT_ROOT

Write-Host "==================================" -ForegroundColor Blue
Write-Host "Forjador v5 - Quality Gate Check" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue
Write-Host ""

# Track overall status
$CHECKS_PASSED = 0
$CHECKS_FAILED = 0

# Helper function to run checks
function Run-Check {
    param (
        [string]$Name,
        [string]$Command
    )

    Write-Host "Running: $Name" -ForegroundColor Yellow
    Write-Host "Command: $Command"
    Write-Host ""

    $output = Invoke-Expression $Command 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host "✓ $Name passed" -ForegroundColor Green
        Write-Host ""
        $script:CHECKS_PASSED++
        return $true
    } else {
        Write-Host "✗ $Name failed" -ForegroundColor Red
        Write-Host $output
        Write-Host ""
        $script:CHECKS_FAILED++
        return $false
    }
}

# 1. Code Formatting Check (Ruff)
Write-Host "[1/4] Checking code formatting..." -ForegroundColor Blue
Run-Check "Ruff Format Check" "python -m ruff format --check src\ tests\" | Out-Null

# 2. Linting (Ruff)
Write-Host "[2/4] Running linter..." -ForegroundColor Blue
Run-Check "Ruff Linting" "python -m ruff check src\ tests\" | Out-Null

# 3. Type Checking (MyPy)
Write-Host "[3/4] Running type checker..." -ForegroundColor Blue
Run-Check "MyPy Type Check" "python -m mypy src\" | Out-Null

# 4. Tests (Pytest)
Write-Host "[4/4] Running tests..." -ForegroundColor Blue
Run-Check "Pytest" "python -m pytest tests\ -v --cov=src --cov-report=term-missing --cov-report=html" | Out-Null

# Summary
Write-Host ""
Write-Host "==================================" -ForegroundColor Blue
Write-Host "Quality Gate Summary" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue
Write-Host "Passed: $CHECKS_PASSED" -ForegroundColor Green
Write-Host "Failed: $CHECKS_FAILED" -ForegroundColor Red
Write-Host ""

if ($CHECKS_FAILED -eq 0) {
    Write-Host "✓ All quality checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ Some quality checks failed. Please fix the issues above." -ForegroundColor Red
    exit 1
}
