#!/bin/bash

# ---------------------------------------------------------------------------
# run_main.sh - Script to Set Up and Launch FastAPI Application
#
# This script is designed to locate and activate a virtual environment for
# running a FastAPI application. It checks the operating system and shell 
# type to ensure compatibility with Linux, macOS, and Windows environments. 
# The script determines the correct activation path for the virtual environment 
# (either `bin/activate` for Linux/macOS or `Scripts/activate` for Windows),
# and activates it if found. If activation fails, an error message with 
# guidance is displayed.
#
# After successfully activating the virtual environment, the script launches 
# the FastAPI application using the `main.py` file located in the same 
# directory as this script.
#
# Usage:
#   ./run_main.sh
#
# Requirements:
#   - Bash shell
#   - Compatible with Linux, macOS, and Windows (PowerShell or Git Bash)
#   - A FastAPI application and virtual environment in the script's directory
#
# ---------------------------------------------------------------------------


# Set the base directory to where the script is located
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.venv"

# Function to activate the virtual environment based on OS and shell type
activate_virtual_env() {
    if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
        # Linux or macOS
        if [[ -f "$BASE_DIR/bin/activate" ]]; then
            echo "Initiating Virtual Environment..."
            source "$BASE_DIR/bin/activate"
        else
            echo "Error: Could not find the virtual environment activation script at $BASE_DIR/bin/activate"
            exit 1
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows Git Bash or Cygwin
        if [[ -f "$BASE_DIR/Scripts/activate" ]]; then
            echo "Initiating Virtual Environment..."
            source "$BASE_DIR/Scripts/activate"
        else
            echo "Error: Could not find the virtual environment activation script at $BASE_DIR/Scripts/activate"
            exit 1
        fi
    elif [[ "$OSTYPE" == "win32" ]]; then
        # Windows PowerShell
        if [[ -f "$BASE_DIR/Scripts/Activate.ps1" ]]; then
            echo "Initiating Virtual Environment..."
            pwsh -Command "$BASE_DIR/Scripts/Activate.ps1"
        else
            echo "Error: Could not find the PowerShell activation script at $BASE_DIR/Scripts/Activate.ps1"
            exit 1
        fi
    else
        echo "Unsupported OS or shell type. Please activate the virtual environment manually."
        exit 1
    fi
}

# Call the function to activate the virtual environment
activate_virtual_env

# Pause for 1 seconds
sleep 1

# Run the Python script using a relative path
# fastapi dev "$BASE_DIR/app/main.py"
uvicorn "app.main:app" --host 0.0.0.0 --port 8000