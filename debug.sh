#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i:"$1" >/dev/null 2>&1
}

# Function to print status messages
print_status() {
    echo -e "${GREEN}[DEBUG]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if virtual environment is active
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Virtual environment is not active"
        print_error "Please run: source venv/bin/activate (or equivalent)"
        exit 1
    fi
}

# Check TURN server
check_turn() {
    if ! command_exists turnserver; then
        print_warning "coturn is not installed. TURN server will not be available"
        return 1
    fi
    
    if port_in_use 3478; then
        print_warning "Port 3478 is already in use. TURN server may already be running"
        return 1
    fi
    
    return 0
}

# Start development server with debugging
start_debug_server() {
    print_status "Starting development server..."
    export PYTHONPATH="${PYTHONPATH}:${PWD}"
    export DEBUG=1
    
    # Start Python debugger if requested
    if [ "$1" == "--pdb" ]; then
        python3 -m pdb -m server.api
    else
        python3 -m server.api
    fi
}

# Main execution
main() {
    check_venv
    
    # Check if TURN server should be started
    if [ "$1" != "--no-turn" ]; then
        if check_turn; then
            print_status "Starting TURN server..."
            turnserver -c /etc/turnserver.conf &
            TURN_PID=$!
        fi
    fi
    
    # Trap Ctrl+C to clean up
    trap 'cleanup' INT
    
    # Start server with remaining args
    start_debug_server "${@:2}"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    if [ ! -z "$TURN_PID" ]; then
        kill $TURN_PID 2>/dev/null
    fi
    exit 0
}

# Show help
show_help() {
    echo "Usage: ./debug.sh [OPTIONS]"
    echo
    echo "Options:"
    echo "  --help      Show this help message"
    echo "  --no-turn   Don't start the TURN server"
    echo "  --pdb       Start with Python debugger"
    echo
    echo "Examples:"
    echo "  ./debug.sh              # Start everything"
    echo "  ./debug.sh --no-turn    # Start without TURN server"
    echo "  ./debug.sh --pdb        # Start with Python debugger"
}

# Parse arguments
case "$1" in
    --help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 