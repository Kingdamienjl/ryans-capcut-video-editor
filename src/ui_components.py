"""
UI Components for Athena Video Editor
Cyberpunk-themed interface with modern design
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
from pathlib import Path
from typing import List, Dict, Optional, Callable
import webbrowser
import json
from datetime import datetime

# Try to import tkinterdnd2 for drag and drop functionality
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("tkinterdnd2 not available - drag and drop disabled")

class AthenaUI:
    """Main UI controller for the application"""
    
    def __init__(self, root: ctk.CTk, app_controller):
        self.root = root
        self.app = app_controller
        
        # Color scheme - Cyberpunk theme
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a', 
            'accent_cyan': '#00ffff',
            'accent_blue': '#0080ff',
            'accent_green': '#00ff88',
            'accent_purple': '#8b00ff',
            'accent_orange': '#ff8800',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_muted': '#888888',
            'danger': '#ff0040',
            'warning': '#ffaa00',
            'success': '#00ff88'
        }
        
        # UI state
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to process video")
        self.video_info_text = tk.StringVar(value="No video selected")
        
        # Create custom styles
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom styling for the application"""
        # Configure CTk colors
        ctk.set_appearance_mode("dark")
        
        # Custom button style
        self.button_style = {
            'corner_radius': 8,
            'border_width': 1,
            'font': ('Consolas', 12, 'bold')
        }
        
        # Custom frame style
        self.frame_style = {
            'corner_radius': 10,
            'border_width': 1
        }
    
    def create_main_interface(self):
        """Create the main application interface"""
        # Configure main window - only for CTk windows
        if hasattr(self.root, 'configure') and hasattr(self.root, '_fg_color'):
            self.root.configure(fg_color=self.colors['bg_primary'])
        
        # Create main container
        main_container = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['bg_primary'],
            corner_radius=0
        )
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header(main_container)
        
        # Create main content area
        content_frame = ctk.CTkFrame(
            main_container,
            fg_color=self.colors['bg_secondary'],
            **self.frame_style
        )
        content_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create left panel (controls)
        self.create_control_panel(content_frame)
        
        # Create right panel (preview/results)
        self.create_preview_panel(content_frame)
        
        # Create bottom status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create the application header with Athena branding"""
        header_frame = ctk.CTkFrame(
            parent,
            height=80,
            fg_color=self.colors['bg_secondary'],
            **self.frame_style
        )
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Left side - Logo and title
        left_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        left_frame.pack(side='left', fill='y', padx=20, pady=10)
        
        # Athena logo (text-based for now)
        logo_label = ctk.CTkLabel(
            left_frame,
            text="⚡ ATHENA",
            font=('Consolas', 24, 'bold'),
            text_color=self.colors['accent_cyan']
        )
        logo_label.pack(side='left', padx=(0, 15))
        
        # Title and subtitle
        title_frame = ctk.CTkFrame(left_frame, fg_color='transparent')
        title_frame.pack(side='left', fill='y')
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="VIDEO EDITOR",
            font=('Consolas', 18, 'bold'),
            text_color=self.colors['text_primary']
        )
        title_label.pack(anchor='w')
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="AI-Powered Clip Generation for Ryan's Podcast",
            font=('Consolas', 10),
            text_color=self.colors['text_muted']
        )
        subtitle_label.pack(anchor='w')
        
        # Right side - Menu buttons
        right_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        right_frame.pack(side='right', fill='y', padx=20, pady=10)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            right_frame,
            text="⚙ SETTINGS",
            width=100,
            height=30,
            fg_color=self.colors['bg_primary'],
            hover_color=self.colors['accent_purple'],
            border_color=self.colors['accent_purple'],
            corner_radius=8,
            border_width=1,
            font=('Consolas', 12, 'bold'),
            command=self.app.open_settings
        )
        settings_btn.pack(side='right', padx=(10, 0))
        
        # About button
        about_btn = ctk.CTkButton(
            right_frame,
            text="? ABOUT",
            width=100,
            height=30,
            fg_color=self.colors['bg_primary'],
            hover_color=self.colors['accent_green'],
            border_color=self.colors['accent_green'],
            corner_radius=8,
            border_width=1,
            font=('Consolas', 12, 'bold'),
            command=self.app.show_about
        )
        about_btn.pack(side='right')
    
    def create_control_panel(self, parent):
        """Create the left control panel with scrolling"""
        # Create scrollable frame
        self.control_canvas = ctk.CTkScrollableFrame(
            parent,
            width=400,
            fg_color=self.colors['bg_primary'],
            **self.frame_style
        )
        self.control_canvas.pack(side='left', fill='both', expand=True, padx=(10, 5), pady=10)
        
        # Video preview section FIRST (at the top)
        self.create_video_preview_section(self.control_canvas)
        
        # Video selection section
        self.create_video_section(self.control_canvas)
        
        # AI settings section
        self.create_ai_section(self.control_canvas)
        
        # Processing controls
        self.create_processing_section(self.control_canvas)
    
    def create_video_preview_section(self, parent):
        """Create video preview section at the top - now just the header"""
        # Just the section header - preview box will be at bottom
        pass

    def create_video_section(self, parent):
        """Create video selection and info section"""
        # Section header
        video_header = ctk.CTkLabel(
            parent,
            text="📹 VIDEO INPUT",
            font=('Consolas', 14, 'bold'),
            text_color=self.colors['accent_cyan']
        )
        video_header.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Drag and drop area
        self.drop_frame = ctk.CTkFrame(
            parent,
            height=80,
            fg_color=self.colors['bg_secondary'],
            border_color=self.colors['accent_cyan'],
            border_width=2,
            corner_radius=8
        )
        self.drop_frame.pack(fill='x', padx=20, pady=(0, 10))
        self.drop_frame.pack_propagate(False)
        
        # Configure drag and drop
        self.setup_drag_drop(self.drop_frame)
        
        # Drop zone label
        drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="📁 DRAG & DROP VIDEO FILE HERE\n or click SELECT VIDEO FILE below",
            font=('Consolas', 11, 'bold'),
            text_color=self.colors['text_muted'],
            justify='center'
        )
        drop_label.pack(expand=True)
        
        # File selection button
        select_btn = ctk.CTkButton(
            parent,
            text="SELECT VIDEO FILE",
            height=40,
            fg_color=self.colors['accent_cyan'],
            hover_color='#00cccc',
            text_color=self.colors['bg_primary'],
            corner_radius=8,
            border_width=1,
            font=('Consolas', 12, 'bold'),
            command=self.app.select_video_file
        )
        select_btn.pack(fill='x', padx=20, pady=(0, 10))
        
        # Video info display
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=5
        )
        info_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.video_info_label = ctk.CTkLabel(
            info_frame,
            textvariable=self.video_info_text,
            font=('Consolas', 10),
            text_color=self.colors['text_secondary'],
            justify='left'
        )
        self.video_info_label.pack(padx=15, pady=15, anchor='w')
    
    def create_ai_section(self, parent):
        """Create AI settings section"""
        # Section header
        ai_header = ctk.CTkLabel(
            parent,
            text="🧠 AI ANALYSIS MODE",
            font=('Consolas', 14, 'bold'),
            text_color=self.colors['accent_green']
        )
        ai_header.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Settings frame
        settings_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=5
        )
        settings_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Clipping Mode Selection
        mode_label = ctk.CTkLabel(
            settings_frame,
            text="Clipping Mode:",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['text_primary']
        )
        mode_label.pack(anchor='w', padx=15, pady=(15, 5))
        
        # Mode selection frame
        mode_frame = ctk.CTkFrame(settings_frame, fg_color='transparent')
        mode_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Radio button variable
        self.clipping_mode = ctk.StringVar(value="intelligent")
        
        # Intelligent mode (default)
        intelligent_radio = ctk.CTkRadioButton(
            mode_frame,
            text="🎯 Intelligent Analysis",
            variable=self.clipping_mode,
            value="intelligent",
            font=('Consolas', 11),
            text_color=self.colors['text_primary'],
            fg_color=self.colors['accent_cyan'],
            hover_color=self.colors['accent_purple'],
            command=self.on_mode_change
        )
        intelligent_radio.pack(anchor='w', pady=2)
        
        intelligent_desc = ctk.CTkLabel(
            mode_frame,
            text="   AI decides the best clips based on content analysis",
            font=('Consolas', 9),
            text_color=self.colors['text_muted']
        )
        intelligent_desc.pack(anchor='w', padx=(20, 0))
        
        # Interval mode
        interval_radio = ctk.CTkRadioButton(
            mode_frame,
            text="⏱️ Fixed Intervals",
            variable=self.clipping_mode,
            value="interval",
            font=('Consolas', 11),
            text_color=self.colors['text_primary'],
            fg_color=self.colors['accent_cyan'],
            hover_color=self.colors['accent_purple'],
            command=self.on_mode_change
        )
        interval_radio.pack(anchor='w', pady=(10, 2))
        
        interval_desc = ctk.CTkLabel(
            mode_frame,
            text="   Auto-clip at regular time intervals",
            font=('Consolas', 9),
            text_color=self.colors['text_muted']
        )
        interval_desc.pack(anchor='w', padx=(20, 0))
        
        # Hybrid mode
        hybrid_radio = ctk.CTkRadioButton(
            mode_frame,
            text="🔄 Hybrid Mode",
            variable=self.clipping_mode,
            value="hybrid",
            font=('Consolas', 11),
            text_color=self.colors['text_primary'],
            fg_color=self.colors['accent_cyan'],
            hover_color=self.colors['accent_purple'],
            command=self.on_mode_change
        )
        hybrid_radio.pack(anchor='w', pady=(10, 2))
        
        hybrid_desc = ctk.CTkLabel(
            mode_frame,
            text="   Combine AI analysis with interval-based backup clips",
            font=('Consolas', 9),
            text_color=self.colors['text_muted']
        )
        hybrid_desc.pack(anchor='w', padx=(20, 0), pady=(0, 10))
        
        # Dynamic settings container
        self.dynamic_settings_frame = ctk.CTkFrame(settings_frame, fg_color='transparent')
        self.dynamic_settings_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Initialize with intelligent mode settings
        self.create_intelligent_settings()
    
    def on_mode_change(self):
        """Handle clipping mode change"""
        # Clear existing dynamic settings
        for widget in self.dynamic_settings_frame.winfo_children():
            widget.destroy()

        mode = self.clipping_mode.get()

        if mode == "intelligent":
            self.create_intelligent_settings()
        elif mode == "interval":
            self.create_interval_settings()
        elif mode == "hybrid":
            self.create_hybrid_settings()
    
    def update_sensitivity_label(self, value):
        """Update the sensitivity label with current value"""
        if hasattr(self, 'sens_label'):
            self.sens_label.configure(text=f"AI Sensitivity: {value:.1f}")
    
    def update_clips_label(self, value):
        """Update the clips label with current value"""
        if hasattr(self, 'clips_label'):
            self.clips_label.configure(text=f"Max Number of Clips: {int(value)}")
    
    def create_intelligent_settings(self):
        """Create settings for intelligent mode"""
        # Sensitivity setting
        # AI Sensitivity setting
        sens_frame = ctk.CTkFrame(self.dynamic_settings_frame, fg_color='transparent')
        sens_frame.pack(fill='x', pady=(5, 10))
        
        self.sens_label = ctk.CTkLabel(
            sens_frame,
            text="AI Sensitivity: 0.6",
            font=('Consolas', 10),
            text_color=self.colors['text_secondary']
        )
        self.sens_label.pack(anchor='w', pady=(0, 2))
        
        self.sensitivity_slider = ctk.CTkSlider(
            sens_frame,
            from_=0.1,
            to=1.0,
            number_of_steps=9,
            progress_color=self.colors['accent_green'],
            button_color=self.colors['accent_green'],
            button_hover_color='#00cc66',
            command=self.update_sensitivity_label
        )
        self.sensitivity_slider.set(0.6)
        self.sensitivity_slider.pack(fill='x')
        
        # Max clips setting
        clips_frame = ctk.CTkFrame(self.dynamic_settings_frame, fg_color='transparent')
        clips_frame.pack(fill='x', pady=(0, 5))
        
        self.clips_label = ctk.CTkLabel(
            clips_frame,
            text="Max Number of Clips: 8",
            font=('Consolas', 10),
            text_color=self.colors['text_secondary']
        )
        self.clips_label.pack(anchor='w', pady=(0, 2))
        
        self.clips_slider = ctk.CTkSlider(
            clips_frame,
            from_=3,
            to=15,
            number_of_steps=12,
            progress_color=self.colors['accent_green'],
            button_color=self.colors['accent_green'],
            button_hover_color='#00cc66',
            command=self.update_clips_label
        )
        self.clips_slider.set(8)
        self.clips_slider.pack(fill='x')
    
    def create_interval_settings(self):
        """Create settings for interval mode"""
        # Interval duration
        interval_label = ctk.CTkLabel(
            self.dynamic_settings_frame,
            text="Clip Interval (seconds):",
            font=('Consolas', 10),
            text_color=self.colors['text_secondary']
        )
        interval_label.pack(anchor='w', pady=(5, 2))
        
        self.interval_slider = ctk.CTkSlider(
            self.dynamic_settings_frame,
            from_=30,
            to=300,
            number_of_steps=27,
            progress_color=self.colors['accent_orange'],
            button_color=self.colors['accent_orange'],
            button_hover_color='#ff9933'
        )
        self.interval_slider.set(60)
        self.interval_slider.pack(fill='x', pady=(0, 10))
        
        # Clip duration
        duration_label = ctk.CTkLabel(
            self.dynamic_settings_frame,
            text="Clip Duration (seconds):",
            font=('Consolas', 10),
            text_color=self.colors['text_secondary']
        )
        duration_label.pack(anchor='w', pady=(5, 2))
        
        self.duration_slider = ctk.CTkSlider(
            self.dynamic_settings_frame,
            from_=10,
            to=120,
            number_of_steps=11,
            progress_color=self.colors['accent_orange'],
            button_color=self.colors['accent_orange'],
            button_hover_color='#ff9933'
        )
        self.duration_slider.set(30)
        self.duration_slider.pack(fill='x', pady=(0, 5))
    
    def create_hybrid_settings(self):
        """Create settings for hybrid mode"""
        # AI portion
        ai_label = ctk.CTkLabel(
            self.dynamic_settings_frame,
            text="AI-Generated Clips:",
            font=('Consolas', 10),
            text_color=self.colors['text_secondary']
        )
        ai_label.pack(anchor='w', pady=(5, 2))
        
        self.ai_clips_slider = ctk.CTkSlider(
            self.dynamic_settings_frame,
            from_=2,
            to=10,
            number_of_steps=8,
            progress_color=self.colors['accent_purple'],
            button_color=self.colors['accent_purple'],
            button_hover_color='#9933ff'
        )
        self.ai_clips_slider.set(5)
        self.ai_clips_slider.pack(fill='x', pady=(0, 10))
        
        # Interval portion
        interval_label = ctk.CTkLabel(
            self.dynamic_settings_frame,
            text="Interval Backup Clips:",
            font=('Consolas', 10),
            text_color=self.colors['text_secondary']
        )
        interval_label.pack(anchor='w', pady=(5, 2))
        
        self.backup_clips_slider = ctk.CTkSlider(
            self.dynamic_settings_frame,
            from_=1,
            to=8,
            number_of_steps=7,
            progress_color=self.colors['accent_purple'],
            button_color=self.colors['accent_purple'],
            button_hover_color='#9933ff'
        )
        self.backup_clips_slider.set(3)
        self.backup_clips_slider.pack(fill='x', pady=(0, 5))
    
    def create_processing_section(self, parent):
        """Create processing controls section"""
        # Section header
        process_header = ctk.CTkLabel(
            parent,
            text="⚡ PROCESSING",
            font=('Consolas', 14, 'bold'),
            text_color=self.colors['accent_purple']
        )
        process_header.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Start processing button
        self.process_btn = ctk.CTkButton(
            parent,
            text="🚀 START AI ANALYSIS",
            height=50,
            fg_color=self.colors['accent_purple'],
            hover_color='#6600cc',
            text_color=self.colors['text_primary'],
            corner_radius=8,
            border_width=1,
            font=('Consolas', 14, 'bold'),
            command=self.app.start_processing
        )
        self.process_btn.pack(fill='x', padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            parent,
            height=20,
            progress_color=self.colors['accent_purple'],
            fg_color=self.colors['bg_secondary']
        )
        self.progress_bar.pack(fill='x', padx=20, pady=(0, 10))
        self.progress_bar.set(0)
    
    def create_preview_panel(self, parent):
        """Create the right preview/results panel"""
        results_panel_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_primary'],
            **self.frame_style
        )
        results_panel_frame.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)
        
        # Video Preview header (moved from top section)
        preview_header = ctk.CTkLabel(
            results_panel_frame,
            text="🎬 VIDEO PREVIEW",
            font=('Consolas', 14, 'bold'),
            text_color=self.colors['accent_purple']
        )
        preview_header.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Video preview frame (initially hidden)
        self.preview_frame = ctk.CTkFrame(
            results_panel_frame,
            height=200,
            fg_color=self.colors['bg_secondary'],
            corner_radius=5
        )
        # Don't pack initially - will be shown when video is selected
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Video Preview",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['accent_green']
        )
        self.preview_label.pack(pady=10)
        
        # Video preview label (this is what update_video_preview references)
        self.video_preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="🎬 Select a video to see preview",
            font=('Consolas', 10),
            text_color=self.colors['text_muted'],
            justify='center',
            cursor='hand2'
        )
        self.video_preview_label.pack(expand=True)
        
        # Bind click event to show preview window
        self.video_preview_label.bind("<Button-1>", lambda e: self.show_video_preview_window())
        
        # Analysis Results header
        analysis_header = ctk.CTkLabel(
            results_panel_frame,
            text="📊 ANALYSIS RESULTS",
            font=('Consolas', 14, 'bold'),
            text_color=self.colors['accent_cyan']
        )
        analysis_header.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Scrollable results area
        self.results_frame = ctk.CTkScrollableFrame(
            results_panel_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=5
        )
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Initial message
        initial_label = ctk.CTkLabel(
            self.results_frame,
            text="Select a video and start processing to see results here.\n\nAthena will analyze your video and identify the best clips automatically.",
            font=('Consolas', 12),
            text_color=self.colors['text_muted'],
            justify='center'
        )
        initial_label.pack(expand=True, pady=50)
    
    def create_status_bar(self, parent):
        """Create bottom status bar"""
        status_frame = ctk.CTkFrame(
            parent,
            height=40,
            fg_color=self.colors['bg_secondary'],
            corner_radius=5
        )
        status_frame.pack(fill='x', pady=(10, 0))
        status_frame.pack_propagate(False)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=('Consolas', 10),
            text_color=self.colors['text_secondary']
        )
        self.status_label.pack(side='left', padx=20, pady=10)
        
        # Version info
        version_label = ctk.CTkLabel(
            status_frame,
            text="Athena Video Editor v1.0",
            font=('Consolas', 10),
            text_color=self.colors['text_muted']
        )
        version_label.pack(side='right', padx=20, pady=10)
    
    def update_video_info(self, video_path: str):
        """Update video information display"""
        try:
            # Get file info
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            file_name = os.path.basename(video_path)
            
            info_text = f"📁 {file_name}\n💾 Size: {file_size:.1f} MB\n📍 Path: {video_path}"
            self.video_info_text.set(info_text)
            
        except Exception as e:
            self.video_info_text.set(f"Error reading file: {str(e)}")
    
    def update_progress(self, value: float):
        """Update progress bar"""
        self.progress_bar.set(value / 100.0)
        self.root.update_idletasks()
    
    def update_status(self, message: str):
        """Update status message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_results(self, clips: List[str]):
        """Display processing results"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not clips:
            no_results_label = ctk.CTkLabel(
                self.results_frame,
                text="No clips were generated.\nTry adjusting the AI settings and processing again.",
                font=('Consolas', 12),
                text_color=self.colors['warning']
            )
            no_results_label.pack(pady=20)
            return
        
        # Results header
        results_header = ctk.CTkLabel(
            self.results_frame,
            text=f"✅ Generated {len(clips)} clips successfully!",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['success']
        )
        results_header.pack(pady=(10, 20))
        
        # Display each clip
        for i, clip_path in enumerate(clips):
            self.create_clip_result_item(clip_path, i + 1)
    
    def create_clip_result_item(self, clip_path: str, clip_number: int):
        """Create a result item for each generated clip"""
        # Clip container
        clip_frame = ctk.CTkFrame(
            self.results_frame,
            fg_color=self.colors['bg_primary'],
            corner_radius=8,
            border_width=1,
            border_color=self.colors['accent_cyan']
        )
        clip_frame.pack(fill='x', padx=10, pady=5)
        
        # Clip info
        clip_name = os.path.basename(clip_path)
        file_size = os.path.getsize(clip_path) / (1024 * 1024)  # MB
        
        info_label = ctk.CTkLabel(
            clip_frame,
            text=f"🎬 Clip {clip_number}: {clip_name}\n💾 Size: {file_size:.1f} MB",
            font=('Consolas', 10),
            text_color=self.colors['text_secondary'],
            justify='left'
        )
        info_label.pack(side='left', padx=15, pady=10)
        
        # Action buttons
        button_frame = ctk.CTkFrame(clip_frame, fg_color='transparent')
        button_frame.pack(side='right', padx=15, pady=10)
        
        # Open folder button
        open_btn = ctk.CTkButton(
            button_frame,
            text="📁",
            width=40,
            height=30,
            fg_color=self.colors['accent_green'],
            hover_color='#00cc66',
            command=lambda: self.open_file_location(clip_path),
            font=('Consolas', 12)
        )
        open_btn.pack(side='right', padx=(5, 0))
        
        # Play button (placeholder)
        play_btn = ctk.CTkButton(
            button_frame,
            text="▶",
            width=40,
            height=30,
            fg_color=self.colors['accent_cyan'],
            hover_color='#00cccc',
            command=lambda: self.play_clip(clip_path),
            font=('Consolas', 12)
        )
        play_btn.pack(side='right')
    
    def open_file_location(self, file_path: str):
        """Open file location in explorer"""
        try:
            import subprocess
            subprocess.run(['explorer', '/select,', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file location: {str(e)}")
    
    def play_clip(self, file_path: str):
        """Play clip with default media player"""
        try:
            import subprocess
            subprocess.run(['start', file_path], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not play clip: {str(e)}")
    
    def show_settings_dialog(self):
        """Show advanced settings configuration dialog"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Athena Advanced Settings")
        settings_window.geometry("700x800")
        settings_window.configure(fg_color=self.colors['bg_primary'])
        settings_window.resizable(False, False)
        
        # Make it modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Fix transparency issue by ensuring proper cleanup
        def on_close():
            try:
                settings_window.grab_release()
                settings_window.destroy()
                # Force main window to refresh and become fully opaque
                self.root.update_idletasks()
                self.root.focus_force()
                self.root.lift()
                self.root.attributes('-alpha', 1.0)  # Ensure full opacity
                self.root.configure(fg_color=self.colors['bg_primary'])
                # Additional fix: refresh the entire UI
                self.root.update()
                # Force redraw of all widgets
                for widget in self.root.winfo_children():
                    widget.update_idletasks()
            except Exception as e:
                print(f"Error closing settings: {e}")
        
        settings_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Main container with scrollable frame
        main_frame = ctk.CTkScrollableFrame(
            settings_window,
            fg_color=self.colors['bg_primary']
        )
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        header_frame.pack(fill='x', pady=(0, 20))
        
        settings_label = ctk.CTkLabel(
            header_frame,
            text="⚙ ADVANCED CONFIGURATION",
            font=('Consolas', 18, 'bold'),
            text_color=self.colors['accent_cyan']
        )
        settings_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Fine-tune Athena's AI analysis parameters",
            font=('Consolas', 11),
            text_color=self.colors['text_muted']
        )
        subtitle_label.pack(pady=(5, 0))
        
        # AI Analysis Settings
        self.create_settings_section(main_frame, "🧠 AI ANALYSIS", [
            ("Highlight Sensitivity", "highlight_sensitivity", 0.1, 1.0, 0.6, "Higher values find more clips"),
            ("Scene Change Threshold", "scene_threshold", 0.1, 0.9, 0.3, "Lower values detect more scene changes"),
            ("Minimum Clip Duration", "min_duration", 3, 30, 5, "Shortest allowed clip length (seconds)"),
            ("Maximum Clip Duration", "max_duration", 30, 300, 120, "Longest allowed clip length (seconds)"),
            ("Maximum Clips", "max_clips", 1, 50, 10, "Maximum number of clips to generate")
        ])
        
        # OpenAI API Configuration
        api_frame = self.create_section_frame(main_frame, "🔑 OPENAI API CONFIGURATION")
        
        # API Key input
        api_key_frame = ctk.CTkFrame(api_frame, fg_color='transparent')
        api_key_frame.pack(fill='x', padx=15, pady=10)
        
        api_key_label = ctk.CTkLabel(
            api_key_frame,
            text="OpenAI API Key:",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['text_primary']
        )
        api_key_label.pack(anchor='w', pady=(0, 5))
        
        self.api_key_entry = ctk.CTkEntry(
            api_key_frame,
            placeholder_text="sk-... (Enter your OpenAI API key)",
            font=('Consolas', 11),
            show="*",
            height=35
        )
        self.api_key_entry.pack(fill='x', pady=(0, 10))
        
        # API Guide button
        guide_btn = ctk.CTkButton(
            api_key_frame,
            text="📖 HOW TO GET API KEY",
            height=30,
            fg_color=self.colors['accent_cyan'],
            hover_color='#00cccc',
            font=('Consolas', 10, 'bold'),
            command=self.show_api_guide
        )
        guide_btn.pack(anchor='w')
        
        # Social Media Upload Settings
        social_frame = self.create_section_frame(main_frame, "📱 SOCIAL MEDIA UPLOAD")
        
        # Platform selection checkboxes
        platform_frame = ctk.CTkFrame(social_frame, fg_color='transparent')
        platform_frame.pack(fill='x', padx=15, pady=10)
        
        platform_label = ctk.CTkLabel(
            platform_frame,
            text="Auto-Upload Platforms:",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['text_primary']
        )
        platform_label.pack(anchor='w', pady=(0, 10))
        
        self.create_checkbox_setting(platform_frame, "📺 YouTube Shorts", "upload_youtube", False)
        self.create_checkbox_setting(platform_frame, "📱 TikTok", "upload_tiktok", False)
        self.create_checkbox_setting(platform_frame, "📸 Instagram Reels", "upload_instagram", False)
        self.create_checkbox_setting(platform_frame, "🐦 Twitter/X", "upload_twitter", False)
        self.create_checkbox_setting(platform_frame, "📘 Facebook", "upload_facebook", False)
        
        # Upload settings
        upload_settings_frame = ctk.CTkFrame(social_frame, fg_color='transparent')
        upload_settings_frame.pack(fill='x', padx=15, pady=10)
        
        upload_label = ctk.CTkLabel(
            upload_settings_frame,
            text="Upload Settings:",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['text_primary']
        )
        upload_label.pack(anchor='w', pady=(0, 5))
        
        self.create_checkbox_setting(upload_settings_frame, "Auto-generate titles", "auto_titles", True)
        self.create_checkbox_setting(upload_settings_frame, "Auto-generate descriptions", "auto_descriptions", True)
        self.create_checkbox_setting(upload_settings_frame, "Add hashtags", "auto_hashtags", True)
        self.create_checkbox_setting(upload_settings_frame, "Schedule uploads", "schedule_uploads", False)
        
        # Default tags entry
        tags_frame = ctk.CTkFrame(upload_settings_frame, fg_color='transparent')
        tags_frame.pack(fill='x', pady=(10, 0))
        
        tags_label = ctk.CTkLabel(
            tags_frame,
            text="Default Tags/Hashtags:",
            font=('Consolas', 11),
            text_color=self.colors['text_secondary']
        )
        tags_label.pack(anchor='w', pady=(0, 5))
        
        self.default_tags_entry = ctk.CTkEntry(
            tags_frame,
            placeholder_text="#podcast #ai #clips #shorts",
            font=('Consolas', 11),
            height=30
        )
        self.default_tags_entry.pack(fill='x')
        
        # Content Filtering
        self.create_settings_section(main_frame, "🎯 CONTENT FILTERING", [
            ("Keyword Weight", "keyword_weight", 0.0, 3.0, 1.0, "Importance of highlight keywords"),
            ("Question Weight", "question_weight", 0.0, 3.0, 2.0, "Boost segments with questions"),
            ("Emotion Weight", "emotion_weight", 0.0, 3.0, 1.0, "Boost emotional content (caps, exclamation)"),
            ("Length Preference", "length_preference", 0.0, 2.0, 1.0, "Prefer medium-length segments")
        ])
        
        # Video Processing
        self.create_settings_section(main_frame, "🎬 VIDEO PROCESSING", [
            ("Output Quality", "output_quality", 1, 10, 8, "1=Lowest, 10=Highest quality"),
            ("Frame Rate", "output_fps", 15, 60, 30, "Output video frame rate"),
            ("Audio Bitrate", "audio_bitrate", 64, 320, 192, "Audio quality (kbps)")
        ])
        
        # Advanced Options
        advanced_frame = self.create_section_frame(main_frame, "🔧 ADVANCED OPTIONS")
        
        # Checkboxes for advanced features
        self.create_checkbox_setting(advanced_frame, "Enable GPU Acceleration", "use_gpu", True)
        self.create_checkbox_setting(advanced_frame, "Preserve Original Audio", "preserve_audio", True)
        self.create_checkbox_setting(advanced_frame, "Generate Thumbnails", "generate_thumbnails", True)
        self.create_checkbox_setting(advanced_frame, "Auto-Open Output Folder", "auto_open_output", False)
        self.create_checkbox_setting(advanced_frame, "Save Processing Log", "save_log", True)
        
        # Advanced Tools Section
        self.create_settings_section(main_frame, "🔧 ADVANCED TOOLS", [
            ("Batch Processing Threads", "batch_threads", 1, 16, 4, "Number of parallel processing threads"),
            ("Memory Buffer Size (MB)", "memory_buffer", 128, 2048, 512, "Memory allocated for video processing"),
            ("Cache Size (MB)", "cache_size", 64, 1024, 256, "Temporary cache for analysis data"),
            ("Preview Quality", "preview_quality", 0.1, 1.0, 0.5, "Quality of preview thumbnails (lower = faster)")
        ])
        
        # Performance Optimization
        perf_frame = self.create_section_frame(main_frame, "⚡ PERFORMANCE OPTIMIZATION")
        
        self.create_checkbox_setting(perf_frame, "Enable GPU Acceleration", "use_gpu", True)
        self.create_checkbox_setting(perf_frame, "Enable Multi-threading", "use_multithread", True)
        self.create_checkbox_setting(perf_frame, "Low Memory Mode", "low_memory", False)
        self.create_checkbox_setting(perf_frame, "Fast Preview Mode", "fast_preview", False)
        self.create_checkbox_setting(perf_frame, "Hardware Decoding", "hw_decode", True)
        
        # Export Tools
        export_tools_frame = self.create_section_frame(main_frame, "📤 EXPORT TOOLS")
        
        self.create_checkbox_setting(export_tools_frame, "Auto-generate Thumbnails", "auto_thumbnails", True)
        self.create_checkbox_setting(export_tools_frame, "Create Metadata Files", "create_metadata", False)
        self.create_checkbox_setting(export_tools_frame, "Generate Subtitle Files", "generate_subs", False)
        self.create_checkbox_setting(export_tools_frame, "Batch Export Mode", "batch_export", False)
        self.create_checkbox_setting(export_tools_frame, "Auto-open Output Folder", "auto_open_folder", True)
        
        # Quality presets dropdown
        quality_frame = ctk.CTkFrame(export_tools_frame, fg_color='transparent')
        quality_frame.pack(fill='x', padx=15, pady=10)
        
        quality_label = ctk.CTkLabel(
            quality_frame,
            text="Export Quality Preset:",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['text_primary']
        )
        quality_label.pack(anchor='w', pady=(0, 5))
        
        self.quality_preset = ctk.StringVar(value="High")
        quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            values=["Ultra (Lossless)", "High (Recommended)", "Medium (Balanced)", "Low (Fast)", "Custom"],
            variable=self.quality_preset,
            font=('Consolas', 11),
            fg_color=self.colors['bg_primary'],
            button_color=self.colors['accent_cyan'],
            button_hover_color='#00cccc'
        )
        quality_menu.pack(fill='x', pady=(0, 10))
        
        # Debug & Analysis Tools
        debug_frame = self.create_section_frame(main_frame, "🔍 DEBUG & ANALYSIS")
        
        self.create_checkbox_setting(debug_frame, "Verbose Logging", "verbose_log", False)
        self.create_checkbox_setting(debug_frame, "Save Analysis Report", "save_report", True)
        self.create_checkbox_setting(debug_frame, "Export Processing Timeline", "export_timeline", False)
        self.create_checkbox_setting(debug_frame, "Generate Heatmaps", "generate_heatmaps", False)
        self.create_checkbox_setting(debug_frame, "Preview Mode (No Export)", "preview_only", False)
        
        # Log level dropdown
        log_frame = ctk.CTkFrame(debug_frame, fg_color='transparent')
        log_frame.pack(fill='x', padx=15, pady=10)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Log Level:",
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['text_primary']
        )
        log_label.pack(anchor='w', pady=(0, 5))
        
        self.log_level = ctk.StringVar(value="INFO")
        log_menu = ctk.CTkOptionMenu(
            log_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.log_level,
            font=('Consolas', 11),
            fg_color=self.colors['bg_primary'],
            button_color=self.colors['accent_green'],
            button_hover_color='#00cc66'
        )
        log_menu.pack(fill='x', pady=(0, 10))
        
        # Export/Import Settings
        io_frame = self.create_section_frame(main_frame, "💾 SETTINGS MANAGEMENT")
        
        io_buttons_frame = ctk.CTkFrame(io_frame, fg_color='transparent')
        io_buttons_frame.pack(fill='x', pady=10)
        
        export_btn = ctk.CTkButton(
            io_buttons_frame,
            text="📤 EXPORT SETTINGS",
            width=150,
            height=35,
            fg_color=self.colors['accent_green'],
            hover_color='#00cc66',
            font=('Consolas', 11, 'bold'),
            command=self.export_settings
        )
        export_btn.pack(side='left', padx=(0, 10))
        
        import_btn = ctk.CTkButton(
            io_buttons_frame,
            text="📥 IMPORT SETTINGS",
            width=150,
            height=35,
            fg_color=self.colors['accent_orange'],
            hover_color='#ff9933',
            font=('Consolas', 11, 'bold'),
            command=self.import_settings
        )
        import_btn.pack(side='left', padx=(0, 10))
        
        reset_btn = ctk.CTkButton(
            io_buttons_frame,
            text="🔄 RESET TO DEFAULTS",
            width=150,
            height=35,
            fg_color=self.colors['warning'],
            hover_color='#ff6666',
            font=('Consolas', 11, 'bold'),
            command=self.reset_settings
        )
        reset_btn.pack(side='left')
        
        # Backup/Restore section
        backup_frame = ctk.CTkFrame(io_frame, fg_color='transparent')
        backup_frame.pack(fill='x', pady=(10, 0))
        
        backup_label = ctk.CTkLabel(
            backup_frame,
            text="Configuration Backup:",
            font=('Consolas', 11, 'bold'),
            text_color=self.colors['text_secondary']
        )
        backup_label.pack(anchor='w', pady=(0, 5))
        
        backup_buttons_frame = ctk.CTkFrame(backup_frame, fg_color='transparent')
        backup_buttons_frame.pack(fill='x')
        
        backup_btn = ctk.CTkButton(
            backup_buttons_frame,
            text="💾 CREATE BACKUP",
            width=140,
            height=30,
            fg_color=self.colors['accent_purple'],
            hover_color='#6600cc',
            font=('Consolas', 10, 'bold'),
            command=self.create_backup
        )
        backup_btn.pack(side='left', padx=(0, 10))
        
        restore_btn = ctk.CTkButton(
            backup_buttons_frame,
            text="🔄 RESTORE BACKUP",
            width=140,
            height=30,
            fg_color=self.colors['accent_purple'],
            hover_color='#6600cc',
            font=('Consolas', 10, 'bold'),
            command=self.restore_backup
        )
        restore_btn.pack(side='left')
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(settings_window, fg_color='transparent')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Apply and Close buttons
        apply_btn = ctk.CTkButton(
            button_frame,
            text="✅ APPLY SETTINGS",
            height=40,
            fg_color=self.colors['success'],
            hover_color='#00cc44',
            font=('Consolas', 12, 'bold'),
            command=lambda: self.apply_settings(settings_window, on_close)
        )
        apply_btn.pack(side='right', padx=(10, 0))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="❌ CANCEL",
            height=40,
            fg_color=self.colors['accent_purple'],
            hover_color='#6600cc',
            font=('Consolas', 12, 'bold'),
            command=on_close
        )
        close_btn.pack(side='right')
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (800 // 2)
        settings_window.geometry(f"700x800+{x}+{y}")
    
    def create_settings_section(self, parent, title, settings):
        """Create a section with multiple slider settings"""
        section_frame = self.create_section_frame(parent, title)
        
        for setting in settings:
            name, key, min_val, max_val, default_val, description = setting
            self.create_slider_setting(section_frame, name, key, min_val, max_val, default_val, description)
    
    def create_section_frame(self, parent, title):
        """Create a collapsible section frame"""
        section_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=10,
            border_width=1,
            border_color=self.colors['accent_cyan']
        )
        section_frame.pack(fill='x', pady=(0, 15))
        
        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=('Consolas', 14, 'bold'),
            text_color=self.colors['accent_cyan']
        )
        title_label.pack(anchor='w')
        
        return section_frame
    
    def create_slider_setting(self, parent, name, key, min_val, max_val, default_val, description):
        """Create a slider setting with label and description"""
        setting_frame = ctk.CTkFrame(parent, fg_color='transparent')
        setting_frame.pack(fill='x', padx=15, pady=5)
        
        # Setting name and value
        name_frame = ctk.CTkFrame(setting_frame, fg_color='transparent')
        name_frame.pack(fill='x')
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=name,
            font=('Consolas', 12, 'bold'),
            text_color=self.colors['text_primary']
        )
        name_label.pack(side='left')
        
        value_var = ctk.StringVar(value=str(default_val))
        value_label = ctk.CTkLabel(
            name_frame,
            textvariable=value_var,
            font=('Consolas', 12),
            text_color=self.colors['accent_cyan']
        )
        value_label.pack(side='right')
        
        # Slider
        slider = ctk.CTkSlider(
            setting_frame,
            from_=min_val,
            to=max_val,
            number_of_steps=100,
            fg_color=self.colors['bg_primary'],
            progress_color=self.colors['accent_cyan'],
            button_color=self.colors['accent_purple'],
            button_hover_color=self.colors['accent_cyan'],
            command=lambda val: value_var.set(f"{val:.2f}" if isinstance(val, float) else str(int(val)))
        )
        slider.set(default_val)
        slider.pack(fill='x', pady=(5, 0))
        
        # Description
        desc_label = ctk.CTkLabel(
            setting_frame,
            text=description,
            font=('Consolas', 10),
            text_color=self.colors['text_muted']
        )
        desc_label.pack(anchor='w', pady=(2, 0))
        
        # Store reference for later access
        if not hasattr(self, 'settings_widgets'):
            self.settings_widgets = {}
        self.settings_widgets[key] = {'slider': slider, 'var': value_var}
    
    def create_checkbox_setting(self, parent, name, key, default_value):
        """Create a checkbox setting"""
        setting_frame = ctk.CTkFrame(parent, fg_color='transparent')
        setting_frame.pack(fill='x', padx=15, pady=5)
        
        checkbox_var = ctk.BooleanVar(value=default_value)
        checkbox = ctk.CTkCheckBox(
            setting_frame,
            text=name,
            variable=checkbox_var,
            font=('Consolas', 12),
            text_color=self.colors['text_primary'],
            fg_color=self.colors['accent_cyan'],
            hover_color=self.colors['accent_purple'],
            checkmark_color=self.colors['bg_primary']
        )
        checkbox.pack(anchor='w')
        
        # Store reference
        if not hasattr(self, 'settings_widgets'):
            self.settings_widgets = {}
        self.settings_widgets[key] = {'checkbox': checkbox, 'var': checkbox_var}
    
    def apply_settings(self, window, close_callback=None):
        """Apply the current settings"""
        try:
            # Here you would save settings to config file
            # For now, just show confirmation
            self.update_status("Settings applied successfully!")
            if close_callback:
                close_callback()
            else:
                window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
    
    def export_settings(self):
        """Export current settings to file"""
        try:
            from tkinter import filedialog
            import json
            
            file_path = filedialog.asksaveasfilename(
                title="Export Settings",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                settings_data = {
                    "athena_version": "1.0",
                    "export_date": "2024-01-01",  # You'd use actual date
                    "settings": {
                        # Collect all current settings values
                        "highlight_sensitivity": 0.6,
                        "scene_threshold": 0.3,
                        # ... other settings
                    }
                }
                
                with open(file_path, 'w') as f:
                    json.dump(settings_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Settings exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export settings: {str(e)}")
    
    def import_settings(self):
        """Import settings from file"""
        try:
            from tkinter import filedialog
            import json
            
            file_path = filedialog.askopenfilename(
                title="Import Settings",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    settings_data = json.load(f)
                
                # Apply imported settings to widgets
                # Implementation would update all slider/checkbox values
                
                messagebox.showinfo("Success", f"Settings imported from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import settings: {str(e)}")
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        result = messagebox.askyesno(
            "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?\n\nThis cannot be undone."
        )
        
        if result:
            try:
                # Reset all widgets to default values
                if hasattr(self, 'settings_widgets'):
                    # Implementation would reset all sliders and checkboxes
                    pass
                
                messagebox.showinfo("Success", "Settings reset to defaults!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
    
    def create_backup(self):
        """Create a backup of current settings"""
        try:
            import json
            from datetime import datetime
            from tkinter import filedialog
            
            # Get current settings
            settings = self.get_all_settings()
            
            # Add timestamp
            settings['backup_timestamp'] = datetime.now().isoformat()
            settings['backup_version'] = "1.0"
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                title="Save Settings Backup",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialname=f"athena_settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                # Show success message
                success_dialog = ctk.CTkToplevel()
                success_dialog.title("Backup Created")
                success_dialog.geometry("300x150")
                success_dialog.configure(fg_color=self.colors['bg_primary'])
                
                success_label = ctk.CTkLabel(
                    success_dialog,
                    text="✅ Settings backup created successfully!",
                    font=('Consolas', 12),
                    text_color=self.colors['accent_green']
                )
                success_label.pack(pady=50)
                
                ok_btn = ctk.CTkButton(
                    success_dialog,
                    text="OK",
                    command=success_dialog.destroy,
                    fg_color=self.colors['accent_green']
                )
                ok_btn.pack()
                
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def restore_backup(self):
        """Restore settings from backup"""
        try:
            import json
            from tkinter import filedialog, messagebox
            
            # Ask user for backup file
            filename = filedialog.askopenfilename(
                title="Select Settings Backup",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    settings = json.load(f)
                
                # Confirm restore
                if messagebox.askyesno("Restore Settings", 
                                     "This will replace all current settings. Continue?"):
                    self.apply_all_settings(settings)
                    
                    # Show success message
                    success_dialog = ctk.CTkToplevel()
                    success_dialog.title("Settings Restored")
                    success_dialog.geometry("300x150")
                    success_dialog.configure(fg_color=self.colors['bg_primary'])
                    
                    success_label = ctk.CTkLabel(
                        success_dialog,
                        text="✅ Settings restored successfully!",
                        font=('Consolas', 12),
                        text_color=self.colors['accent_green']
                    )
                    success_label.pack(pady=50)
                    
                    ok_btn = ctk.CTkButton(
                        success_dialog,
                        text="OK",
                        command=success_dialog.destroy,
                        fg_color=self.colors['accent_green']
                    )
                    ok_btn.pack()
                    
        except Exception as e:
            print(f"Error restoring backup: {e}")
    
    def get_all_settings(self):
        """Get all current settings as a dictionary"""
        settings = {}
        
        # Get clipping mode
        if hasattr(self, 'clipping_mode'):
            settings['clipping_mode'] = self.clipping_mode.get()
        
        # Get slider values
        sliders = ['sensitivity_slider', 'clips_slider', 'interval_slider', 'duration_slider', 
                  'ai_clips_slider', 'backup_clips_slider', 'thread_slider']
        for slider_name in sliders:
            if hasattr(self, slider_name):
                settings[slider_name] = getattr(self, slider_name).get()
        
        # Get checkbox values
        checkboxes = ['gpu_var', 'parallel_var', 'memory_opt_var', 'auto_export_var', 
                     'thumbnails_var', 'metadata_var', 'verbose_var', 'save_analysis_var', 'preview_var']
        for checkbox_name in checkboxes:
            if hasattr(self, checkbox_name):
                settings[checkbox_name] = getattr(self, checkbox_name).get()
        
        # Get dropdown values
        if hasattr(self, 'quality_var'):
            settings['quality_preset'] = self.quality_var.get()
        if hasattr(self, 'log_level'):
            settings['log_level'] = self.log_level.get()
            
        return settings
    
    def setup_drag_drop(self, widget):
        """Setup drag and drop functionality for video files"""
        if not DRAG_DROP_AVAILABLE:
            print("Drag and drop not available - tkinterdnd2 not installed")
            return
            
        def on_drop(event):
            files = event.data.split()
            if files:
                file_path = files[0].strip('{}')  # Remove curly braces if present
                if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm')):
                    self.app.select_video_file(file_path)
                else:
                    messagebox.showerror("Invalid File", "Please select a valid video file.")
        
        def on_drag_enter(event):
            widget.configure(fg_color=self.colors['accent_blue'])
            return event.action
        
        def on_drag_leave(event):
            widget.configure(fg_color=self.colors['bg_secondary'])
            return event.action
        
        try:
            # Setup drag and drop
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', on_drop)
            widget.dnd_bind('<<DragEnter>>', on_drag_enter)
            widget.dnd_bind('<<DragLeave>>', on_drag_leave)
        except Exception as e:
            print(f"Error setting up drag and drop: {e}")
    
    def show_api_guide(self):
        """Show guide for obtaining OpenAI API key"""
        guide_dialog = ctk.CTkToplevel()
        guide_dialog.title("OpenAI API Key Guide")
        guide_dialog.geometry("500x400")
        guide_dialog.configure(fg_color=self.colors['bg_primary'])
        
        # Make dialog modal
        guide_dialog.transient(self.root)
        guide_dialog.grab_set()
        
        # Title
        title_label = ctk.CTkLabel(
            guide_dialog,
            text="🔑 How to Get Your OpenAI API Key",
            font=('Consolas', 16, 'bold'),
            text_color=self.colors['accent_blue']
        )
        title_label.pack(pady=20)
        
        # Instructions frame
        instructions_frame = ctk.CTkFrame(guide_dialog, fg_color=self.colors['bg_secondary'])
        instructions_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        instructions_text = """
Step 1: Go to OpenAI's website
• Visit: https://platform.openai.com

Step 2: Create an account or sign in
• Click "Sign up" if you don't have an account
• Or "Log in" if you already have one

Step 3: Navigate to API Keys
• Click on your profile (top right)
• Select "View API keys" from the dropdown

Step 4: Create a new API key
• Click "Create new secret key"
• Give it a name (e.g., "Athena Video Editor")
• Copy the key immediately (you won't see it again!)

Step 5: Add billing information
• Go to "Billing" in your account settings
• Add a payment method
• Set usage limits if desired

⚠️ Important Notes:
• Keep your API key secret and secure
• Never share it publicly or commit it to code
• Monitor your usage to avoid unexpected charges
• Free tier includes $5 in credits for new users
        """
        
        instructions_label = ctk.CTkLabel(
            instructions_frame,
            text=instructions_text,
            font=('Consolas', 11),
            text_color=self.colors['text_primary'],
            justify="left",
            anchor="nw"
        )
        instructions_label.pack(padx=15, pady=15, fill="both", expand=True)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(guide_dialog, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        # Open website button
        def open_openai():
            import webbrowser
            webbrowser.open("https://platform.openai.com")
        
        open_btn = ctk.CTkButton(
            buttons_frame,
            text="🌐 Open OpenAI Platform",
            command=open_openai,
            fg_color=self.colors['accent_green'],
            hover_color=self.colors['accent_blue']
        )
        open_btn.pack(side="left", padx=10)
        
        # Close button
        close_btn = ctk.CTkButton(
            buttons_frame,
            text="Close",
            command=guide_dialog.destroy,
            fg_color=self.colors['bg_secondary'],
            hover_color=self.colors['accent_blue']
        )
        close_btn.pack(side="left", padx=10)
    
    def update_video_preview(self, video_path):
        """Update the video preview with thumbnail and create preview window"""
        try:
            # Show the preview frame when video is selected (only the top one)
            if hasattr(self, 'preview_frame'):
                self.preview_frame.pack(fill='x', padx=20, pady=(0, 10))
            
            if hasattr(self, 'video_preview_label'):
                # Try to generate a thumbnail
                try:
                    import cv2
                    import numpy as np
                    from PIL import Image, ImageTk
                    
                    # Capture first frame
                    cap = cv2.VideoCapture(video_path)
                    ret, frame = cap.read()
                    cap.release()
                    
                    if ret:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Resize to fit preview area (200x150)
                        height, width = frame_rgb.shape[:2]
                        aspect_ratio = width / height
                        
                        if aspect_ratio > 200/150:  # Wider than preview area
                            new_width = 200
                            new_height = int(200 / aspect_ratio)
                        else:  # Taller than preview area
                            new_height = 150
                            new_width = int(150 * aspect_ratio)
                        
                        frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
                        
                        # Convert to PIL Image and then to PhotoImage
                        pil_image = Image.fromarray(frame_resized)
                        photo = ImageTk.PhotoImage(pil_image)
                        
                        # Update label
                        self.video_preview_label.configure(image=photo, text="")
                        self.video_preview_label.image = photo  # Keep a reference
                        
                        # Add click handler to open full preview
                        self.video_preview_label.bind("<Button-1>", lambda e: self.show_video_preview_window(video_path))
                        
                    else:
                        self.video_preview_label.configure(
                            image="",
                            text="📹 Preview\nUnavailable",
                            text_color=self.colors['text_secondary']
                        )
                        
                except Exception as e:
                    print(f"Error generating thumbnail: {e}")
                    # Fallback to text
                    self.video_preview_label.configure(
                        image="",
                        text="📹 Video\nSelected\n(Click to preview)",
                        text_color=self.colors['accent_green']
                    )
                    self.video_preview_label.bind("<Button-1>", lambda e: self.show_video_preview_window(video_path))
                    
        except Exception as e:
            print(f"Error updating video preview: {e}")
    
    def show_video_preview_window(self, video_path):
        """Show an enhanced video preview window with processing options"""
        try:
            preview_window = ctk.CTkToplevel()
            preview_window.title("Video Preview & Processing")
            preview_window.geometry("1000x700")
            preview_window.configure(fg_color=self.colors['bg_primary'])
            
            # Make window modal
            preview_window.transient(self.root)
            preview_window.grab_set()
            
            # Main container with scrollable content
            main_container = ctk.CTkScrollableFrame(
                preview_window,
                fg_color=self.colors['bg_primary']
            )
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Header
            header_label = ctk.CTkLabel(
                main_container,
                text="📹 VIDEO PREVIEW & PROCESSING",
                font=('Consolas', 18, 'bold'),
                text_color=self.colors['accent_cyan']
            )
            header_label.pack(pady=(0, 20))
            
            # Video info frame
            info_frame = ctk.CTkFrame(main_container, fg_color=self.colors['bg_secondary'])
            info_frame.pack(fill='x', pady=(0, 20))
            
            # Get video info
            try:
                import cv2
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                duration_min = int(duration // 60)
                duration_sec = int(duration % 60)
                size_mb = os.path.getsize(video_path) / (1024 * 1024)
                
                info_text = f"""📁 File: {os.path.basename(video_path)}
⏱️ Duration: {duration_min}:{duration_sec:02d}
📐 Resolution: {width}x{height}
🎬 FPS: {fps:.1f}
💾 Size: {size_mb:.1f} MB"""
                
            except Exception as e:
                info_text = f"📁 {os.path.basename(video_path)}\nError reading video info: {str(e)}"
            
            info_label = ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=('Consolas', 12),
                text_color=self.colors['text_primary'],
                justify='left'
            )
            info_label.pack(padx=15, pady=10)
            
            # Preview frame with thumbnail
            preview_frame = ctk.CTkFrame(main_container, fg_color=self.colors['bg_secondary'])
            preview_frame.pack(fill='x', pady=(0, 20))
            
            preview_label = ctk.CTkLabel(
                preview_frame,
                text="🎬 Loading video preview...",
                font=('Consolas', 14),
                text_color=self.colors['text_muted']
            )
            preview_label.pack(expand=True, pady=40)
            
            # Try to load thumbnail
            try:
                import cv2
                import numpy as np
                from PIL import Image, ImageTk
                
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # Resize frame for preview
                    height, width = frame.shape[:2]
                    max_width, max_height = 600, 400
                    
                    if width > max_width or height > max_height:
                        scale = min(max_width/width, max_height/height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        frame_resized = cv2.resize(frame, (new_width, new_height))
                    else:
                        frame_resized = frame
                    
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(pil_image)
                    
                    preview_label.configure(image=photo, text="")
                    preview_label.image = photo  # Keep reference
                    
            except Exception as e:
                preview_label.configure(text=f"❌ Could not load preview: {str(e)}")
            
            # Processing options frame
            processing_frame = ctk.CTkFrame(main_container, fg_color=self.colors['bg_secondary'])
            processing_frame.pack(fill='x', pady=(0, 20))
            
            processing_header = ctk.CTkLabel(
                processing_frame,
                text="⚙️ PROCESSING OPTIONS",
                font=('Consolas', 14, 'bold'),
                text_color=self.colors['accent_green']
            )
            processing_header.pack(pady=(15, 10))
            
            # Quick processing buttons
            quick_buttons_frame = ctk.CTkFrame(processing_frame, fg_color='transparent')
            quick_buttons_frame.pack(fill='x', padx=15, pady=(0, 15))
            
            # Analyze video button
            analyze_btn = ctk.CTkButton(
                quick_buttons_frame,
                text="🔍 Analyze Video",
                command=lambda: self.analyze_video_preview(video_path),
                fg_color=self.colors['accent_green'],
                hover_color=self.colors['accent_cyan'],
                font=('Consolas', 12, 'bold'),
                height=40
            )
            analyze_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
            
            # Process full video button
            process_btn = ctk.CTkButton(
                quick_buttons_frame,
                text="⚡ Process Full Video",
                command=lambda: self.process_full_video(video_path, preview_window),
                fg_color=self.colors['accent_orange'],
                hover_color=self.colors['danger'],
                font=('Consolas', 12, 'bold'),
                height=40
            )
            process_btn.pack(side='left', fill='x', expand=True)
            
            # Processing status
            self.processing_status_var = tk.StringVar(value="Ready to process")
            status_label = ctk.CTkLabel(
                processing_frame,
                textvariable=self.processing_status_var,
                font=('Consolas', 11),
                text_color=self.colors['text_muted']
            )
            status_label.pack(pady=(0, 15))
            
            # Bottom buttons frame
            buttons_frame = ctk.CTkFrame(main_container, fg_color='transparent')
            buttons_frame.pack(fill='x', pady=(20, 0))
            
            # Close button
            close_btn = ctk.CTkButton(
                buttons_frame,
                text="❌ Close Preview",
                command=preview_window.destroy,
                fg_color=self.colors['accent_blue'],
                hover_color=self.colors['accent_purple'],
                font=('Consolas', 12, 'bold')
            )
            close_btn.pack(side='right', padx=10)
            
            # Open in explorer button
            def open_in_explorer():
                import subprocess
                subprocess.run(['explorer', '/select,', video_path.replace('/', '\\')])
            
            explorer_btn = ctk.CTkButton(
                buttons_frame,
                text="📁 Show in Explorer",
                command=open_in_explorer,
                fg_color=self.colors['accent_green'],
                hover_color=self.colors['accent_cyan'],
                font=('Consolas', 12, 'bold')
            )
            explorer_btn.pack(side='right', padx=10)
            
            # Video info button
            info_btn = ctk.CTkButton(
                buttons_frame,
                text="ℹ️ Video Details",
                command=lambda: self.show_video_details(video_path),
                fg_color=self.colors['bg_primary'],
                hover_color=self.colors['accent_purple'],
                border_color=self.colors['accent_purple'],
                border_width=1,
                font=('Consolas', 12, 'bold')
            )
            info_btn.pack(side='right', padx=10)
            
        except Exception as e:
            print(f"Error showing video preview: {e}")
            messagebox.showerror("Preview Error", f"Could not show video preview:\n{str(e)}")
    
    def analyze_video_preview(self, video_path):
        """Analyze video and show basic information"""
        try:
            self.processing_status_var.set("Analyzing video...")
            
            # Get detailed video information
            try:
                import cv2
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                video_info = {
                    'duration': duration,
                    'fps': fps,
                    'frame_count': frame_count,
                    'width': width,
                    'height': height,
                    'size_mb': os.path.getsize(video_path) / (1024 * 1024)
                }
            except Exception as e:
                video_info = {
                    'duration': 0,
                    'fps': 0,
                    'frame_count': 0,
                    'width': 0,
                    'height': 0,
                    'size_mb': os.path.getsize(video_path) / (1024 * 1024) if os.path.exists(video_path) else 0
                }
            
            # Create analysis window
            analysis_window = ctk.CTkToplevel()
            analysis_window.title("Video Analysis")
            analysis_window.geometry("600x500")
            analysis_window.configure(fg_color=self.colors['bg_primary'])
            analysis_window.transient(self.root)
            
            # Analysis content
            content_frame = ctk.CTkScrollableFrame(analysis_window, fg_color=self.colors['bg_primary'])
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Header
            header = ctk.CTkLabel(
                content_frame,
                text="📊 VIDEO ANALYSIS RESULTS",
                font=('Consolas', 16, 'bold'),
                text_color=self.colors['accent_cyan']
            )
            header.pack(pady=(0, 20))
            
            # Basic info
            basic_info = f"""📁 File: {os.path.basename(video_path)}
⏱️ Duration: {video_info['duration']:.1f} seconds
📐 Resolution: {video_info['width']}x{video_info['height']}
🎬 FPS: {video_info['fps']:.1f}
🎞️ Total Frames: {video_info['frame_count']}
💾 Size: {video_info['size_mb']:.1f} MB"""
            
            info_frame = ctk.CTkFrame(content_frame, fg_color=self.colors['bg_secondary'])
            info_frame.pack(fill='x', pady=(0, 15))
            
            info_label = ctk.CTkLabel(
                info_frame,
                text=basic_info,
                font=('Consolas', 12),
                text_color=self.colors['text_primary'],
                justify='left'
            )
            info_label.pack(padx=15, pady=15)
            
            # Processing capabilities
            capabilities_frame = ctk.CTkFrame(content_frame, fg_color=self.colors['bg_secondary'])
            capabilities_frame.pack(fill='x', pady=(0, 15))
            
            cap_header = ctk.CTkLabel(
                capabilities_frame,
                text="⚙️ PROCESSING CAPABILITIES",
                font=('Consolas', 14, 'bold'),
                text_color=self.colors['accent_green']
            )
            cap_header.pack(pady=(15, 10))
            
            # Check available processing methods
            methods = []
            if self.app.video_processor._check_ffmpeg():
                methods.append("✅ FFmpeg (System) - Best quality")
            else:
                methods.append("❌ FFmpeg (System) - Not available")
                
            try:
                import ffmpeg
                methods.append("✅ FFmpeg-Python - Good quality")
            except ImportError:
                methods.append("❌ FFmpeg-Python - Not installed")
                
            try:
                from moviepy.editor import VideoFileClip
                methods.append("✅ MoviePy - Good compatibility")
            except ImportError:
                methods.append("❌ MoviePy - Not installed")
                
            try:
                import cv2
                methods.append("✅ OpenCV - Basic processing")
            except ImportError:
                methods.append("❌ OpenCV - Not available")
            
            methods_text = "\n".join(methods)
            
            methods_label = ctk.CTkLabel(
                capabilities_frame,
                text=methods_text,
                font=('Consolas', 11),
                text_color=self.colors['text_primary'],
                justify='left'
            )
            methods_label.pack(padx=15, pady=(0, 15))
            
            # Close button
            close_btn = ctk.CTkButton(
                content_frame,
                text="Close Analysis",
                command=analysis_window.destroy,
                fg_color=self.colors['accent_blue'],
                hover_color=self.colors['accent_purple']
            )
            close_btn.pack(pady=20)
            
            self.processing_status_var.set("✅ Analysis complete")
            
        except Exception as e:
            self.processing_status_var.set(f"❌ Analysis failed: {str(e)}")
            messagebox.showerror("Analysis Error", f"Could not analyze video:\n{str(e)}")
    
    def process_full_video(self, video_path, parent_window):
        """Process the full video using AI analysis"""
        try:
            self.processing_status_var.set("Processing full video...")
            parent_window.update()
            
            # This would normally call the full AI processing pipeline
            # For now, we'll create a simple processing demo
            
            result = messagebox.askyesno(
                "Full Video Processing",
                "This will process the entire video using AI analysis.\n\n"
                "This may take several minutes depending on video length.\n\n"
                "Continue with processing?"
            )
            
            if result:
                # Call the main processing function
                self.app.process_video()
                parent_window.destroy()
            else:
                self.processing_status_var.set("Processing cancelled")
                
        except Exception as e:
            self.processing_status_var.set(f"❌ Processing failed: {str(e)}")
            messagebox.showerror("Processing Error", f"Could not process video:\n{str(e)}")
    
    def show_video_details(self, video_path):
        """Show detailed video information"""
        try:
            details_window = ctk.CTkToplevel()
            details_window.title("Video Details")
            details_window.geometry("500x400")
            details_window.configure(fg_color=self.colors['bg_primary'])
            details_window.transient(self.root)
            
            content_frame = ctk.CTkScrollableFrame(details_window, fg_color=self.colors['bg_primary'])
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Get file stats
            file_stats = os.stat(video_path)
            file_size = file_stats.st_size
            modified_time = datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            details_text = f"""📁 FILE INFORMATION
Path: {video_path}
Name: {os.path.basename(video_path)}
Directory: {os.path.dirname(video_path)}
Size: {file_size / (1024*1024):.2f} MB ({file_size:,} bytes)
Modified: {modified_time}

🎬 VIDEO PROPERTIES"""
            
            try:
                import cv2
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                details_text += f"""
Duration: {duration:.2f} seconds
Frame Rate: {fps:.2f} fps
Resolution: {width} x {height}
Total Frames: {frame_count}
Aspect Ratio: {width/height:.2f}:1"""
            except Exception as e:
                details_text += f"\nError reading video properties: {str(e)}"
            
            details_label = ctk.CTkLabel(
                content_frame,
                text=details_text,
                font=('Consolas', 11),
                text_color=self.colors['text_primary'],
                justify='left'
            )
            details_label.pack(pady=20)
            
            close_btn = ctk.CTkButton(
                content_frame,
                text="Close",
                command=details_window.destroy,
                fg_color=self.colors['accent_blue']
            )
            close_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Details Error", f"Could not show video details:\n{str(e)}")
    
    def apply_all_settings(self, settings):
        """Apply settings from dictionary"""
        # Apply clipping mode
        if 'clipping_mode' in settings and hasattr(self, 'clipping_mode'):
            self.clipping_mode.set(settings['clipping_mode'])
            self.on_mode_change()
        
        # Apply slider values
        sliders = ['sensitivity_slider', 'clips_slider', 'interval_slider', 'duration_slider', 
                  'ai_clips_slider', 'backup_clips_slider', 'thread_slider']
        for slider_name in sliders:
            if slider_name in settings and hasattr(self, slider_name):
                getattr(self, slider_name).set(settings[slider_name])
        
        # Apply checkbox values
        checkboxes = ['gpu_var', 'parallel_var', 'memory_opt_var', 'auto_export_var', 
                     'thumbnails_var', 'metadata_var', 'verbose_var', 'save_analysis_var', 'preview_var']
        for checkbox_name in checkboxes:
            if checkbox_name in settings and hasattr(self, checkbox_name):
                getattr(self, checkbox_name).set(settings[checkbox_name])
        
        # Apply dropdown values
        if 'quality_preset' in settings and hasattr(self, 'quality_var'):
            self.quality_var.set(settings['quality_preset'])
        if 'log_level' in settings and hasattr(self, 'log_level'):
            self.log_level.set(settings['log_level'])
    
    def get_current_settings(self):
        """Get current settings for processing"""
        settings = {
            'mode': self.clipping_mode.get() if hasattr(self, 'clipping_mode') else 'intelligent',
            'max_clips': int(self.clips_slider.get()) if hasattr(self, 'clips_slider') else 8,
            'gpu_enabled': self.gpu_var.get() if hasattr(self, 'gpu_var') else True,
            'parallel_processing': self.parallel_var.get() if hasattr(self, 'parallel_var') else True,
            'auto_export': self.auto_export_var.get() if hasattr(self, 'auto_export_var') else True,
            'generate_thumbnails': self.thumbnails_var.get() if hasattr(self, 'thumbnails_var') else True,
            'create_metadata': self.metadata_var.get() if hasattr(self, 'metadata_var') else False,
            'verbose_logging': self.verbose_var.get() if hasattr(self, 'verbose_var') else False,
            'preview_only': self.preview_var.get() if hasattr(self, 'preview_var') else False
        }
        
        # Mode-specific settings
        mode = settings['mode']
        if mode == 'intelligent':
            settings['sensitivity'] = self.sensitivity_slider.get() if hasattr(self, 'sensitivity_slider') else 0.6
        elif mode == 'interval':
            settings['interval'] = int(self.interval_slider.get()) if hasattr(self, 'interval_slider') else 60
            settings['clip_duration'] = int(self.duration_slider.get()) if hasattr(self, 'duration_slider') else 30
        elif mode == 'hybrid':
            settings['ai_clips'] = int(self.ai_clips_slider.get()) if hasattr(self, 'ai_clips_slider') else 5
            settings['backup_clips'] = int(self.backup_clips_slider.get()) if hasattr(self, 'backup_clips_slider') else 3
        
        return settings
    
    def save_api_key(self, api_key_entry):
        """Save OpenAI API key"""
        try:
            api_key = api_key_entry.get().strip()
            if api_key:
                # Store API key securely (in a real app, use proper encryption)
                import os
                config_dir = os.path.expanduser("~/.athena_video_editor")
                os.makedirs(config_dir, exist_ok=True)
                
                with open(os.path.join(config_dir, "api_key.txt"), "w") as f:
                    f.write(api_key)
                
                self.update_status("API key saved successfully!")
            else:
                self.update_status("Please enter a valid API key")
        except Exception as e:
            self.update_status(f"Error saving API key: {str(e)}")
    
    def test_api_key(self, api_key_entry):
        """Test OpenAI API key"""
        try:
            api_key = api_key_entry.get().strip()
            if not api_key:
                self.update_status("Please enter an API key first")
                return
            
            # Simple test - check if key format is valid
            if api_key.startswith("sk-") and len(api_key) > 20:
                self.update_status("API key format appears valid ✓")
                # In a real implementation, you'd make a test API call here
            else:
                self.update_status("Invalid API key format")
        except Exception as e:
            self.update_status(f"Error testing API key: {str(e)}")
    
    def save_social_settings(self):
        """Save social media settings"""
        try:
            # Collect social media platform settings
            platforms = {}
            if hasattr(self, 'youtube_var'):
                platforms['youtube'] = self.youtube_var.get()
            if hasattr(self, 'tiktok_var'):
                platforms['tiktok'] = self.tiktok_var.get()
            if hasattr(self, 'instagram_var'):
                platforms['instagram'] = self.instagram_var.get()
            if hasattr(self, 'twitter_var'):
                platforms['twitter'] = self.twitter_var.get()
            if hasattr(self, 'facebook_var'):
                platforms['facebook'] = self.facebook_var.get()
            
            # Save settings
            import os, json
            config_dir = os.path.expanduser("~/.athena_video_editor")
            os.makedirs(config_dir, exist_ok=True)
            
            with open(os.path.join(config_dir, "social_settings.json"), "w") as f:
                json.dump(platforms, f, indent=2)
            
            self.update_status("Social media settings saved!")
        except Exception as e:
            self.update_status(f"Error saving social settings: {str(e)}")
    
    def test_social_upload(self):
        """Test social media upload functionality and show setup dialog"""
        try:
            # Import social media manager
            from .social_media_manager import SocialMediaManager
            
            # Create social media manager instance
            social_manager = SocialMediaManager()
            
            # Show social media setup dialog
            self.show_social_media_setup(social_manager)
            
        except Exception as e:
            messagebox.showerror("Social Media Error", f"Error initializing social media: {str(e)}")
    
    def show_social_media_setup(self, social_manager):
        """Show social media platform setup and login dialog"""
        try:
            setup_window = ctk.CTkToplevel()
            setup_window.title("Social Media Setup")
            setup_window.geometry("900x700")
            setup_window.configure(fg_color=self.colors['bg_primary'])
            
            # Make window modal
            setup_window.transient(self.root)
            setup_window.grab_set()
            
            # Handle window close
            def on_close():
                try:
                    setup_window.grab_release()
                    setup_window.destroy()
                    self.root.focus_force()
                except Exception as e:
                    print(f"Error closing social setup: {e}")
            
            setup_window.protocol("WM_DELETE_WINDOW", on_close)
            
            # Main container
            main_frame = ctk.CTkScrollableFrame(
                setup_window,
                fg_color=self.colors['bg_primary']
            )
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Header
            header_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
            header_frame.pack(fill='x', pady=(0, 20))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="📱 SOCIAL MEDIA SETUP",
                font=('Consolas', 20, 'bold'),
                text_color=self.colors['accent_cyan']
            )
            title_label.pack()
            
            subtitle_label = ctk.CTkLabel(
                header_frame,
                text="Configure your social media accounts for automatic uploads",
                font=('Consolas', 12),
                text_color=self.colors['text_muted']
            )
            subtitle_label.pack(pady=(5, 0))
            
            # Platform sections
            platforms = [
                {
                    'name': 'YouTube',
                    'icon': '📺',
                    'color': self.colors['accent_red'],
                    'key': 'youtube',
                    'fields': ['API Key', 'Channel ID'],
                    'description': 'Upload to YouTube Shorts automatically'
                },
                {
                    'name': 'TikTok',
                    'icon': '📱',
                    'color': self.colors['accent_purple'],
                    'key': 'tiktok',
                    'fields': ['Access Token', 'User ID'],
                    'description': 'Share clips directly to TikTok'
                },
                {
                    'name': 'Instagram',
                    'icon': '📸',
                    'color': self.colors['accent_orange'],
                    'key': 'instagram',
                    'fields': ['Access Token', 'User ID'],
                    'description': 'Post to Instagram Reels'
                },
                {
                    'name': 'Twitter/X',
                    'icon': '🐦',
                    'color': self.colors['accent_blue'],
                    'key': 'twitter',
                    'fields': ['API Key', 'API Secret', 'Access Token', 'Access Secret'],
                    'description': 'Tweet your video clips'
                }
            ]
            
            self.platform_entries = {}
            
            for platform in platforms:
                # Platform frame
                platform_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_secondary'])
                platform_frame.pack(fill='x', pady=10)
                
                # Platform header
                platform_header = ctk.CTkFrame(platform_frame, fg_color='transparent')
                platform_header.pack(fill='x', padx=15, pady=(15, 10))
                
                platform_title = ctk.CTkLabel(
                    platform_header,
                    text=f"{platform['icon']} {platform['name']}",
                    font=('Consolas', 16, 'bold'),
                    text_color=platform['color']
                )
                platform_title.pack(side='left')
                
                # Status indicator
                status_label = ctk.CTkLabel(
                    platform_header,
                    text="🔴 Not Connected",
                    font=('Consolas', 10),
                    text_color=self.colors['text_muted']
                )
                status_label.pack(side='right')
                
                # Description
                desc_label = ctk.CTkLabel(
                    platform_frame,
                    text=platform['description'],
                    font=('Consolas', 11),
                    text_color=self.colors['text_secondary']
                )
                desc_label.pack(padx=15, pady=(0, 10))
                
                # Input fields
                fields_frame = ctk.CTkFrame(platform_frame, fg_color='transparent')
                fields_frame.pack(fill='x', padx=15, pady=(0, 15))
                
                self.platform_entries[platform['key']] = {}
                
                for field in platform['fields']:
                    field_frame = ctk.CTkFrame(fields_frame, fg_color='transparent')
                    field_frame.pack(fill='x', pady=5)
                    
                    field_label = ctk.CTkLabel(
                        field_frame,
                        text=f"{field}:",
                        font=('Consolas', 11),
                        text_color=self.colors['text_primary'],
                        width=120
                    )
                    field_label.pack(side='left', padx=(0, 10))
                    
                    field_entry = ctk.CTkEntry(
                        field_frame,
                        placeholder_text=f"Enter your {field.lower()}",
                        font=('Consolas', 10),
                        show="*" if "secret" in field.lower() or "token" in field.lower() else None
                    )
                    field_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
                    
                    self.platform_entries[platform['key']][field.lower().replace(' ', '_')] = field_entry
                    
                    # Test button
                    test_btn = ctk.CTkButton(
                        field_frame,
                        text="Test",
                        width=60,
                        height=28,
                        fg_color=platform['color'],
                        font=('Consolas', 9),
                        command=lambda p=platform['key']: self.test_platform_connection(p, social_manager)
                    )
                    test_btn.pack(side='right')
                
                # Setup guide button
                guide_btn = ctk.CTkButton(
                    platform_frame,
                    text=f"📖 How to get {platform['name']} API credentials",
                    height=30,
                    fg_color='transparent',
                    border_width=1,
                    border_color=platform['color'],
                    text_color=platform['color'],
                    font=('Consolas', 10),
                    command=lambda p=platform['name']: self.show_api_guide(p)
                )
                guide_btn.pack(padx=15, pady=(0, 15))
            
            # Buttons frame
            buttons_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
            buttons_frame.pack(fill='x', pady=20)
            
            # Save all button
            save_btn = ctk.CTkButton(
                buttons_frame,
                text="💾 Save All Credentials",
                height=40,
                fg_color=self.colors['accent_green'],
                hover_color=self.colors['accent_cyan'],
                font=('Consolas', 12, 'bold'),
                command=lambda: self.save_all_social_credentials(social_manager, setup_window)
            )
            save_btn.pack(side='left', padx=(0, 10))
            
            # Test all button
            test_all_btn = ctk.CTkButton(
                buttons_frame,
                text="🧪 Test All Connections",
                height=40,
                fg_color=self.colors['accent_blue'],
                hover_color=self.colors['accent_purple'],
                font=('Consolas', 12, 'bold'),
                command=lambda: self.test_all_connections(social_manager)
            )
            test_all_btn.pack(side='left', padx=10)
            
            # Close button
            close_btn = ctk.CTkButton(
                buttons_frame,
                text="Close",
                height=40,
                fg_color=self.colors['bg_secondary'],
                hover_color=self.colors['text_muted'],
                font=('Consolas', 12),
                command=on_close
            )
            close_btn.pack(side='right')
            
        except Exception as e:
            print(f"Error showing social media setup: {e}")
            messagebox.showerror("Setup Error", f"Unable to show social media setup: {str(e)}")
    
    def test_platform_connection(self, platform, social_manager):
        """Test connection to a specific platform"""
        try:
            # Get credentials from entries
            credentials = {}
            if platform in self.platform_entries:
                for field, entry in self.platform_entries[platform].items():
                    credentials[field] = entry.get()
            
            # Test connection
            result = social_manager.test_platform_connection(platform, credentials)
            
            if result:
                messagebox.showinfo("Connection Test", f"✅ {platform.title()} connection successful!")
            else:
                messagebox.showerror("Connection Test", f"❌ {platform.title()} connection failed. Check your credentials.")
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Error testing {platform}: {str(e)}")
    
    def test_all_connections(self, social_manager):
        """Test all platform connections"""
        try:
            results = []
            
            for platform in self.platform_entries:
                credentials = {}
                for field, entry in self.platform_entries[platform].items():
                    credentials[field] = entry.get()
                
                if any(credentials.values()):  # Only test if credentials are provided
                    result = social_manager.test_platform_connection(platform, credentials)
                    status = "✅ Connected" if result else "❌ Failed"
                    results.append(f"{platform.title()}: {status}")
            
            if results:
                messagebox.showinfo("Connection Tests", "\n".join(results))
            else:
                messagebox.showwarning("No Credentials", "No credentials provided to test.")
                
        except Exception as e:
            messagebox.showerror("Test Error", f"Error testing connections: {str(e)}")
    
    def save_all_social_credentials(self, social_manager, window):
        """Save all social media credentials"""
        try:
            saved_count = 0
            
            for platform in self.platform_entries:
                credentials = {}
                for field, entry in self.platform_entries[platform].items():
                    value = entry.get().strip()
                    if value:
                        credentials[field] = value
                
                if credentials:
                    social_manager.save_credentials(platform, credentials)
                    saved_count += 1
            
            if saved_count > 0:
                messagebox.showinfo("Credentials Saved", f"✅ Saved credentials for {saved_count} platform(s)")
                window.destroy()
                self.root.focus_force()
            else:
                messagebox.showwarning("No Credentials", "No credentials provided to save.")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving credentials: {str(e)}")
    
    def show_api_guide(self, platform):
        """Show API setup guide for a platform"""
        try:
            guide_window = ctk.CTkToplevel()
            guide_window.title(f"{platform} API Setup Guide")
            guide_window.geometry("800x600")
            guide_window.configure(fg_color=self.colors['bg_primary'])
            
            # Make window modal
            guide_window.transient(self.root)
            guide_window.grab_set()
            
            # Main frame
            main_frame = ctk.CTkScrollableFrame(guide_window, fg_color=self.colors['bg_primary'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text=f"📖 {platform} API Setup Guide",
                font=('Consolas', 18, 'bold'),
                text_color=self.colors['accent_cyan']
            )
            title_label.pack(pady=(0, 20))
            
            # Guide content based on platform
            guides = {
                'YouTube': [
                    "1. Go to Google Cloud Console (console.cloud.google.com)",
                    "2. Create a new project or select existing one",
                    "3. Enable YouTube Data API v3",
                    "4. Create credentials (API Key)",
                    "5. Get your Channel ID from YouTube Studio",
                    "6. Copy API Key and Channel ID to the fields above"
                ],
                'TikTok': [
                    "1. Visit TikTok for Developers (developers.tiktok.com)",
                    "2. Create a developer account",
                    "3. Register your application",
                    "4. Get Access Token from app dashboard",
                    "5. Find your User ID in TikTok profile settings",
                    "6. Copy credentials to the fields above"
                ],
                'Instagram': [
                    "1. Go to Facebook for Developers (developers.facebook.com)",
                    "2. Create an app and add Instagram Basic Display",
                    "3. Configure Instagram Basic Display settings",
                    "4. Generate Access Token",
                    "5. Get your Instagram User ID",
                    "6. Copy credentials to the fields above"
                ],
                'Twitter/X': [
                    "1. Visit Twitter Developer Portal (developer.twitter.com)",
                    "2. Apply for developer account",
                    "3. Create a new app",
                    "4. Generate API Key and Secret",
                    "5. Generate Access Token and Secret",
                    "6. Copy all four credentials to the fields above"
                ]
            }
            
            steps = guides.get(platform, ["Guide not available for this platform"])
            
            for i, step in enumerate(steps, 1):
                step_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_secondary'])
                step_frame.pack(fill='x', pady=5)
                
                step_label = ctk.CTkLabel(
                    step_frame,
                    text=step,
                    font=('Consolas', 11),
                    text_color=self.colors['text_primary'],
                    anchor='w'
                )
                step_label.pack(padx=15, pady=10, fill='x')
            
            # Close button
            close_btn = ctk.CTkButton(
                main_frame,
                text="Close Guide",
                height=40,
                fg_color=self.colors['accent_blue'],
                font=('Consolas', 12),
                command=lambda: [guide_window.grab_release(), guide_window.destroy()]
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            print(f"Error showing API guide: {e}")
            messagebox.showerror("Guide Error", f"Unable to show API guide: {str(e)}")
    
    def save_content_filter(self):
        """Save content filtering settings"""
        try:
            # Collect content filter settings
            filters = {}
            if hasattr(self, 'profanity_var'):
                filters['profanity_filter'] = self.profanity_var.get()
            if hasattr(self, 'violence_var'):
                filters['violence_filter'] = self.violence_var.get()
            if hasattr(self, 'adult_var'):
                filters['adult_content_filter'] = self.adult_var.get()
            
            # Save settings
            import os, json
            config_dir = os.path.expanduser("~/.athena_video_editor")
            os.makedirs(config_dir, exist_ok=True)
            
            with open(os.path.join(config_dir, "content_filters.json"), "w") as f:
                json.dump(filters, f, indent=2)
            
            self.update_status("Content filter settings saved!")
        except Exception as e:
            self.update_status(f"Error saving content filters: {str(e)}")
    
    def save_video_processing(self):
        """Save video processing settings"""
        try:
            # Collect video processing settings
            processing = {}
            if hasattr(self, 'quality_var'):
                processing['quality_preset'] = self.quality_var.get()
            if hasattr(self, 'format_var'):
                processing['output_format'] = getattr(self, 'format_var', 'mp4')
            
            # Save settings
            import os, json
            config_dir = os.path.expanduser("~/.athena_video_editor")
            os.makedirs(config_dir, exist_ok=True)
            
            with open(os.path.join(config_dir, "video_processing.json"), "w") as f:
                json.dump(processing, f, indent=2)
            
            self.update_status("Video processing settings saved!")
        except Exception as e:
            self.update_status(f"Error saving video processing settings: {str(e)}")
    
    def save_advanced_options(self):
        """Save advanced options"""
        try:
            # Collect advanced settings
            advanced = {}
            if hasattr(self, 'thread_slider'):
                advanced['max_threads'] = int(self.thread_slider.get())
            if hasattr(self, 'memory_opt_var'):
                advanced['memory_optimization'] = self.memory_opt_var.get()
            
            # Save settings
            import os, json
            config_dir = os.path.expanduser("~/.athena_video_editor")
            os.makedirs(config_dir, exist_ok=True)
            
            with open(os.path.join(config_dir, "advanced_options.json"), "w") as f:
                json.dump(advanced, f, indent=2)
            
            self.update_status("Advanced options saved!")
        except Exception as e:
            self.update_status(f"Error saving advanced options: {str(e)}")
    
    def save_performance_settings(self):
        """Save performance settings"""
        try:
            # Collect performance settings
            performance = {}
            if hasattr(self, 'gpu_var'):
                performance['gpu_acceleration'] = self.gpu_var.get()
            if hasattr(self, 'parallel_var'):
                performance['parallel_processing'] = self.parallel_var.get()
            if hasattr(self, 'memory_opt_var'):
                performance['memory_optimization'] = self.memory_opt_var.get()
            
            # Save settings
            import os, json
            config_dir = os.path.expanduser("~/.athena_video_editor")
            os.makedirs(config_dir, exist_ok=True)
            
            with open(os.path.join(config_dir, "performance.json"), "w") as f:
                json.dump(performance, f, indent=2)
            
            self.update_status("Performance settings saved!")
        except Exception as e:
            self.update_status(f"Error saving performance settings: {str(e)}")