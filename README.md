# 🐧 Linux System Manager

A modern system management tool for Linux systems with both GUI and TUI interfaces. Monitor your system resources, manage processes, and browse files with an intuitive graphical interface or terminal-based interface.

## ✨ Features

- **Real-time System Monitoring** - CPU, Memory, Disk usage with live updates
- **Process Management** - View and manage running processes with clickable buttons
- **File Manager** - Browse files and directories with double-click navigation
- **Terminal Emulator** - Execute commands directly in the GUI
- **Modern GUI** - Beautiful graphical interface with tabs and buttons
- **TUI Alternative** - Terminal-based interface for command-line lovers
- **Lightweight** - Minimal dependencies, fast and efficient
- **Cross-distribution** - Works on Ubuntu, Debian, CentOS, Arch Linux, and more

## 🚀 Quick Start

### Prerequisites
- Linux operating system
- Python 3.6 or higher
- pip3 package manager
- tkinter (for GUI version)
  - Ubuntu/Debian: `sudo apt install python3-tk`
  - CentOS/RHEL: `sudo yum install tkinter`
  - Arch Linux: `sudo pacman -S tk`

### Installation

1. **Clone or download the project:**
   ```bash
   git clone https://github.com/Florex0Real/linux-system-manager.git
   cd linux-system-manager
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Or install manually:**
   ```bash
   pip3 install -r requirements.txt
   chmod +x linux_system_manager.py
   ```

### Usage

**GUI Version (Recommended):**
```bash
./run_gui.sh
# or
python3 linux_gui_manager.py
```

**Terminal Version:**
```bash
python3 linux_system_manager.py
# or
./linux_system_manager.py
```

## 🎮 Controls

### GUI Version
- **Clickable Buttons** - All functions accessible via buttons
- **Tab Navigation** - Switch between Dashboard, Processes, Files, Terminal
- **Double-click Files** - Enter directories or open files
- **Refresh Buttons** - Update data with single click
- **Kill Process Button** - Terminate selected processes
- **Terminal Tab** - Execute commands directly in GUI

### Terminal Version (TUI)
- `q`, `Q`, `ESC` - Quit application
- `h`, `H` - Show help screen
- `r`, `R` - Refresh data
- `c`, `C` - Clear screen
- `d`, `D` - Dashboard view (default)
- `p`, `P` - Processes view
- `f`, `F` - File manager view

## 📊 System Information Displayed

### Dashboard View
- **System Info**: Hostname, Kernel version, Architecture, Uptime
- **CPU Info**: Usage percentage, Core count, Frequency, Load average
- **Memory Info**: Total, Used, Available memory with usage bar
- **Disk Info**: Total, Used, Free space with usage bar

### Processes View
- **Top 15 processes** sorted by CPU usage
- **Process details**: PID, Name, CPU%, Memory%, Status
- **Real-time updates** every 2 seconds

### File Manager View
- **Current directory** path display
- **File listing** with type, name, size, modified date, permissions
- **Directory navigation** with visual indicators

## 🛠️ Technical Details

### Dependencies
- `psutil` - System and process utilities
- `curses` - Terminal UI (built-in with Python)

### System Requirements
- Linux kernel 2.6+
- Python 3.6+
- 50MB RAM minimum
- Terminal with color support

### Architecture
- **Modular design** - Separate classes for different functionalities
- **Real-time updates** - Background data refresh
- **Error handling** - Graceful error recovery
- **Signal handling** - Proper cleanup on exit

## 🔧 Development

### Project Structure
```
linux-system-manager/
├── linux_system_manager.py  # Terminal version (TUI)
├── linux_gui_manager.py     # GUI version
├── run_gui.sh              # GUI launcher script
├── requirements.txt         # Python dependencies
├── install.sh              # Installation script
└── README.md               # This file
```

### Key Classes
- `SystemInfo` - System data gathering
- `FileManager` - File system operations
- `TerminalEmulator` - Command execution
- `LinuxSystemManager` - Main application controller

### Adding New Features
1. Create new methods in appropriate classes
2. Add new view types in main application
3. Update help screen with new controls
4. Test on different Linux distributions

## 🐛 Troubleshooting

### Common Issues

**"psutil module not found"**
```bash
pip3 install psutil
```

**"Permission denied" errors**
```bash
chmod +x linux_system_manager.py
```

**Terminal doesn't support colors**
- Use a modern terminal emulator (GNOME Terminal, Konsole, etc.)
- Check TERM environment variable

**High CPU usage**
- The application refreshes every 2 seconds by default
- This is normal for real-time monitoring

### Performance Tips
- Close unnecessary applications for better performance
- Use SSD storage for faster file operations
- Ensure adequate RAM for smooth operation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on different Linux distributions
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and psutil
- Inspired by htop, btop, and other system monitors
- Designed for Linux enthusiasts and system administrators

---

**Made with ❤️ for the Linux community**

*Enjoy monitoring your Linux system! 🐧*
