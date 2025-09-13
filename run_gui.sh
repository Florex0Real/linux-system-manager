#!/bin/bash

# Linux System Manager - GUI Launcher
# Author: AI Assistant

echo "🐧 Linux System Manager - GUI Version"
echo "====================================="
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

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: tkinter is not installed"
    echo "Please install tkinter:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  CentOS/RHEL: sudo yum install tkinter"
    echo "  Arch Linux: sudo pacman -S tk"
    exit 1
fi

# Check if psutil is installed
python3 -c "import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: psutil is not installed"
    echo "Installing psutil..."
    pip3 install psutil
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install psutil"
        exit 1
    fi
fi

echo "✅ All dependencies are available"
echo "🚀 Starting GUI application..."
echo

# Run the GUI application
python3 linux_gui_manager.py
