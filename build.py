#!/usr/bin/env python3
"""
Build script for Athena Video Editor
Creates a Windows executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required build tools are installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check for FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg found")
        else:
            print("⚠️  FFmpeg not found in PATH. Please install FFmpeg for video processing.")
    except FileNotFoundError:
        print("⚠️  FFmpeg not found. Please install FFmpeg for video processing.")

def create_spec_file():
    """Create PyInstaller spec file with custom configuration"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'whisper',
        'torch',
        'torchvision',
        'torchaudio',
        'transformers',
        'sklearn',
        'cv2',
        'numpy',
        'PIL',
        'customtkinter',
        'moviepy',
        'ffmpeg'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AthenaVideoEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/athena_icon.ico' if os.path.exists('assets/athena_icon.ico') else None,
)
'''
    
    with open('athena_video_editor.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file")

def create_icon():
    """Create a simple icon for the application"""
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple SVG icon
    icon_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00ffff;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#8b00ff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00ff88;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="32" cy="32" r="30" fill="url(#grad1)" opacity="0.8"/>
  
  <!-- Lightning bolt (Athena symbol) -->
  <path d="M28 12 L36 12 L30 28 L38 28 L26 52 L30 32 L22 32 Z" 
        fill="#ffffff" stroke="#000000" stroke-width="1"/>
  
  <!-- Video play symbol -->
  <polygon points="20,45 20,55 28,50" fill="#ffffff" opacity="0.9"/>
  <polygon points="36,45 36,55 44,50" fill="#ffffff" opacity="0.9"/>
</svg>'''
    
    icon_path = assets_dir / 'athena_icon.svg'
    with open(icon_path, 'w') as f:
        f.write(icon_svg)
    
    print("✅ Created application icon")

def build_executable():
    """Build the Windows executable"""
    print("🔨 Building Windows executable...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Run PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=AthenaVideoEditor',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        'athena_video_editor.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = Path('dist/AthenaVideoEditor.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
        else:
            print("❌ Executable not found in dist folder")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo.
echo ========================================
echo   Athena Video Editor Installer
echo ========================================
echo.
echo Installing Athena Video Editor...
echo.

REM Create installation directory
if not exist "%PROGRAMFILES%\\AthenaVideoEditor" (
    mkdir "%PROGRAMFILES%\\AthenaVideoEditor"
)

REM Copy executable
copy "AthenaVideoEditor.exe" "%PROGRAMFILES%\\AthenaVideoEditor\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Athena Video Editor.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\AthenaVideoEditor\\AthenaVideoEditor.exe'; $Shortcut.Save()"

REM Create start menu entry
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Athena Video Editor" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Athena Video Editor"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Athena Video Editor\\Athena Video Editor.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\AthenaVideoEditor\\AthenaVideoEditor.exe'; $Shortcut.Save()"

echo.
echo ✅ Installation completed!
echo.
echo You can now run Athena Video Editor from:
echo - Desktop shortcut
echo - Start Menu
echo - %PROGRAMFILES%\\AthenaVideoEditor\\AthenaVideoEditor.exe
echo.
pause
'''
    
    with open('dist/install.bat', 'w') as f:
        f.write(installer_content)
    
    print("✅ Created installer script")

def main():
    """Main build process"""
    print("🚀 Starting Athena Video Editor build process...")
    print()
    
    # Check dependencies
    print("1. Checking dependencies...")
    check_dependencies()
    print()
    
    # Create assets
    print("2. Creating assets...")
    create_icon()
    print()
    
    # Create spec file
    print("3. Creating build configuration...")
    create_spec_file()
    print()
    
    # Build executable
    print("4. Building executable...")
    if build_executable():
        print()
        print("5. Creating installer...")
        create_installer_script()
        print()
        print("🎉 Build process completed successfully!")
        print()
        print("📁 Output files:")
        print("   - dist/AthenaVideoEditor.exe (Main executable)")
        print("   - dist/install.bat (Installer script)")
        print()
        print("🚀 Ready to distribute to Ryan!")
    else:
        print("❌ Build process failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())