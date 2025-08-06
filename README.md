# Athena Video Editor 🎬

*An AI-powered video clipping tool that automatically creates highlight clips from long-form videos.*

## 🚀 Quick Start (For Ryan and Everyone Else)

### Option 1: Download Ready-to-Use Executable (Easiest)
1. Go to [Releases](https://github.com/your-username/athena-video-editor/releases)
2. Download `AthenaVideoEditor.exe`
3. Double-click to run - that's it! 

### Option 2: Run from Source
1. Download this repository (green "Code" button → "Download ZIP")
2. Extract the ZIP file
3. Double-click `setup.py` to install everything automatically
4. Run `main.py` to start the application

## ✨ Features

- **🤖 AI-Powered Analysis**: Automatically finds the best moments in your videos
- **🎯 Smart Clipping**: Creates multiple short clips perfect for social media
- **🔊 Audio Transcription**: Uses Whisper AI to understand what's being said
- **📱 Platform Optimization**: Outputs optimized for YouTube Shorts, TikTok, Instagram Reels
- **🎨 Modern Interface**: Clean, cyberpunk-inspired design
- **⚡ Fast Processing**: Uses FFmpeg for lightning-fast video processing

## 📖 How to Use

1. **Launch** the application
2. **Select** your video file (MP4, AVI, MOV, etc.)
3. **Configure** settings:
   - Number of clips to generate
   - Minimum clip duration
   - Add your OpenAI API key for better AI analysis
4. **Click "Analyze Video"** and let Athena work
5. **Review** generated clips in the output folder
6. **Share** your clips on social media!

## 🛠️ Technical Requirements

- **Windows 10/11** (64-bit)
- **4GB RAM** minimum (8GB recommended)
- **FFmpeg** (automatically installed by setup script)
- **Internet connection** (for AI features)

## 🔧 For Developers

```bash
# Clone the repository
git clone https://github.com/your-username/athena-video-editor.git
cd athena-video-editor

# Install dependencies
python setup.py

# Run the application
python main.py

# Build executable
python build.py
```

## 📁 Project Structure

```
athena-video-editor/
├── main.py              # Application entry point
├── setup.py             # Automatic dependency installer
├── build.py             # Executable builder
├── requirements.txt     # Python dependencies
└── src/                 # Source code
    ├── ai_analyzer.py   # AI analysis engine
    ├── video_processor.py # Video processing
    ├── ui_components.py # User interface
    └── ...
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - Feel free to use, modify, and distribute.

---

*Built with ❤️ by Athena AI - Making video editing accessible for everyone, especially Ryan.*