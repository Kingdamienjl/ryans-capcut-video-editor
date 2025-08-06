"""
Configuration management for Athena Video Editor
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AISettings:
    """AI analysis settings"""
    whisper_model: str = "base"
    scene_threshold: float = 0.3
    highlight_min_duration: int = 10  # seconds
    highlight_max_duration: int = 60  # seconds
    confidence_threshold: float = 0.7

@dataclass
class VideoSettings:
    """Video processing settings"""
    output_format: str = "mp4"
    output_quality: str = "high"  # low, medium, high
    fps: int = 30
    resolution: str = "1080p"  # 720p, 1080p, 4k
    
@dataclass
class UISettings:
    """UI preferences"""
    theme: str = "dark"
    accent_color: str = "#00ff88"  # Cyberpunk green
    window_size: str = "1200x800"
    auto_save_settings: bool = True

class Config:
    """Configuration manager for the application"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".athena_video_editor"
        self.config_file = self.config_dir / "config.json"
        
        # Default settings
        self.ai_settings = AISettings()
        self.video_settings = VideoSettings()
        self.ui_settings = UISettings()
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load existing config
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Update settings from loaded data
                if 'ai_settings' in data:
                    self.ai_settings = AISettings(**data['ai_settings'])
                if 'video_settings' in data:
                    self.video_settings = VideoSettings(**data['video_settings'])
                if 'ui_settings' in data:
                    self.ui_settings = UISettings(**data['ui_settings'])
                    
            except Exception as e:
                print(f"Error loading config: {e}")
                # Use defaults if config is corrupted
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config_data = {
                'ai_settings': asdict(self.ai_settings),
                'video_settings': asdict(self.video_settings),
                'ui_settings': asdict(self.ui_settings)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_output_settings(self) -> Dict[str, Any]:
        """Get video output settings for FFmpeg"""
        quality_presets = {
            'low': {'crf': 28, 'preset': 'fast'},
            'medium': {'crf': 23, 'preset': 'medium'},
            'high': {'crf': 18, 'preset': 'slow'}
        }
        
        resolution_settings = {
            '720p': {'width': 1280, 'height': 720},
            '1080p': {'width': 1920, 'height': 1080},
            '4k': {'width': 3840, 'height': 2160}
        }
        
        settings = quality_presets[self.video_settings.output_quality]
        settings.update(resolution_settings[self.video_settings.resolution])
        settings['fps'] = self.video_settings.fps
        settings['format'] = self.video_settings.output_format
        
        return settings
    
    def update_ai_settings(self, **kwargs):
        """Update AI settings"""
        for key, value in kwargs.items():
            if hasattr(self.ai_settings, key):
                setattr(self.ai_settings, key, value)
        
        if self.ui_settings.auto_save_settings:
            self.save_config()
    
    def update_video_settings(self, **kwargs):
        """Update video settings"""
        for key, value in kwargs.items():
            if hasattr(self.video_settings, key):
                setattr(self.video_settings, key, value)
        
        if self.ui_settings.auto_save_settings:
            self.save_config()
    
    def update_ui_settings(self, **kwargs):
        """Update UI settings"""
        for key, value in kwargs.items():
            if hasattr(self.ui_settings, key):
                setattr(self.ui_settings, key, value)
        
        if self.ui_settings.auto_save_settings:
            self.save_config()