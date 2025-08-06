#!/usr/bin/env python3
"""
Setup script for Athena Video Editor
Handles installation of dependencies and initial setup
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed and accessible")
            return True
        else:
            print("⚠️  FFmpeg found but may not be working correctly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in system PATH")
        print("Please install FFmpeg from: https://ffmpeg.org/download.html")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = ['output', 'temp', 'assets']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def download_models():
    """Download required AI models"""
    print("🤖 Downloading AI models...")
    
    try:
        # This will download the Whisper base model on first use
        import whisper
        model = whisper.load_model("base")
        print("✅ Whisper model downloaded successfully")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not pre-download models: {e}")
        print("Models will be downloaded automatically on first use")
        return True

def create_desktop_shortcut():
    """Create desktop shortcut for development"""
    if platform.system() != "Windows":
        return
    
    try:
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "Athena Video Editor (Dev).lnk"
        
        # PowerShell command to create shortcut
        ps_command = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{sys.executable}"
$Shortcut.Arguments = "{Path.cwd() / 'main.py'}"
$Shortcut.WorkingDirectory = "{Path.cwd()}"
$Shortcut.IconLocation = "{sys.executable}"
$Shortcut.Description = "Athena Video Editor - Development Version"
$Shortcut.Save()
'''
        
        subprocess.run(['powershell', '-Command', ps_command], check=True)
        print("✅ Desktop shortcut created")
        
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")

def verify_installation():
    """Verify that all required components are installed"""
    print("🔍 Verifying installation...")
    
    try:
        # Test imports
        import customtkinter
        import cv2
        import numpy
        import whisper
        import moviepy
        import ffmpeg
        
        print("✅ All core modules can be imported")
        return True
        
    except ImportError as e:
        print(f"❌ Import verification failed: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 Athena Video Editor Setup")
    print("=" * 40)
    print()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    print()
    
    # Check FFmpeg
    check_ffmpeg()
    print()
    
    # Setup directories
    print("📁 Setting up directories...")
    setup_directories()
    print()
    
    # Download models
    download_models()
    print()
    
    # Create shortcut
    print("🔗 Creating shortcuts...")
    create_desktop_shortcut()
    print()
    
    # Verify installation
    if not verify_installation():
        print("⚠️  Some components failed verification, but setup may still work")
    
    print()
    print("🎉 Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Make sure FFmpeg is installed if not already")
    print("2. Run: python main.py")
    print("3. Or use the desktop shortcut if created")
    print()
    print("To build executable: python build.py")
    print()
    print("Happy video editing! 🎬")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())