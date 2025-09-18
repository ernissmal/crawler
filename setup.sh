#!/bin/bash

# Enhanced Oak Table Scraper - Installation and Setup Script
# This script helps set up the enhanced scraper environment

echo "🌳 Enhanced Oak Table Scraper v2.0 - Setup Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Python is installed
echo
print_info "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_status "Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_error "Python not found. Please install Python 3.7+ first."
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 7 ]; then
    print_status "Python version is compatible (3.7+)"
else
    print_error "Python 3.7+ is required. Current version: $PYTHON_MAJOR.$PYTHON_MINOR"
    exit 1
fi

# Check if pip is installed
echo
print_info "Checking pip installation..."
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    print_status "pip found"
    PIP_CMD="pip"
else
    print_error "pip not found. Please install pip first."
    exit 1
fi

# Ask about virtual environment
echo
print_info "Virtual environment setup..."
read -p "Do you want to create a virtual environment? (recommended) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ ! -d ".venv" ]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv .venv
        print_status "Virtual environment created in .venv/"
    else
        print_warning "Virtual environment already exists"
    fi
    
    print_info "Activating virtual environment..."
    source .venv/bin/activate
    print_status "Virtual environment activated"
    
    # Update pip in virtual environment
    pip install --upgrade pip
else
    print_warning "Skipping virtual environment creation"
fi

# Install Python dependencies
echo
print_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_status "Python dependencies installed successfully"
    else
        print_error "Failed to install Python dependencies"
        exit 1
    fi
else
    print_error "requirements.txt not found"
    exit 1
fi

# Check for ChromeDriver (needed for Google search)
echo
print_info "Checking ChromeDriver for Google search functionality..."
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version)
    print_status "ChromeDriver found: $CHROMEDRIVER_VERSION"
else
    print_warning "ChromeDriver not found"
    
    # Try to install via webdriver-manager
    print_info "Attempting to install ChromeDriver automatically..."
    $PYTHON_CMD -c "
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

try:
    service = Service(ChromeDriverManager().install())
    print('✓ ChromeDriver installed successfully via webdriver-manager')
except Exception as e:
    print(f'✗ Failed to install ChromeDriver: {e}')
    print('Please install manually:')
    print('  macOS: brew install chromedriver')
    print('  Ubuntu: sudo apt-get install chromium-chromedriver')
    print('  Or download from: https://chromedriver.chromium.org/')
" 2>/dev/null
fi

# Create directories
echo
print_info "Creating necessary directories..."
mkdir -p logs
mkdir -p exports
mkdir -p config
print_status "Directories created: logs/, exports/, config/"

# Copy sample configuration
echo
print_info "Setting up configuration..."
if [ ! -f "scraper_config.yaml" ]; then
    if [ -f "sample_config.yaml" ]; then
        cp sample_config.yaml scraper_config.yaml
        print_status "Configuration file created from sample"
    else
        print_warning "Sample configuration not found, will use defaults"
    fi
else
    print_warning "Configuration file already exists"
fi

# Test installation
echo
print_info "Testing installation..."
$PYTHON_CMD -c "
import sys
required_modules = [
    'fastapi', 'pydantic', 'pandas', 'requests', 'bs4', 
    'forex_python', 'selenium', 'yaml', 'openpyxl'
]

missing_modules = []
for module in required_modules:
    try:
        if module == 'bs4':
            import bs4
        elif module == 'forex_python':
            from forex_python.converter import CurrencyRates
        elif module == 'yaml':
            import yaml
        else:
            __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f'✗ Missing modules: {missing_modules}')
    sys.exit(1)
else:
    print('✓ All required modules are available')
"

if [ $? -eq 0 ]; then
    print_status "Installation test passed"
else
    print_error "Installation test failed"
    exit 1
fi

# Display next steps
echo
echo "🎉 Setup completed successfully!"
echo
echo "Next steps:"
echo "==========="
echo
echo "1. Activate virtual environment (if created):"
echo "   source .venv/bin/activate"
echo
echo "2. Review and customize configuration:"
echo "   edit scraper_config.yaml"
echo
echo "3. Start the enhanced scraper API:"
echo "   python enhanced_main.py"
echo
echo "4. Or run the original scraper:"
echo "   python main.py"
echo
echo "5. Access the web interface:"
echo "   http://localhost:8000"
echo
echo "6. Run tests (optional):"
echo "   python test_framework.py"
echo
echo "📚 See README.md for detailed usage instructions"

# Check if we should start the server
echo
read -p "Do you want to start the enhanced scraper API now? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting enhanced scraper API..."
    echo "Press Ctrl+C to stop the server"
    echo "Access the API at: http://localhost:8000"
    echo
    $PYTHON_CMD enhanced_main.py
fi

print_status "Setup script completed!"