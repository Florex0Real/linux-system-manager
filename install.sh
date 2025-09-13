#!/bin/bash

# Linux System Manager Installation Script
# Author: AI Assistant

echo "🐧 Linux System Manager - Installation Script"
echo "=============================================="
echo

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: This tool is designed for Linux systems only"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Arch Linux: sudo pacman -S python python-pip"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    echo "Please install pip3 first:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3-pip"
    echo "  Arch Linux: sudo pacman -S python-pip"
    exit 1
fi

echo "✅ Python 3 and pip3 are installed"
echo

# Install required packages
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

# Make the script executable
chmod +x linux_system_manager.py

echo
echo "🎉 Installation completed successfully!"
echo
echo "Usage:"
echo "  python3 linux_system_manager.py"
echo "  or"
echo "  ./linux_system_manager.py"
echo
echo "Features:"
echo "  • Real-time system monitoring"
echo "  • Process management"
echo "  • File manager"
echo "  • Terminal interface"
echo
echo "Keyboard shortcuts:"
echo "  q, ESC - Quit"
echo "  h - Help"
echo "  d - Dashboard"
echo "  p - Processes"
echo "  f - Files"
echo "  r - Refresh"
echo
echo "Enjoy using Linux System Manager! 🚀"
