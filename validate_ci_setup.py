#!/usr/bin/env python3
"""
Validation Script for CI/CD Pipeline Setup
Verifies that all required files and configurations are in place.
"""

import sys
import json
from pathlib import Path
from typing import List, Tuple


class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {text}")


def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists"""
    if file_path.exists():
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description} missing: {file_path}")
        return False


def validate_project_structure() -> Tuple[int, int]:
    """Validate basic project structure"""
    print_header("Project Structure Validation")

    passed = 0
    failed = 0

    # Check critical directories
    directories = [
        (Path("src"), "Source directory"),
        (Path("tests"), "Tests directory"),
        (Path(".github/workflows"), "GitHub workflows directory"),
    ]

    for dir_path, description in directories:
        if dir_path.exists() and dir_path.is_dir():
            print_success(f"{description}: {dir_path}")
            passed += 1
        else:
            print_error(f"{description} missing: {dir_path}")
            failed += 1

    # Check critical files
    files = [
        (Path("pyproject.toml"), "Project configuration"),
        (Path("langgraph.json"), "LangGraph configuration"),
        (Path("README.md"), "README file"),
    ]

    for file_path, description in files:
        if check_file_exists(file_path, description):
            passed += 1
        else:
            failed += 1

    return passed, failed


def validate_workflows() -> Tuple[int, int]:
    """Validate GitHub Actions workflows"""
    print_header("GitHub Actions Workflows Validation")

    passed = 0
    failed = 0

    workflows = [
        (Path(".github/workflows/test.yml"), "Test workflow"),
        (Path(".github/workflows/quality.yml"), "Quality workflow"),
        (Path(".github/workflows/deploy.yml"), "Deploy workflow"),
    ]

    for workflow_path, description in workflows:
        if check_file_exists(workflow_path, description):
            passed += 1

            # Basic content validation
            try:
                content = workflow_path.read_text()
                if "runs-on: ubuntu-latest" in content:
                    print_info(f"  -> Valid workflow structure detected")
                else:
                    print_warning(f"  -> Workflow might be missing 'runs-on' directive")
            except Exception as e:
                print_warning(f"  -> Could not read workflow file: {e}")
        else:
            failed += 1

    return passed, failed


def validate_langgraph_config() -> Tuple[int, int]:
    """Validate langgraph.json configuration"""
    print_header("LangGraph Configuration Validation")

    passed = 0
    failed = 0

    langgraph_json = Path("langgraph.json")

    if not langgraph_json.exists():
        print_error("langgraph.json not found")
        return 0, 1

    try:
        with open(langgraph_json, 'r') as f:
            config = json.load(f)

        print_success("langgraph.json is valid JSON")
        passed += 1

        # Check required fields
        required_fields = {
            "python_version": "3.11",
            "dependencies": ["."],
            "graphs": {"forjador_v5_pipeline": "src.agent:graph"},
        }

        for field, expected in required_fields.items():
            if field in config:
                if field == "python_version":
                    if config[field] == expected:
                        print_success(f"Python version: {config[field]}")
                        passed += 1
                    else:
                        print_warning(f"Python version is {config[field]}, expected {expected}")
                        failed += 1
                elif field == "dependencies":
                    if "." in config[field]:
                        print_success(f"Dependencies include current directory")
                        passed += 1
                    else:
                        print_warning(f"Dependencies might not include current directory")
                        failed += 1
                elif field == "graphs":
                    if "forjador_v5_pipeline" in config[field]:
                        graph_entry = config[field]["forjador_v5_pipeline"]
                        print_success(f"Graph entry point: {graph_entry}")
                        passed += 1
                    else:
                        print_error(f"Graph 'forjador_v5_pipeline' not found in config")
                        failed += 1
            else:
                print_error(f"Required field '{field}' missing from langgraph.json")
                failed += 1

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in langgraph.json: {e}")
        failed += 1
    except Exception as e:
        print_error(f"Error reading langgraph.json: {e}")
        failed += 1

    return passed, failed


def validate_pyproject_toml() -> Tuple[int, int]:
    """Validate pyproject.toml configuration"""
    print_header("pyproject.toml Validation")

    passed = 0
    failed = 0

    pyproject = Path("pyproject.toml")

    if not pyproject.exists():
        print_error("pyproject.toml not found")
        return 0, 1

    try:
        content = pyproject.read_text()

        print_success("pyproject.toml exists")
        passed += 1

        # Check for critical dependencies
        critical_deps = [
            "langgraph",
            "langchain",
            "langchain-google-genai",
            "pytest",
            "ruff",
            "mypy",
        ]

        for dep in critical_deps:
            if dep in content:
                print_success(f"Dependency found: {dep}")
                passed += 1
            else:
                print_warning(f"Dependency might be missing: {dep}")
                failed += 1

    except Exception as e:
        print_error(f"Error reading pyproject.toml: {e}")
        failed += 1

    return passed, failed


def validate_entry_point() -> Tuple[int, int]:
    """Validate that the entry point exists"""
    print_header("Entry Point Validation")

    passed = 0
    failed = 0

    entry_file = Path("src/agent.py")

    if not entry_file.exists():
        print_error(f"Entry point file not found: {entry_file}")
        return 0, 1

    print_success(f"Entry point file exists: {entry_file}")
    passed += 1

    try:
        content = entry_file.read_text()

        # Check for graph export
        if "graph" in content:
            print_success("Entry point contains 'graph' variable/function")
            passed += 1
        else:
            print_warning("Entry point might not export 'graph'")
            print_info("  -> Ensure src/agent.py exports 'graph' variable")
            failed += 1

    except Exception as e:
        print_error(f"Error reading entry point: {e}")
        failed += 1

    return passed, failed


def check_documentation() -> Tuple[int, int]:
    """Check if documentation files exist"""
    print_header("Documentation Check")

    passed = 0
    failed = 0

    docs = [
        (Path("GITHUB_SECRETS_SETUP.md"), "Secrets setup guide"),
        (Path("DEPLOYMENT_CHECKLIST.md"), "Deployment checklist"),
        (Path(".github/workflows/README.md"), "Workflows documentation"),
    ]

    for doc_path, description in docs:
        if check_file_exists(doc_path, description):
            passed += 1
        else:
            failed += 1

    return passed, failed


def print_summary(total_passed: int, total_failed: int):
    """Print validation summary"""
    print_header("Validation Summary")

    total = total_passed + total_failed
    percentage = (total_passed / total * 100) if total > 0 else 0

    print(f"Total checks: {total}")
    print(f"{Colors.GREEN}Passed: {total_passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {total_failed}{Colors.RESET}")
    print(f"Success rate: {percentage:.1f}%\n")

    if total_failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] All validation checks passed!{Colors.RESET}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
        print("1. Configure GitHub secrets (see GITHUB_SECRETS_SETUP.md)")
        print("2. Push to GitHub repository")
        print("3. Follow DEPLOYMENT_CHECKLIST.md for deployment")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}[FAILED] Some validation checks failed{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please fix the issues above before deploying{Colors.RESET}")
        return 1


def main():
    """Main validation function"""
    print(f"\n{Colors.BOLD}CI/CD Pipeline Setup Validation{Colors.RESET}")
    print(f"Validating configuration for LangGraph Platform Cloud deployment\n")

    total_passed = 0
    total_failed = 0

    # Run all validations
    validations = [
        validate_project_structure,
        validate_workflows,
        validate_langgraph_config,
        validate_pyproject_toml,
        validate_entry_point,
        check_documentation,
    ]

    for validation_func in validations:
        passed, failed = validation_func()
        total_passed += passed
        total_failed += failed

    # Print summary and exit
    return print_summary(total_passed, total_failed)


if __name__ == "__main__":
    sys.exit(main())
