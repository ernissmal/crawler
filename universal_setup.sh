#!/bin/bash

# Universal Scraper Setup Script
# Automated setup for the Universal Multi-Purpose Scraper

set -e

echo "🚀 Universal Multi-Purpose Scraper Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
    print_status "Python $PYTHON_VERSION found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version | cut -d " " -f 2)
    if [[ $PYTHON_VERSION == 3.* ]]; then
        print_status "Python $PYTHON_VERSION found"
        PYTHON_CMD="python"
    else
        print_error "Python 3.7+ is required. Found Python $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check pip
print_info "Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    print_status "pip3 found"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    print_status "pip found"
else
    print_error "pip is not installed. Please install pip first."
    exit 1
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
    print_status "Python dependencies installed"
else
    print_warning "requirements.txt not found. Installing core dependencies..."
    $PIP_CMD install fastapi pydantic pandas requests beautifulsoup4 selenium webdriver-manager openpyxl xlsxwriter pyyaml uvicorn
    print_status "Core dependencies installed"
fi

# Check for Chrome/Chromium
print_info "Checking for Chrome browser..."
if command -v google-chrome &> /dev/null; then
    print_status "Google Chrome found"
    CHROME_FOUND=true
elif command -v chromium-browser &> /dev/null; then
    print_status "Chromium browser found"
    CHROME_FOUND=true
elif command -v chromium &> /dev/null; then
    print_status "Chromium found"
    CHROME_FOUND=true
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "/Applications/Google Chrome.app" ]; then
        print_status "Google Chrome found on macOS"
        CHROME_FOUND=true
    else
        print_warning "Chrome not found. Please install Google Chrome."
        CHROME_FOUND=false
    fi
else
    print_warning "Chrome/Chromium not found. Please install Google Chrome."
    CHROME_FOUND=false
fi

# Install ChromeDriver using webdriver-manager (automatic)
print_info "Setting up ChromeDriver..."
$PYTHON_CMD -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

try:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.quit()
    print('ChromeDriver setup successful')
except Exception as e:
    print(f'ChromeDriver setup failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_status "ChromeDriver configured successfully"
else
    print_error "ChromeDriver setup failed"
    exit 1
fi

# Create directories
print_info "Creating directory structure..."
mkdir -p configs
mkdir -p exports
mkdir -p logs
mkdir -p cache
print_status "Directory structure created"

# Make scripts executable
print_info "Making scripts executable..."
chmod +x cli.py
chmod +x examples.py
if [ -f "setup.sh" ]; then
    chmod +x setup.sh
fi
print_status "Scripts made executable"

# Test basic functionality
print_info "Testing basic functionality..."

# Test imports
$PYTHON_CMD -c "
import sys
try:
    import fastapi
    import pydantic
    import pandas
    import requests
    import bs4
    import selenium
    import yaml
    print('✅ All core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "Basic functionality test passed"
else
    print_error "Basic functionality test failed"
    exit 1
fi

# Test CLI
print_info "Testing CLI interface..."
$PYTHON_CMD cli.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status "CLI interface working"
else
    print_warning "CLI test had issues but setup can continue"
fi

# Display usage information
echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
echo "📚 Quick Start Guide:"
echo ""
echo "1. 🔍 Search for products:"
echo "   $PYTHON_CMD cli.py product \"oak furniture Kaunas\" --max-results 10"
echo ""
echo "2. 🏢 Search for companies:"
echo "   $PYTHON_CMD cli.py company \"IT companies Lisburn\" --regions \"Northern Ireland\""
echo ""
echo "3. 👤 Search for people:"
echo "   $PYTHON_CMD cli.py person \"executives Dubai public directory\" --extraction basic"
echo ""
echo "4. 📱 Search for social media:"
echo "   $PYTHON_CMD cli.py social_media \"tech startups Ireland Twitter\""
echo ""
echo "5. 📧 Search for emails:"
echo "   $PYTHON_CMD cli.py email \"tech companies contact Ireland\""
echo ""
echo "6. 🌐 Start API server:"
echo "   $PYTHON_CMD universal_scraper.py"
echo ""
echo "7. 📖 See all examples:"
echo "   $PYTHON_CMD examples.py"
echo ""
echo "📁 Configuration files:"
echo "   - configs/product_config.yaml"
echo "   - configs/company_config.yaml"
echo "   - configs/person_config.yaml"
echo "   - configs/social_media_config.yaml"
echo "   - configs/email_config.yaml"
echo ""
echo "🔧 Test with dry run:"
echo "   $PYTHON_CMD cli.py product \"test query\" --dry-run"
echo ""
echo "📊 Run examples:"
echo "   $PYTHON_CMD examples.py"
echo ""
echo "🆘 For help:"
echo "   $PYTHON_CMD cli.py --help"
echo "   $PYTHON_CMD cli.py product --help"
echo ""

if [ "$CHROME_FOUND" = false ]; then
    print_warning "⚠️  Chrome browser not detected. Please install Google Chrome for full functionality."
    echo "   - macOS: Download from https://www.google.com/chrome/"
    echo "   - Ubuntu: sudo apt-get install google-chrome-stable"
    echo "   - CentOS: sudo yum install google-chrome-stable"
    echo ""
fi

print_status "Universal Multi-Purpose Scraper is ready to use! 🎯"