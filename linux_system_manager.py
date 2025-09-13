#!/usr/bin/env python3
"""
Linux System Manager - Modern Terminal System Management Tool
Author: AI Assistant
Description: A comprehensive Linux system management tool with TUI interface
"""

import os
import sys
import time
import psutil
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
import json
import curses
from curses import wrapper
import signal
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SystemInfo:
    """System information gathering class"""
    
    @staticmethod
    def get_system_info():
        """Get basic system information"""
        try:
            uname = os.uname()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'hostname': uname.nodename,
                'system': uname.sysname,
                'kernel': uname.release,
                'architecture': uname.machine,
                'uptime': str(uptime).split('.')[0],
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_cpu_info():
        """Get CPU information and usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return {
                'usage_percent': cpu_percent,
                'core_count': cpu_count,
                'frequency': cpu_freq.current if cpu_freq else 'N/A',
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_memory_info():
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percentage': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percentage': swap.percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_disk_info():
        """Get disk usage information"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percentage': (disk_usage.used / disk_usage.total) * 100,
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_processes():
        """Get running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent'],
                        'status': proc_info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:20]  # Top 20 processes
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_network_info():
        """Get network information"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception as e:
            return {'error': str(e)}

class FileManager:
    """File management utilities"""
    
    def __init__(self, current_path='.'):
        self.current_path = Path(current_path).resolve()
    
    def list_files(self):
        """List files in current directory"""
        try:
            files = []
            for item in self.current_path.iterdir():
                stat = item.stat()
                files.append({
                    'name': item.name,
                    'is_dir': item.is_dir(),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'permissions': oct(stat.st_mode)[-3:]
                })
            
            # Sort: directories first, then files
            files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            return files
        except Exception as e:
            return {'error': str(e)}
    
    def change_directory(self, path):
        """Change current directory"""
        try:
            new_path = self.current_path / path
            if new_path.is_dir():
                self.current_path = new_path.resolve()
                return True
            return False
        except Exception as e:
            return False
    
    def get_current_path(self):
        """Get current directory path"""
        return str(self.current_path)

class TerminalEmulator:
    """Simple terminal command executor"""
    
    @staticmethod
    def execute_command(command):
        """Execute a shell command and return output"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1,
                'success': False
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'success': False
            }

class LinuxSystemManager:
    """Main application class"""
    
    def __init__(self):
        self.running = True
        self.current_view = 'dashboard'
        self.file_manager = FileManager()
        self.terminal = TerminalEmulator()
        self.refresh_interval = 2  # seconds
        self.last_refresh = 0
        
        # Data storage
        self.system_data = {}
        self.process_data = []
        self.file_data = []
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle system signals"""
        self.running = False
        sys.exit(0)
    
    def refresh_data(self):
        """Refresh all system data"""
        current_time = time.time()
        if current_time - self.last_refresh < self.refresh_interval:
            return
        
        self.last_refresh = current_time
        
        # Update system data
        self.system_data = {
            'system': SystemInfo.get_system_info(),
            'cpu': SystemInfo.get_cpu_info(),
            'memory': SystemInfo.get_memory_info(),
            'disk': SystemInfo.get_disk_info(),
            'network': SystemInfo.get_network_info()
        }
        
        # Update process data
        self.process_data = SystemInfo.get_processes()
        
        # Update file data
        self.file_data = self.file_manager.list_files()
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def format_percentage(self, value, total):
        """Format percentage with bar"""
        if total == 0:
            return "0%"
        
        percentage = (value / total) * 100
        bar_length = 20
        filled_length = int(bar_length * value // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"{percentage:.1f}% [{bar}]"
    
    def draw_header(self, stdscr):
        """Draw application header"""
        height, width = stdscr.getmaxyx()
        
        # Title
        title = "🐧 Linux System Manager"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(1))
        
        # Status line
        status = f"Last updated: {datetime.now().strftime('%H:%M:%S')} | Press 'q' to quit, 'h' for help"
        stdscr.addstr(1, 0, status, curses.color_pair(2))
        
        # Separator
        stdscr.addstr(2, 0, "─" * width, curses.color_pair(2))
    
    def draw_dashboard(self, stdscr):
        """Draw main dashboard view"""
        height, width = stdscr.getmaxyx()
        y = 3
        
        # System Information
        if 'system' in self.system_data:
            sys_info = self.system_data['system']
            stdscr.addstr(y, 0, "🖥️  System Information", curses.A_BOLD | curses.color_pair(1))
            y += 1
            
            info_lines = [
                f"Hostname: {sys_info.get('hostname', 'N/A')}",
                f"Kernel: {sys_info.get('kernel', 'N/A')}",
                f"Architecture: {sys_info.get('architecture', 'N/A')}",
                f"Uptime: {sys_info.get('uptime', 'N/A')}"
            ]
            
            for line in info_lines:
                if y < height - 1:
                    stdscr.addstr(y, 2, line, curses.color_pair(3))
                    y += 1
            y += 1
        
        # CPU Information
        if 'cpu' in self.system_data:
            cpu_info = self.system_data['cpu']
            stdscr.addstr(y, 0, "⚡ CPU Information", curses.A_BOLD | curses.color_pair(1))
            y += 1
            
            if 'error' not in cpu_info:
                cpu_usage = cpu_info.get('usage_percent', 0)
                core_count = cpu_info.get('core_count', 0)
                frequency = cpu_info.get('frequency', 0)
                
                stdscr.addstr(y, 2, f"Usage: {cpu_usage:.1f}%", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Cores: {core_count}", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Frequency: {frequency:.0f} MHz" if frequency != 'N/A' else "Frequency: N/A", curses.color_pair(3))
                y += 1
            y += 1
        
        # Memory Information
        if 'memory' in self.system_data:
            mem_info = self.system_data['memory']
            stdscr.addstr(y, 0, "💾 Memory Information", curses.A_BOLD | curses.color_pair(1))
            y += 1
            
            if 'error' not in mem_info:
                total = mem_info.get('total', 0)
                used = mem_info.get('used', 0)
                available = mem_info.get('available', 0)
                percentage = mem_info.get('percentage', 0)
                
                stdscr.addstr(y, 2, f"Total: {self.format_bytes(total)}", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Used: {self.format_bytes(used)}", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Available: {self.format_bytes(available)}", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Usage: {self.format_percentage(used, total)}", curses.color_pair(3))
                y += 1
            y += 1
        
        # Disk Information
        if 'disk' in self.system_data:
            disk_info = self.system_data['disk']
            stdscr.addstr(y, 0, "💿 Disk Information", curses.A_BOLD | curses.color_pair(1))
            y += 1
            
            if 'error' not in disk_info:
                total = disk_info.get('total', 0)
                used = disk_info.get('used', 0)
                free = disk_info.get('free', 0)
                
                stdscr.addstr(y, 2, f"Total: {self.format_bytes(total)}", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Used: {self.format_bytes(used)}", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Free: {self.format_bytes(free)}", curses.color_pair(3))
                y += 1
                stdscr.addstr(y, 2, f"Usage: {self.format_percentage(used, total)}", curses.color_pair(3))
                y += 1
    
    def draw_processes(self, stdscr):
        """Draw processes view"""
        height, width = stdscr.getmaxyx()
        y = 3
        
        stdscr.addstr(y, 0, "🔄 Running Processes", curses.A_BOLD | curses.color_pair(1))
        y += 2
        
        # Header
        header = f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'Memory%':<10} {'Status':<10}"
        stdscr.addstr(y, 0, header, curses.A_BOLD | curses.color_pair(2))
        y += 1
        stdscr.addstr(y, 0, "─" * len(header), curses.color_pair(2))
        y += 1
        
        # Process list
        for proc in self.process_data[:15]:  # Show top 15 processes
            if y >= height - 2:
                break
            
            if 'error' not in proc:
                pid = str(proc.get('pid', ''))
                name = proc.get('name', '')[:19]
                cpu = f"{proc.get('cpu_percent', 0):.1f}"
                memory = f"{proc.get('memory_percent', 0):.1f}"
                status = proc.get('status', '')[:9]
                
                line = f"{pid:<8} {name:<20} {cpu:<8} {memory:<10} {status:<10}"
                stdscr.addstr(y, 0, line, curses.color_pair(3))
                y += 1
    
    def draw_files(self, stdscr):
        """Draw file manager view"""
        height, width = stdscr.getmaxyx()
        y = 3
        
        stdscr.addstr(y, 0, f"📁 File Manager - {self.file_manager.get_current_path()}", curses.A_BOLD | curses.color_pair(1))
        y += 2
        
        # Header
        header = f"{'Type':<4} {'Name':<30} {'Size':<12} {'Modified':<20} {'Perms':<6}"
        stdscr.addstr(y, 0, header, curses.A_BOLD | curses.color_pair(2))
        y += 1
        stdscr.addstr(y, 0, "─" * len(header), curses.color_pair(2))
        y += 1
        
        # File list
        for file_info in self.file_data[:20]:  # Show first 20 files
            if y >= height - 2:
                break
            
            if 'error' not in file_info:
                file_type = "DIR" if file_info.get('is_dir', False) else "FILE"
                name = file_info.get('name', '')[:29]
                size = self.format_bytes(file_info.get('size', 0)) if not file_info.get('is_dir', False) else "-"
                modified = file_info.get('modified', datetime.now()).strftime('%Y-%m-%d %H:%M')
                perms = file_info.get('permissions', '000')
                
                line = f"{file_type:<4} {name:<30} {size:<12} {modified:<20} {perms:<6}"
                color = curses.color_pair(4) if file_info.get('is_dir', False) else curses.color_pair(3)
                stdscr.addstr(y, 0, line, color)
                y += 1
    
    def draw_help(self, stdscr):
        """Draw help screen"""
        height, width = stdscr.getmaxyx()
        y = 3
        
        stdscr.addstr(y, 0, "❓ Help - Linux System Manager", curses.A_BOLD | curses.color_pair(1))
        y += 2
        
        help_text = [
            "Keyboard Shortcuts:",
            "",
            "  q, Q, ESC    - Quit application",
            "  h, H         - Show this help",
            "  d, D         - Dashboard view",
            "  p, P         - Processes view", 
            "  f, F         - File manager view",
            "  r, R         - Refresh data",
            "  c, C         - Clear screen",
            "",
            "File Manager:",
            "  ↑/↓          - Navigate files",
            "  Enter        - Enter directory",
            "  ..           - Go to parent directory",
            "",
            "Process Manager:",
            "  ↑/↓          - Navigate processes",
            "  k            - Kill selected process",
            "",
            "Press any key to return to dashboard..."
        ]
        
        for line in help_text:
            if y >= height - 2:
                break
            stdscr.addstr(y, 2, line, curses.color_pair(3))
            y += 1
    
    def run(self, stdscr):
        """Main application loop"""
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Headers
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Status
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal text
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Directories
        
        # Initial data refresh
        self.refresh_data()
        
        while self.running:
            try:
                # Clear screen
                stdscr.clear()
                
                # Draw header
                self.draw_header(stdscr)
                
                # Draw current view
                if self.current_view == 'dashboard':
                    self.draw_dashboard(stdscr)
                elif self.current_view == 'processes':
                    self.draw_processes(stdscr)
                elif self.current_view == 'files':
                    self.draw_files(stdscr)
                elif self.current_view == 'help':
                    self.draw_help(stdscr)
                
                # Refresh screen
                stdscr.refresh()
                
                # Handle input
                key = stdscr.getch()
                
                if key == ord('q') or key == ord('Q') or key == 27:  # q, Q, ESC
                    self.running = False
                elif key == ord('h') or key == ord('H'):  # h, H
                    self.current_view = 'help'
                elif key == ord('d') or key == ord('D'):  # d, D
                    self.current_view = 'dashboard'
                elif key == ord('p') or key == ord('P'):  # p, P
                    self.current_view = 'processes'
                elif key == ord('f') or key == ord('F'):  # f, F
                    self.current_view = 'files'
                elif key == ord('r') or key == ord('R'):  # r, R
                    self.refresh_data()
                elif key == ord('c') or key == ord('C'):  # c, C
                    stdscr.clear()
                
                # Auto refresh data
                self.refresh_data()
                
                # Small delay to prevent high CPU usage
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                stdscr.addstr(0, 0, f"Error: {str(e)}", curses.color_pair(5))
                stdscr.refresh()
                time.sleep(2)

def main():
    """Main entry point"""
    print(f"{Colors.HEADER}🐧 Linux System Manager{Colors.ENDC}")
    print(f"{Colors.OKBLUE}Starting system monitoring tool...{Colors.ENDC}")
    print(f"{Colors.WARNING}Press Ctrl+C to exit{Colors.ENDC}")
    print()
    
    try:
        # Check if running on Linux
        if sys.platform != 'linux':
            print(f"{Colors.FAIL}Error: This tool is designed for Linux systems only{Colors.ENDC}")
            sys.exit(1)
        
        # Check required modules
        try:
            import psutil
        except ImportError:
            print(f"{Colors.FAIL}Error: psutil module not found. Install with: pip install psutil{Colors.ENDC}")
            sys.exit(1)
        
        # Create and run application
        app = LinuxSystemManager()
        wrapper(app.run)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Application terminated by user{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Error: {str(e)}{Colors.ENDC}")
        sys.exit(1)
    finally:
        print(f"{Colors.OKGREEN}Goodbye! 👋{Colors.ENDC}")

if __name__ == "__main__":
    main()
