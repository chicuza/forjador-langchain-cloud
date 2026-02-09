# Forjador v5 - Test Runner Script (PowerShell)
# Purpose: Run tests with various options
# Version: 1.0.0
# Date: 2026-02-09

param(
    [Parameter(Position=0)]
    [string]$TestType = "all",

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ExtraArgs
)

# Configuration
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $PROJECT_ROOT

Write-Host "Forjador v5 - Test Runner" -ForegroundColor Blue
Write-Host ""

$ExtraArgsString = $ExtraArgs -join " "

switch ($TestType.ToLower()) {
    "all" {
        Write-Host "Running all tests..."
        python -m pytest tests\ -v $ExtraArgsString
    }

    "unit" {
        Write-Host "Running unit tests..."
        python -m pytest tests\ -v -m "not integration" $ExtraArgsString
    }

    "integration" {
        Write-Host "Running integration tests..."
        python -m pytest tests\ -v -m integration $ExtraArgsString
    }

    "fast" {
        Write-Host "Running fast tests (no coverage)..."
        python -m pytest tests\ -v --no-cov -m "not slow" $ExtraArgsString
    }

    "coverage" {
        Write-Host "Running tests with detailed coverage..."
        python -m pytest tests\ -v --cov=src --cov-report=term-missing --cov-report=html $ExtraArgsString
        Write-Host ""
        Write-Host "Coverage report generated in: htmlcov\index.html" -ForegroundColor Green
    }

    "parallel" {
        Write-Host "Running tests in parallel..."
        python -m pytest tests\ -v -n auto $ExtraArgsString
    }

    default {
        Write-Host "Usage: .\run_tests.ps1 {all|unit|integration|fast|coverage|parallel} [extra_args]"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\run_tests.ps1 all                    # Run all tests"
        Write-Host "  .\run_tests.ps1 unit                   # Run only unit tests"
        Write-Host "  .\run_tests.ps1 integration            # Run only integration tests"
        Write-Host "  .\run_tests.ps1 fast                   # Run fast tests without coverage"
        Write-Host "  .\run_tests.ps1 coverage               # Run with detailed coverage report"
        Write-Host "  .\run_tests.ps1 parallel               # Run tests in parallel"
        Write-Host "  .\run_tests.ps1 all -k test_pipeline   # Run specific test pattern"
        exit 1
    }
}
