#!/bin/bash

# Function to detect shell type
detect_shell() {
    if [ -n "$BASH_VERSION" ]; then
        echo "bash"
    elif [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$FISH_VERSION" ]; then
        echo "fish"
    else
        # Default to bash if can't determine
        echo "bash"
    fi
}

# Function to check if Python 3.8+ is installed
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if (( $(echo "$python_version >= 3.8" | bc -l) )); then
            echo "Python $python_version found"
            return 0
        fi
    fi
    echo "Error: Python 3.8 or higher is required"
    exit 1
}

# Function to create and activate virtual environment
setup_venv() {
    if [ -d "venv" ]; then
        echo "Virtual environment already exists"
    else
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Detect shell and activate accordingly
    shell_type=$(detect_shell)
    echo "Detected $shell_type shell"

    case $shell_type in
        "fish")
            source venv/bin/activate.fish 2>/dev/null || \
            source venv/Scripts/activate.fish 2>/dev/null || \
            echo "Error: Could not find fish activation script"
            ;;
        "zsh")
            source venv/bin/activate 2>/dev/null || \
            source venv/Scripts/activate 2>/dev/null || \
            echo "Error: Could not find zsh activation script"
            ;;
        *)  # Default to bash
            source venv/bin/activate 2>/dev/null || \
            source venv/Scripts/activate 2>/dev/null || \
            echo "Error: Could not find bash activation script"
            ;;
    esac

    if [ $? -ne 0 ]; then
        echo "Error: Failed to activate virtual environment"
        exit 1
    fi
}

# Function to install requirements
install_requirements() {
    echo "Installing requirements..."
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Function to run the application
run_app() {
    echo "Starting Rhystic.io server..."
    python -m server.api
}

# Main script
main() {
    check_python
    setup_venv
    install_requirements
    
    if [ "$1" == "--run" ]; then
        run_app
    else
        echo "Setup complete! To run the server, use: ./setup.sh --run"
    fi
}

# Run main function with all arguments
main "$@" 