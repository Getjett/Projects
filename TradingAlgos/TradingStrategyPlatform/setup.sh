#!/bin/bash

# AstraCharts Trading Platform - Complete Setup Script
# This script will install all dependencies and start both frontend and backend

set -e  # Exit on any error

echo "🚀 AstraCharts Trading Platform Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in correct directory
if [ ! -f "setup.sh" ]; then
    print_error "Please run this script from the TradingStrategyPlatform directory"
    exit 1
fi

# Check system requirements
print_status "Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d" " -f2 | cut -d"." -f1-2)
print_success "Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

NPM_VERSION=$(npm --version)
print_success "npm $NPM_VERSION found"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip for Python 3."
    exit 1
fi

print_success "All system requirements met!"

# Setup Backend
print_status "Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Backend dependencies installed successfully!"

# Go back to root directory
cd ..

# Setup Frontend
print_status "Setting up Frontend..."
cd frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install --legacy-peer-deps

print_success "Frontend dependencies installed successfully!"

# Go back to root directory
cd ..

print_success "Setup completed successfully!"
echo ""
echo "🎯 Setup Summary:"
echo "=================="
echo "✅ Python virtual environment created"
echo "✅ Backend dependencies installed"
echo "✅ Frontend dependencies installed"
echo "✅ System ready to start!"
echo ""
echo "To start the application, run:"
echo "  ./start.sh"
echo ""
echo "Or start services individually:"
echo "  Backend:  ./start-backend.sh"
echo "  Frontend: ./start-frontend.sh"