#!/usr/bin/env python3
"""
Linux System Manager - Modern GUI System Management Tool
Author: AI Assistant
Description: A comprehensive Linux system management tool with modern GUI interface
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
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import queue
import signal

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
            return processes[:50]  # Top 50 processes
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

class LinuxGUIManager:
    """Main GUI application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐧 Linux System Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0d1117')
        
        # Data storage
        self.system_data = {}
        self.process_data = []
        self.current_path = Path.home()
        self.file_data = []
        
        # Update thread
        self.update_thread = None
        self.running = True
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.start_update_thread()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle system signals"""
        self.running = False
        self.root.quit()
        sys.exit(0)
    
    def setup_styles(self):
        """Setup modern custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern color palette
        colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a', 
            'bg_tertiary': '#2a2a2a',
            'bg_card': '#1e1e1e',
            'accent': '#00d4ff',
            'accent_hover': '#00b8e6',
            'success': '#00ff88',
            'warning': '#ffb800',
            'error': '#ff4757',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0',
            'text_muted': '#666666',
            'border': '#333333',
            'border_light': '#404040'
        }
        
        # Configure modern styles
        style.configure('Title.TLabel', 
                       font=('Inter', 24, 'bold'),
                       foreground=colors['accent'],
                       background=colors['bg_primary'])
        
        style.configure('Header.TLabel',
                       font=('Inter', 14, 'bold'),
                       foreground=colors['text_primary'],
                       background=colors['bg_primary'])
        
        style.configure('Info.TLabel',
                       font=('Inter', 11),
                       foreground=colors['text_secondary'],
                       background=colors['bg_primary'])
        
        # Modern button styles
        style.configure('Primary.TButton',
                       font=('Inter', 11, 'bold'),
                       foreground=colors['text_primary'],
                       background=colors['accent'],
                       borderwidth=0,
                       relief='flat',
                       padding=(20, 12))
        
        style.map('Primary.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', colors['accent_hover'])])
        
        style.configure('Secondary.TButton',
                       font=('Inter', 10, 'bold'),
                       foreground=colors['text_primary'],
                       background=colors['bg_tertiary'],
                       borderwidth=1,
                       relief='solid',
                       padding=(16, 10))
        
        style.map('Secondary.TButton',
                 background=[('active', colors['bg_card']),
                           ('pressed', colors['bg_card'])])
        
        style.configure('Danger.TButton',
                       font=('Inter', 10, 'bold'),
                       foreground=colors['text_primary'],
                       background=colors['error'],
                       borderwidth=0,
                       relief='flat',
                       padding=(16, 10))
        
        style.map('Danger.TButton',
                 background=[('active', '#ff3742'),
                           ('pressed', '#ff3742')])
        
        # Modern treeview styles
        style.configure('Modern.Treeview',
                       font=('JetBrains Mono', 10),
                       foreground=colors['text_primary'],
                       background=colors['bg_card'],
                       fieldbackground=colors['bg_card'],
                       borderwidth=0,
                       rowheight=32)
        
        style.configure('Modern.Treeview.Heading',
                       font=('Inter', 11, 'bold'),
                       foreground=colors['accent'],
                       background=colors['bg_tertiary'],
                       borderwidth=0,
                       padding=(10, 8))
        
        # Modern progressbar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=colors['accent'],
                       troughcolor=colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=colors['accent'],
                       darkcolor=colors['accent'])
        
        # Modern notebook
        style.configure('Modern.TNotebook',
                       background=colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('Modern.TNotebook.Tab',
                       font=('Inter', 11, 'bold'),
                       foreground=colors['text_secondary'],
                       background=colors['bg_secondary'],
                       borderwidth=0,
                       padding=(20, 12))
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', colors['bg_card']),
                           ('active', colors['bg_tertiary'])],
                 foreground=[('selected', colors['accent']),
                           ('active', colors['text_primary'])])
        
        # Store colors for later use
        self.colors = colors
    
    def create_widgets(self):
        """Create main GUI widgets"""
        # Configure root window
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Main container with modern padding
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Modern title with gradient effect
        title_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        title_frame.pack(fill='x', pady=(0, 30))
        
        title_label = ttk.Label(title_frame, text="🐧 Linux System Manager", style='Title.TLabel')
        title_label.pack()
        
        # Subtitle
        subtitle_label = ttk.Label(title_frame, text="Modern System Management Tool", 
                                 font=('Inter', 12), 
                                 foreground=self.colors['text_secondary'],
                                 background=self.colors['bg_primary'])
        subtitle_label.pack(pady=(5, 0))
        
        # Create modern notebook for tabs
        self.notebook = ttk.Notebook(main_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_processes_tab()
        self.create_files_tab()
        self.create_terminal_tab()
        
        # Modern status bar
        status_frame = tk.Frame(main_frame, bg=self.colors['bg_secondary'], height=40, relief='flat')
        status_frame.pack(fill='x', pady=(20, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("🟢 System Ready")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                             font=('Inter', 10),
                             foreground=self.colors['success'],
                             background=self.colors['bg_secondary'])
        status_bar.pack(side='left', padx=15, pady=10)
        
        # Update time
        self.update_time_var = tk.StringVar()
        self.update_time_var.set("")
        time_label = ttk.Label(status_frame, textvariable=self.update_time_var,
                             font=('Inter', 10),
                             foreground=self.colors['text_muted'],
                             background=self.colors['bg_secondary'])
        time_label.pack(side='right', padx=15, pady=10)
    
    def create_dashboard_tab(self):
        """Create modern dashboard tab"""
        dashboard_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Create scrollable frame
        canvas = tk.Canvas(dashboard_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # System Information
        self.create_system_info_section(scrollable_frame)
        
        # CPU Information
        self.create_cpu_info_section(scrollable_frame)
        
        # Memory Information
        self.create_memory_info_section(scrollable_frame)
        
        # Disk Information
        self.create_disk_info_section(scrollable_frame)
        
        # Network Information
        self.create_network_info_section(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def create_system_info_section(self, parent):
        """Create modern system information section"""
        # Modern card frame
        frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=0)
        frame.pack(fill='x', pady=15, padx=10)
        
        # Add subtle border effect
        border_frame = tk.Frame(frame, bg=self.colors['border'], height=1)
        border_frame.pack(fill='x', pady=(0, 15))
        
        # Header with icon
        header_frame = tk.Frame(frame, bg=self.colors['bg_card'])
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        # Icon
        icon_label = tk.Label(header_frame, text="🖥️", font=('Inter', 20), 
                            bg=self.colors['bg_card'], fg=self.colors['accent'])
        icon_label.pack(side='left')
        
        # Title
        header = ttk.Label(header_frame, text="System Information", style='Header.TLabel')
        header.pack(side='left', padx=(10, 0))
        
        # Info frame with modern grid layout
        info_frame = tk.Frame(frame, bg=self.colors['bg_card'])
        info_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Create grid layout for info
        info_items = [
            ("Hostname", "hostname_label"),
            ("Kernel", "kernel_label"), 
            ("Architecture", "arch_label"),
            ("Uptime", "uptime_label")
        ]
        
        for i, (label_text, var_name) in enumerate(info_items):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            label = ttk.Label(info_frame, text=f"{label_text}:", 
                            font=('Inter', 10, 'bold'),
                            foreground=self.colors['text_secondary'],
                            background=self.colors['bg_card'])
            label.grid(row=row, column=col, sticky='w', padx=(0, 10), pady=5)
            
            # Value
            value_label = ttk.Label(info_frame, text="Loading...", 
                                  font=('JetBrains Mono', 10),
                                  foreground=self.colors['text_primary'],
                                  background=self.colors['bg_card'])
            value_label.grid(row=row, column=col+1, sticky='w', padx=(0, 20), pady=5)
            
            # Store reference
            setattr(self, var_name, value_label)
        
        # Configure grid weights
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)
    
    def create_cpu_info_section(self, parent):
        """Create modern CPU information section"""
        # Modern card frame
        frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat', bd=0)
        frame.pack(fill='x', pady=15, padx=10)
        
        # Add subtle border effect
        border_frame = tk.Frame(frame, bg=self.colors['border'], height=1)
        border_frame.pack(fill='x', pady=(0, 15))
        
        # Header with icon
        header_frame = tk.Frame(frame, bg=self.colors['bg_card'])
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        # Icon
        icon_label = tk.Label(header_frame, text="⚡", font=('Inter', 20), 
                            bg=self.colors['bg_card'], fg=self.colors['warning'])
        icon_label.pack(side='left')
        
        # Title
        header = ttk.Label(header_frame, text="CPU Information", style='Header.TLabel')
        header.pack(side='left', padx=(10, 0))
        
        # Info frame
        info_frame = tk.Frame(frame, bg=self.colors['bg_card'])
        info_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # CPU usage with modern progress bar
        usage_frame = tk.Frame(info_frame, bg=self.colors['bg_card'])
        usage_frame.pack(fill='x', pady=(0, 15))
        
        # Usage label
        self.cpu_usage_label = ttk.Label(usage_frame, text="Usage: Loading...", 
                                       font=('Inter', 11, 'bold'),
                                       foreground=self.colors['text_primary'],
                                       background=self.colors['bg_card'])
        self.cpu_usage_label.pack(anchor='w')
        
        # Modern progress bar
        progress_frame = tk.Frame(usage_frame, bg=self.colors['bg_card'])
        progress_frame.pack(fill='x', pady=(5, 0))
        
        self.cpu_progress = ttk.Progressbar(progress_frame, length=400, mode='determinate', 
                                          style='Modern.Horizontal.TProgressbar')
        self.cpu_progress.pack(side='left', fill='x', expand=True)
        
        # CPU details in grid
        details_frame = tk.Frame(info_frame, bg=self.colors['bg_card'])
        details_frame.pack(fill='x')
        
        # Cores
        cores_label = ttk.Label(details_frame, text="Cores:", 
                              font=('Inter', 10, 'bold'),
                              foreground=self.colors['text_secondary'],
                              background=self.colors['bg_card'])
        cores_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        self.cpu_cores_label = ttk.Label(details_frame, text="Loading...", 
                                       font=('JetBrains Mono', 10),
                                       foreground=self.colors['text_primary'],
                                       background=self.colors['bg_card'])
        self.cpu_cores_label.grid(row=0, column=1, sticky='w', padx=(0, 30), pady=5)
        
        # Frequency
        freq_label = ttk.Label(details_frame, text="Frequency:", 
                             font=('Inter', 10, 'bold'),
                             foreground=self.colors['text_secondary'],
                             background=self.colors['bg_card'])
        freq_label.grid(row=0, column=2, sticky='w', padx=(0, 10), pady=5)
        
        self.cpu_freq_label = ttk.Label(details_frame, text="Loading...", 
                                      font=('JetBrains Mono', 10),
                                      foreground=self.colors['text_primary'],
                                      background=self.colors['bg_card'])
        self.cpu_freq_label.grid(row=0, column=3, sticky='w', pady=5)
    
    def create_memory_info_section(self, parent):
        """Create memory information section"""
        frame = tk.Frame(parent, bg='#161b22', relief='solid', bd=1)
        frame.pack(fill='x', pady=5, padx=5)
        
        # Header
        header = ttk.Label(frame, text="💾 Memory Information", style='Header.TLabel')
        header.pack(anchor='w', padx=10, pady=5)
        
        # Info frame
        info_frame = tk.Frame(frame, bg='#161b22')
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # Memory usage
        self.mem_usage_label = ttk.Label(info_frame, text="Usage: Loading...", style='Info.TLabel')
        self.mem_usage_label.pack(anchor='w')
        
        # Memory progress bar
        self.mem_progress = ttk.Progressbar(info_frame, length=300, mode='determinate')
        self.mem_progress.pack(anchor='w', pady=5)
        
        # Memory details
        self.mem_total_label = ttk.Label(info_frame, text="Total: Loading...", style='Info.TLabel')
        self.mem_total_label.pack(anchor='w')
        
        self.mem_used_label = ttk.Label(info_frame, text="Used: Loading...", style='Info.TLabel')
        self.mem_used_label.pack(anchor='w')
        
        self.mem_available_label = ttk.Label(info_frame, text="Available: Loading...", style='Info.TLabel')
        self.mem_available_label.pack(anchor='w')
    
    def create_disk_info_section(self, parent):
        """Create disk information section"""
        frame = tk.Frame(parent, bg='#161b22', relief='solid', bd=1)
        frame.pack(fill='x', pady=5, padx=5)
        
        # Header
        header = ttk.Label(frame, text="💿 Disk Information", style='Header.TLabel')
        header.pack(anchor='w', padx=10, pady=5)
        
        # Info frame
        info_frame = tk.Frame(frame, bg='#161b22')
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # Disk usage
        self.disk_usage_label = ttk.Label(info_frame, text="Usage: Loading...", style='Info.TLabel')
        self.disk_usage_label.pack(anchor='w')
        
        # Disk progress bar
        self.disk_progress = ttk.Progressbar(info_frame, length=300, mode='determinate')
        self.disk_progress.pack(anchor='w', pady=5)
        
        # Disk details
        self.disk_total_label = ttk.Label(info_frame, text="Total: Loading...", style='Info.TLabel')
        self.disk_total_label.pack(anchor='w')
        
        self.disk_used_label = ttk.Label(info_frame, text="Used: Loading...", style='Info.TLabel')
        self.disk_used_label.pack(anchor='w')
        
        self.disk_free_label = ttk.Label(info_frame, text="Free: Loading...", style='Info.TLabel')
        self.disk_free_label.pack(anchor='w')
    
    def create_network_info_section(self, parent):
        """Create network information section"""
        frame = tk.Frame(parent, bg='#161b22', relief='solid', bd=1)
        frame.pack(fill='x', pady=5, padx=5)
        
        # Header
        header = ttk.Label(frame, text="🌐 Network Information", style='Header.TLabel')
        header.pack(anchor='w', padx=10, pady=5)
        
        # Info frame
        info_frame = tk.Frame(frame, bg='#161b22')
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # Network stats
        self.net_sent_label = ttk.Label(info_frame, text="Bytes Sent: Loading...", style='Info.TLabel')
        self.net_sent_label.pack(anchor='w')
        
        self.net_recv_label = ttk.Label(info_frame, text="Bytes Received: Loading...", style='Info.TLabel')
        self.net_recv_label.pack(anchor='w')
        
        self.net_packets_sent_label = ttk.Label(info_frame, text="Packets Sent: Loading...", style='Info.TLabel')
        self.net_packets_sent_label.pack(anchor='w')
        
        self.net_packets_recv_label = ttk.Label(info_frame, text="Packets Received: Loading...", style='Info.TLabel')
        self.net_packets_recv_label.pack(anchor='w')
    
    def create_processes_tab(self):
        """Create modern processes tab"""
        processes_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(processes_frame, text="🔄 Processes")
        
        # Modern control frame
        control_frame = tk.Frame(processes_frame, bg=self.colors['bg_secondary'], height=60)
        control_frame.pack(fill='x', padx=15, pady=15)
        control_frame.pack_propagate(False)
        
        # Control buttons with modern styling
        button_frame = tk.Frame(control_frame, bg=self.colors['bg_secondary'])
        button_frame.pack(side='left', padx=20, pady=15)
        
        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_processes, style='Primary.TButton')
        refresh_btn.pack(side='left', padx=(0, 10))
        
        self.kill_btn = ttk.Button(button_frame, text="💀 Kill Process", command=self.kill_selected_process, style='Danger.TButton')
        self.kill_btn.pack(side='left', padx=(0, 10))
        
        # Process count label
        self.process_count_label = ttk.Label(control_frame, text="Loading processes...", 
                                           font=('Inter', 10),
                                           foreground=self.colors['text_secondary'],
                                           background=self.colors['bg_secondary'])
        self.process_count_label.pack(side='right', padx=20, pady=15)
        
        # Modern process tree
        columns = ('PID', 'Name', 'CPU%', 'Memory%', 'Status')
        self.process_tree = ttk.Treeview(processes_frame, columns=columns, show='headings', style='Modern.Treeview')
        
        # Configure columns with better widths
        column_widths = {'PID': 80, 'Name': 200, 'CPU%': 80, 'Memory%': 80, 'Status': 100}
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=column_widths[col], anchor='center')
        
        # Scrollbar for process tree
        process_scrollbar = ttk.Scrollbar(processes_frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scrollbar.set)
        
        # Pack process tree with modern spacing
        self.process_tree.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
        process_scrollbar.pack(side="right", fill="y", pady=(0, 15))
    
    def create_files_tab(self):
        """Create modern files tab"""
        files_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(files_frame, text="📁 Files")
        
        # Modern control frame
        control_frame = tk.Frame(files_frame, bg=self.colors['bg_secondary'], height=80)
        control_frame.pack(fill='x', padx=15, pady=15)
        control_frame.pack_propagate(False)
        
        # Path section
        path_frame = tk.Frame(control_frame, bg=self.colors['bg_secondary'])
        path_frame.pack(fill='x', padx=20, pady=(10, 5))
        
        path_label = ttk.Label(path_frame, text="Current Path:", 
                             font=('Inter', 10, 'bold'),
                             foreground=self.colors['text_secondary'],
                             background=self.colors['bg_secondary'])
        path_label.pack(side='left', padx=(0, 10))
        
        self.current_path_var = tk.StringVar()
        self.current_path_var.set(str(self.current_path))
        path_entry = ttk.Entry(path_frame, textvariable=self.current_path_var, width=60,
                             font=('JetBrains Mono', 10))
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Navigation buttons
        button_frame = tk.Frame(control_frame, bg=self.colors['bg_secondary'])
        button_frame.pack(fill='x', padx=20, pady=(5, 10))
        
        up_btn = ttk.Button(button_frame, text="⬆️ Up", command=self.go_up_directory, style='Secondary.TButton')
        up_btn.pack(side='left', padx=(0, 10))
        
        home_btn = ttk.Button(button_frame, text="🏠 Home", command=self.go_home_directory, style='Secondary.TButton')
        home_btn.pack(side='left', padx=(0, 10))
        
        refresh_files_btn = ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_files, style='Primary.TButton')
        refresh_files_btn.pack(side='left', padx=(0, 10))
        
        # File count label
        self.file_count_label = ttk.Label(button_frame, text="Loading files...", 
                                        font=('Inter', 10),
                                        foreground=self.colors['text_secondary'],
                                        background=self.colors['bg_secondary'])
        self.file_count_label.pack(side='right')
        
        # Modern file tree
        file_columns = ('Type', 'Name', 'Size', 'Modified', 'Permissions')
        self.file_tree = ttk.Treeview(files_frame, columns=file_columns, show='headings', style='Modern.Treeview')
        
        # Configure columns with better widths
        file_column_widths = {'Type': 80, 'Name': 300, 'Size': 100, 'Modified': 150, 'Permissions': 100}
        for col in file_columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=file_column_widths[col], anchor='center')
        
        # Scrollbar for file tree
        file_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        
        # Pack file tree with modern spacing
        self.file_tree.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
        file_scrollbar.pack(side="right", fill="y", pady=(0, 15))
        
        # Bind double-click event
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
    
    def create_terminal_tab(self):
        """Create terminal tab"""
        terminal_frame = tk.Frame(self.notebook, bg='#0d1117')
        self.notebook.add(terminal_frame, text="💻 Terminal")
        
        # Control frame
        control_frame = tk.Frame(terminal_frame, bg='#0d1117')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Command entry
        self.command_var = tk.StringVar()
        command_entry = ttk.Entry(control_frame, textvariable=self.command_var, width=50)
        command_entry.pack(side='left', padx=5)
        command_entry.bind('<Return>', self.execute_command)
        
        # Execute button
        execute_btn = ttk.Button(control_frame, text="▶️ Execute", command=self.execute_command, style='Custom.TButton')
        execute_btn.pack(side='left', padx=5)
        
        # Clear button
        clear_btn = ttk.Button(control_frame, text="🗑️ Clear", command=self.clear_terminal, style='Custom.TButton')
        clear_btn.pack(side='left', padx=5)
        
        # Terminal output
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame, 
            bg='#000000', 
            fg='#00ff00', 
            font=('JetBrains Mono', 10),
            wrap=tk.WORD
        )
        self.terminal_output.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Add welcome message
        self.terminal_output.insert(tk.END, "🐧 Linux System Manager Terminal\n")
        self.terminal_output.insert(tk.END, "Type commands and press Enter or click Execute\n")
        self.terminal_output.insert(tk.END, "=" * 50 + "\n\n")
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def update_system_data(self):
        """Update all system data"""
        try:
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
            self.refresh_files()
            
        except Exception as e:
            print(f"Error updating system data: {e}")
    
    def update_dashboard(self):
        """Update dashboard display with modern styling"""
        try:
            # Update time
            self.update_time_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # System info
            if 'system' in self.system_data:
                sys_info = self.system_data['system']
                if 'error' not in sys_info:
                    self.hostname_label.config(text=sys_info.get('hostname', 'N/A'))
                    self.kernel_label.config(text=sys_info.get('kernel', 'N/A'))
                    self.arch_label.config(text=sys_info.get('architecture', 'N/A'))
                    self.uptime_label.config(text=sys_info.get('uptime', 'N/A'))
            
            # CPU info
            if 'cpu' in self.system_data:
                cpu_info = self.system_data['cpu']
                if 'error' not in cpu_info:
                    cpu_usage = cpu_info.get('usage_percent', 0)
                    self.cpu_usage_label.config(text=f"Usage: {cpu_usage:.1f}%")
                    self.cpu_progress['value'] = cpu_usage
                    self.cpu_cores_label.config(text=str(cpu_info.get('core_count', 'N/A')))
                    freq = cpu_info.get('frequency', 0)
                    if freq != 'N/A':
                        self.cpu_freq_label.config(text=f"{freq:.0f} MHz")
                    else:
                        self.cpu_freq_label.config(text="N/A")
            
            # Memory info
            if 'memory' in self.system_data:
                mem_info = self.system_data['memory']
                if 'error' not in mem_info:
                    total = mem_info.get('total', 0)
                    used = mem_info.get('used', 0)
                    available = mem_info.get('available', 0)
                    percentage = mem_info.get('percentage', 0)
                    
                    self.mem_usage_label.config(text=f"Usage: {self.format_bytes(used)} / {self.format_bytes(total)} ({percentage:.1f}%)")
                    self.mem_progress['value'] = percentage
                    self.mem_total_label.config(text=self.format_bytes(total))
                    self.mem_used_label.config(text=self.format_bytes(used))
                    self.mem_available_label.config(text=self.format_bytes(available))
            
            # Disk info
            if 'disk' in self.system_data:
                disk_info = self.system_data['disk']
                if 'error' not in disk_info:
                    total = disk_info.get('total', 0)
                    used = disk_info.get('used', 0)
                    free = disk_info.get('free', 0)
                    percentage = disk_info.get('percentage', 0)
                    
                    self.disk_usage_label.config(text=f"Usage: {self.format_bytes(used)} / {self.format_bytes(total)} ({percentage:.1f}%)")
                    self.disk_progress['value'] = percentage
                    self.disk_total_label.config(text=self.format_bytes(total))
                    self.disk_used_label.config(text=self.format_bytes(used))
                    self.disk_free_label.config(text=self.format_bytes(free))
            
            # Network info
            if 'network' in self.system_data:
                net_info = self.system_data['network']
                if 'error' not in net_info:
                    self.net_sent_label.config(text=self.format_bytes(net_info.get('bytes_sent', 0)))
                    self.net_recv_label.config(text=self.format_bytes(net_info.get('bytes_recv', 0)))
                    self.net_packets_sent_label.config(text=f"{net_info.get('packets_sent', 0):,}")
                    self.net_packets_recv_label.config(text=f"{net_info.get('packets_recv', 0):,}")
        
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def refresh_processes(self):
        """Refresh process list with modern styling"""
        try:
            # Clear existing items
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            
            # Add processes with modern formatting
            process_count = 0
            for proc in self.process_data[:50]:  # Show top 50
                if 'error' not in proc:
                    # Color code based on CPU usage
                    cpu_percent = proc.get('cpu_percent', 0)
                    if cpu_percent > 50:
                        cpu_color = self.colors['error']
                    elif cpu_percent > 20:
                        cpu_color = self.colors['warning']
                    else:
                        cpu_color = self.colors['success']
                    
                    self.process_tree.insert('', 'end', values=(
                        proc.get('pid', ''),
                        proc.get('name', '')[:40],  # Longer name display
                        f"{cpu_percent:.1f}%",
                        f"{proc.get('memory_percent', 0):.1f}%",
                        proc.get('status', '')
                    ))
                    process_count += 1
            
            # Update process count
            self.process_count_label.config(text=f"Showing {process_count} processes")
            
        except Exception as e:
            print(f"Error refreshing processes: {e}")
            self.process_count_label.config(text="Error loading processes")
    
    def kill_selected_process(self):
        """Kill selected process"""
        try:
            selection = self.process_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a process to kill")
                return
            
            item = self.process_tree.item(selection[0])
            pid = item['values'][0]
            name = item['values'][1]
            
            result = messagebox.askyesno("Confirm Kill", f"Are you sure you want to kill process {name} (PID: {pid})?")
            if result:
                os.kill(int(pid), signal.SIGTERM)
                messagebox.showinfo("Success", f"Process {name} (PID: {pid}) killed successfully")
                self.refresh_processes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill process: {e}")
    
    def refresh_files(self):
        """Refresh file list with modern styling"""
        try:
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Get files in current directory
            files = []
            for item in self.current_path.iterdir():
                try:
                    stat = item.stat()
                    files.append({
                        'name': item.name,
                        'is_dir': item.is_dir(),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'permissions': oct(stat.st_mode)[-3:]
                    })
                except (PermissionError, OSError):
                    continue
            
            # Sort: directories first, then files
            files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            # Add files to tree with modern formatting
            file_count = 0
            for file_info in files:
                file_type = "📁 DIR" if file_info['is_dir'] else "📄 FILE"
                size = self.format_bytes(file_info['size']) if not file_info['is_dir'] else "-"
                modified = file_info['modified'].strftime('%Y-%m-%d %H:%M')
                
                self.file_tree.insert('', 'end', values=(
                    file_type,
                    file_info['name'][:50],  # Longer name display
                    size,
                    modified,
                    file_info['permissions']
                ))
                file_count += 1
            
            # Update file count
            self.file_count_label.config(text=f"Showing {file_count} items")
            
        except Exception as e:
            print(f"Error refreshing files: {e}")
            self.file_count_label.config(text="Error loading files")
    
    def on_file_double_click(self, event):
        """Handle file double-click"""
        try:
            selection = self.file_tree.selection()
            if not selection:
                return
            
            item = self.file_tree.item(selection[0])
            file_type = item['values'][0]
            name = item['values'][1]
            
            if "DIR" in file_type:
                # Enter directory
                new_path = self.current_path / name
                if new_path.is_dir():
                    self.current_path = new_path
                    self.current_path_var.set(str(self.current_path))
                    self.refresh_files()
        except Exception as e:
            print(f"Error handling file double-click: {e}")
    
    def go_up_directory(self):
        """Go to parent directory"""
        try:
            parent = self.current_path.parent
            if parent != self.current_path:
                self.current_path = parent
                self.current_path_var.set(str(self.current_path))
                self.refresh_files()
        except Exception as e:
            print(f"Error going up directory: {e}")
    
    def go_home_directory(self):
        """Go to home directory"""
        try:
            self.current_path = Path.home()
            self.current_path_var.set(str(self.current_path))
            self.refresh_files()
        except Exception as e:
            print(f"Error going to home directory: {e}")
    
    def execute_command(self, event=None):
        """Execute terminal command"""
        try:
            command = self.command_var.get().strip()
            if not command:
                return
            
            # Add command to terminal
            self.terminal_output.insert(tk.END, f"$ {command}\n")
            
            # Execute command
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            # Add output to terminal
            if result.stdout:
                self.terminal_output.insert(tk.END, result.stdout)
            if result.stderr:
                self.terminal_output.insert(tk.END, f"Error: {result.stderr}")
            
            self.terminal_output.insert(tk.END, "\n")
            self.terminal_output.see(tk.END)
            
            # Clear command entry
            self.command_var.set("")
            
        except subprocess.TimeoutExpired:
            self.terminal_output.insert(tk.END, "Command timed out\n")
        except Exception as e:
            self.terminal_output.insert(tk.END, f"Error: {e}\n")
        finally:
            self.terminal_output.see(tk.END)
    
    def clear_terminal(self):
        """Clear terminal output"""
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.insert(tk.END, "🐧 Linux System Manager Terminal\n")
        self.terminal_output.insert(tk.END, "Type commands and press Enter or click Execute\n")
        self.terminal_output.insert(tk.END, "=" * 50 + "\n\n")
    
    def start_update_thread(self):
        """Start background update thread"""
        def update_loop():
            while self.running:
                try:
                    self.update_system_data()
                    self.root.after(0, self.update_dashboard)
                    self.root.after(0, self.refresh_processes)
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    print(f"Error in update thread: {e}")
                    time.sleep(5)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def run(self):
        """Run the application"""
        try:
            # Initial update
            self.update_system_data()
            self.update_dashboard()
            self.refresh_processes()
            self.refresh_files()
            
            # Start GUI
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            print(f"Error running application: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        self.root.destroy()

def main():
    """Main entry point"""
    print("🐧 Linux System Manager - GUI Version")
    print("Starting GUI application...")
    
    try:
        # Check if running on Linux
        if sys.platform != 'linux':
            print("❌ Error: This tool is designed for Linux systems only")
            sys.exit(1)
        
        # Check required modules
        try:
            import psutil
        except ImportError:
            print("❌ Error: psutil module not found. Install with: pip install psutil")
            sys.exit(1)
        
        # Create and run application
        app = LinuxGUIManager()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        print("Goodbye! 👋")

if __name__ == "__main__":
    main()
