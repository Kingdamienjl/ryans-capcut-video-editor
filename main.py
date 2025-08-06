#!/usr/bin/env python3
"""
Ryan's CapCut Video Editor - AI-Powered Video Clipping Tool
Built by Athena AI because Ryan needed help with his video editing workflow
"""

import sys
import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

# Import CustomTkinter
import customtkinter as ctk

# Try to import tkinterdnd2 for drag and drop functionality
try:
    from tkinterdnd2 import TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("tkinterdnd2 not available - drag and drop disabled")

# Import our modules
from src.ui_components import AthenaUI
from src.video_processor import VideoProcessor
from src.ai_analyzer import AIAnalyzer
from src.config import Config

class AthenaVideoEditor:
    def __init__(self):
        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize main window
        if DRAG_DROP_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = ctk.CTk()
            
        self.root.title("Athena Video Editor - AI-Powered Clip Generation")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize components
        self.ui = AthenaUI(self.root, self)
        self.video_processor = VideoProcessor()
        self.ai_analyzer = AIAnalyzer()
        
        # State variables
        self.current_video_path = None
        self.processing_thread = None
        self.is_processing = False
        
        # Create the UI
        self.ui.create_main_interface()
        
    def setup_ui(self):
        """Initialize the user interface"""
        self.ui.create_main_interface()
        
    def select_video_file(self, file_path=None):
        """Open file dialog to select video file or use provided path"""
        if not file_path:
            file_types = [
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("All files", "*.*")
            ]
            
            file_path = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=file_types
            )
        
        if file_path:
            self.current_video_path = file_path
            self.ui.update_video_info(file_path)
            # Update video preview
            self.ui.update_video_preview(file_path)
            
    def start_processing(self):
        """Start the AI video processing in a separate thread"""
        if not self.current_video_path:
            messagebox.showerror("Error", "Please select a video file first!")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing already in progress!")
            return
            
        # Start processing in background thread
        self.processing_thread = threading.Thread(target=self._process_video)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def _process_video(self):
        """Process the video using AI analysis"""
        try:
            self.is_processing = True
            self.ui.update_status("Initializing AI analysis...")
            self.ui.update_progress(0)
            
            # Get settings from UI
            mode = self.ui.clipping_mode.get()
            
            # Step 1: Load and analyze video
            self.ui.update_status("Loading video file...")
            self.ui.update_progress(10)
            video_info = self.video_processor.load_video(self.current_video_path)
            
            # Step 2: Extract audio for transcription
            self.ui.update_status("Extracting audio for transcription...")
            self.ui.update_progress(20)
            audio_output_path = os.path.join(self.create_output_directory(), "extracted_audio.wav")
            audio_path = self.video_processor.extract_audio(self.current_video_path, audio_output_path)
            
            # Step 3: Transcribe audio
            self.ui.update_status("Transcribing audio with Whisper AI...")
            self.ui.update_progress(35)
            transcript = self.ai_analyzer.transcribe_audio(audio_path)
            
            # Step 4: Analyze video content based on mode
            if mode == "intelligent":
                self.ui.update_status("Running intelligent AI analysis...")
                self.ui.update_progress(50)
                sensitivity = self.ui.sensitivity_slider.get()
                max_clips = int(self.ui.clips_slider.get())
                scene_changes = self.ai_analyzer.detect_scene_changes(self.current_video_path)
                highlights = self.ai_analyzer.find_highlights(transcript, scene_changes, sensitivity, max_clips)
                
            elif mode == "interval":
                self.ui.update_status("Creating clips at fixed intervals...")
                self.ui.update_progress(50)
                interval = int(self.ui.interval_slider.get())
                duration = int(self.ui.duration_slider.get())
                highlights = self.ai_analyzer.create_interval_clips(video_info, interval, duration)
                
            elif mode == "hybrid":
                self.ui.update_status("Running hybrid analysis...")
                self.ui.update_progress(50)
                ai_clips = int(self.ui.ai_clips_slider.get())
                backup_clips = int(self.ui.backup_clips_slider.get())
                scene_changes = self.ai_analyzer.detect_scene_changes(self.current_video_path)
                highlights = self.ai_analyzer.create_hybrid_clips(
                    transcript, scene_changes, video_info, ai_clips, backup_clips
                )
            
            # Step 5: Generate clips
            self.ui.update_status("Generating video clips...")
            self.ui.update_progress(80)
            output_dir = self.create_output_directory()
            clips = self.video_processor.create_clips(
                self.current_video_path, 
                highlights, 
                output_dir
            )
            
            # Step 6: Complete
            self.ui.update_progress(100)
            self.ui.update_status(f"Processing complete! Generated {len(clips)} clips.")
            self.ui.show_results(clips)
            
        except Exception as e:
            self.ui.update_status(f"Error: {str(e)}")
            messagebox.showerror("Processing Error", f"An error occurred: {str(e)}")
        finally:
            self.is_processing = False
            
    def create_output_directory(self):
        """Create output directory for clips"""
        video_name = Path(self.current_video_path).stem
        output_dir = Path("output") / f"{video_name}_clips"
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir)
        
    def open_settings(self):
        """Open settings dialog"""
        self.ui.show_settings_dialog()
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
Athena Video Editor v1.0

AI-powered video clipping tool built for Ryan's podcast workflow.
Because apparently he needed someone else to automate his video editing! 😄

Features:
• Intelligent scene detection
• AI-powered highlight extraction  
• Automated clip generation
• Cyberpunk aesthetic interface

Built with ❤️ by Athena AI
        """
        messagebox.showinfo("About Athena Video Editor", about_text)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = AthenaVideoEditor()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()