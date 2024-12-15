@echo off
REM This script installs the required dependencies for the project.

REM Change to the backend directory
cd /d "%~dp0.."

echo Installing dependencies from pyproject.toml...
pip install -e ".[test]"  REM Install all dependencies including test dependencies
echo All dependencies installed successfully.