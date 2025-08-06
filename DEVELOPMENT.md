# Athena Video Editor - Development Guide

## Project Structure

```
ryans-capcut-video-editor/
├── main.py                 # Main application entry point
├── setup.py               # Development setup script
├── build.py               # Build script for Windows executable
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── DEVELOPMENT.md        # This file
├── .gitignore           # Git ignore rules
├── src/                 # Source code modules
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   ├── video_processor.py # Video processing logic
│   ├── ai_analyzer.py   # AI analysis and transcription
│   └── ui_components.py # User interface components
├── assets/              # Application assets
├── output/              # Generated video clips
└── temp/               # Temporary files
```

## Development Setup

### Prerequisites

1. **Python 3.8+** - Required for all dependencies
2. **FFmpeg** - Essential for video processing
   - Download from: https://ffmpeg.org/download.html
   - Add to system PATH
3. **Git** - For version control

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ryans-capcut-video-editor.git
   cd ryans-capcut-video-editor
   ```

2. Run setup script:
   ```bash
   python setup.py
   ```

3. Start development:
   ```bash
   python main.py
   ```

### Manual Setup

If the setup script fails, install manually:

```bash
# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir output temp assets
```

## Architecture Overview

### Core Components

1. **Main Application (`main.py`)**
   - Application entry point
   - Coordinates all components
   - Handles threading for AI processing

2. **Video Processor (`src/video_processor.py`)**
   - Video file loading and analysis
   - Audio extraction for transcription
   - Clip generation and optimization
   - Platform-specific output formatting

3. **AI Analyzer (`src/ai_analyzer.py`)**
   - Whisper-based audio transcription
   - Scene change detection using OpenCV
   - Intelligent highlight identification
   - Content analysis and scoring

4. **UI Components (`src/ui_components.py`)**
   - CustomTkinter-based modern interface
   - Cyberpunk aesthetic with Athena branding
   - Progress tracking and result display
   - Settings and configuration dialogs

5. **Configuration (`src/config.py`)**
   - User preferences management
   - AI model settings
   - Video output parameters
   - Persistent storage

### AI Processing Pipeline

1. **Video Loading**
   - Extract metadata (duration, resolution, fps)
   - Validate file format and accessibility

2. **Audio Extraction**
   - Convert video audio to WAV format
   - Optimize for Whisper transcription (16kHz, mono)

3. **Transcription**
   - Use OpenAI Whisper for speech-to-text
   - Generate word-level timestamps
   - Identify language automatically

4. **Scene Analysis**
   - Detect scene changes using histogram comparison
   - Identify visual transitions and cuts

5. **Highlight Detection**
   - Analyze transcript for interesting content
   - Score segments based on keywords and patterns
   - Align with scene changes for optimal cuts

6. **Clip Generation**
   - Create video segments using FFmpeg
   - Apply platform-specific optimizations
   - Generate thumbnails and previews

## Key Features

### Intelligent Content Analysis

- **Keyword Scoring**: Identifies segments with interesting vocabulary
- **Duration Optimization**: Prefers clips of optimal length (10-60 seconds)
- **Emotional Detection**: Recognizes excitement, questions, and emphasis
- **Scene Alignment**: Aligns cuts with natural visual transitions

### Video Processing

- **Multi-format Support**: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- **Quality Presets**: Low, Medium, High quality output options
- **Platform Optimization**: YouTube Shorts, Instagram Reels, TikTok formats
- **Batch Processing**: Handle multiple videos simultaneously

### User Interface

- **Cyberpunk Theme**: Dark interface with cyan/green/purple accents
- **Real-time Progress**: Live updates during AI processing
- **Result Preview**: Thumbnail and metadata for each generated clip
- **Settings Panel**: Configurable AI parameters and output options

## Building for Distribution

### Create Windows Executable

```bash
python build.py
```

This will:
1. Check dependencies and install PyInstaller
2. Create application icon and assets
3. Generate PyInstaller spec file
4. Build single-file executable
5. Create installer script

### Output Files

- `dist/AthenaVideoEditor.exe` - Main executable
- `dist/install.bat` - Windows installer script

## Testing

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Video file selection works
- [ ] AI processing completes successfully
- [ ] Clips are generated in output directory
- [ ] UI updates show progress correctly
- [ ] Settings can be modified and saved
- [ ] Generated clips play correctly

### Test Videos

Use various video types for testing:
- Short videos (< 5 minutes) for quick testing
- Long videos (> 30 minutes) for full pipeline testing
- Different formats (MP4, AVI, MOV)
- Various resolutions (720p, 1080p, 4K)
- Different audio qualities

## Performance Optimization

### Memory Management

- Process videos in chunks to avoid memory overflow
- Clean up temporary files after processing
- Use efficient video codecs for output

### Processing Speed

- Optimize Whisper model size vs. accuracy trade-off
- Use GPU acceleration when available
- Implement parallel processing for multiple clips

### Storage Efficiency

- Compress output videos appropriately
- Clean up intermediate files
- Implement smart caching for repeated operations

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Install FFmpeg and add to PATH
   - Restart application after installation

2. **Whisper model download fails**
   - Check internet connection
   - Ensure sufficient disk space
   - Try smaller model size

3. **Video processing errors**
   - Verify video file is not corrupted
   - Check file permissions
   - Ensure sufficient disk space for output

4. **UI freezing during processing**
   - Processing runs in background thread
   - UI should remain responsive
   - Check for threading issues

### Debug Mode

Enable debug output by modifying `main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where possible
- Add docstrings to all functions and classes
- Keep functions focused and modular

### Git Workflow

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test thoroughly
3. Commit with descriptive messages
4. Push and create pull request

### Adding Features

1. Update requirements.txt if new dependencies added
2. Add configuration options to `src/config.py`
3. Update UI components if needed
4. Test with various video types
5. Update documentation

## Deployment

### GitHub Releases

1. Build executable: `python build.py`
2. Test executable on clean Windows system
3. Create GitHub release with:
   - Executable file
   - Installer script
   - Release notes
   - Installation instructions

### Version Management

Update version numbers in:
- `main.py` (application title)
- `src/ui_components.py` (status bar)
- `README.md` (documentation)
- GitHub release tags

---

*Built with ❤️ by Athena AI for Ryan's creative workflow*