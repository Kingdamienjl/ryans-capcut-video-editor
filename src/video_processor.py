"""
Video processing module for Athena Video Editor
Handles video loading, analysis, and clip generation
"""

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not available - some video features disabled")

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    print("FFmpeg-python not available - using moviepy fallback")

try:
    from moviepy.editor import VideoFileClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("MoviePy not available - video processing disabled")

import os
import tempfile
from typing import Dict, List, Tuple, Optional
import subprocess
import json

class VideoProcessor:
    """Handles all video processing operations"""
    
    def __init__(self):
        self.current_video = None
        self.video_info = {}
        
    def load_video(self, video_path: str) -> Dict:
        """Load video and extract basic information"""
        try:
            # Use OpenCV to get basic info
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            self.video_info = {
                'path': video_path,
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'size_mb': os.path.getsize(video_path) / (1024 * 1024)
            }
            
            return self.video_info
            
        except Exception as e:
            raise Exception(f"Error loading video: {str(e)}")
    
    def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extract audio from video using FFmpeg or moviepy fallback"""
        if not MOVIEPY_AVAILABLE and not FFMPEG_AVAILABLE:
            # Audio extraction requires video processing libraries
            return None
            
        try:
            if FFMPEG_AVAILABLE:
                # Use FFmpeg for better performance
                (
                    ffmpeg
                    .input(video_path)
                    .output(output_path, acodec='pcm_s16le', ac=1, ar='16000')
                    .overwrite_output()
                    .run(quiet=True)
                )
            elif MOVIEPY_AVAILABLE:
                # Fallback to moviepy
                video = VideoFileClip(video_path)
                audio = video.audio
                audio.write_audiofile(output_path, verbose=False, logger=None)
                video.close()
                audio.close()
            
            return output_path
        except Exception as e:
            raise Exception(f"Error extracting audio: {str(e)}")
    
    def load_video_info(self, video_path: str) -> Dict:
        """Load basic video information"""
        if not MOVIEPY_AVAILABLE:
            # Video info requires video processing libraries
            return {
                'duration': 0,
                'fps': 0,
                'width': 0,
                'height': 0,
                'size': 0
            }
            
        try:
            video = VideoFileClip(video_path)
            info = {
                'duration': video.duration,
                'fps': video.fps,
                'width': video.w,
                'height': video.h,
                'size': os.path.getsize(video_path)
            }
            video.close()
            return info
        except Exception as e:
            raise Exception(f"Error loading video: {str(e)}")
    
    def get_video_frames(self, video_path: str, sample_rate: int = 30) -> List:
        """Extract frames from video for analysis"""
        if not CV2_AVAILABLE:
            # Return empty list if OpenCV not available
            return []
            
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample every nth frame
                if frame_count % sample_rate == 0:
                    frames.append(frame)
                
                frame_count += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            raise Exception(f"Error extracting frames: {str(e)}")
    
    def sample_frames(self, video_path: str, num_samples: int = 10) -> List:
        """Sample frames from video for analysis"""
        if not CV2_AVAILABLE:
            # Return empty list if OpenCV not available
            return []
            
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            frames = []
            for i in range(num_samples):
                frame_idx = int((i / num_samples) * total_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            return frames
        except Exception as e:
            raise Exception(f"Error sampling frames: {str(e)}")
    
    def create_clips(self, video_path: str, highlights: List[Dict], output_dir: str) -> List[str]:
        """Create video clips from highlight segments with multiple fallbacks"""
        try:
            output_files = []
            
            # Try multiple approaches in order of preference
            methods = [
                ("FFmpeg (system)", self._create_clips_ffmpeg_system),
                ("FFmpeg (python)", self._create_clips_ffmpeg_python),
                ("MoviePy", self._create_clips_moviepy),
                ("OpenCV", self._create_clips_opencv)
            ]
            
            for method_name, method_func in methods:
                try:
                    print(f"Attempting video processing with {method_name}...")
                    return method_func(video_path, highlights, output_dir)
                except Exception as e:
                    print(f"{method_name} failed: {str(e)}")
                    continue
            
            # If all methods fail
            raise Exception("All video processing methods failed. Please install FFmpeg or MoviePy.")
            
        except Exception as e:
            raise Exception(f"Error creating clips: {str(e)}")
    
    def _create_clips_ffmpeg_system(self, video_path: str, highlights: List[Dict], output_dir: str) -> List[str]:
        """Create clips using system FFmpeg command"""
        if not self._check_ffmpeg():
            raise Exception("System FFmpeg not available")
            
        output_files = []
        
        for i, highlight in enumerate(highlights):
            start_time = highlight['start_time']
            end_time = highlight['end_time']
            title = highlight.get('title', f'Clip_{i+1}')
            
            # Clean title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            output_file = os.path.join(output_dir, f"{safe_title}_{i+1}.mp4")
            
            # Use FFmpeg to create clip with audio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(start_time),  # Start time
                '-t', str(end_time - start_time),  # Duration
                '-c:v', 'libx264',  # Video codec
                '-c:a', 'aac',  # Audio codec - ensure audio is included
                '-preset', 'medium',  # Encoding speed/quality balance
                '-crf', '23',  # Quality (lower = better quality)
                '-avoid_negative_ts', 'make_zero',  # Fix audio sync issues
                '-y',  # Overwrite output file
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                output_files.append(output_file)
            else:
                raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_files
    
    def _create_clips_ffmpeg_python(self, video_path: str, highlights: List[Dict], output_dir: str) -> List[str]:
        """Create clips using ffmpeg-python library"""
        if not FFMPEG_AVAILABLE:
            raise Exception("ffmpeg-python library not available")
            
        output_files = []
        
        for i, highlight in enumerate(highlights):
            start_time = highlight['start_time']
            end_time = highlight['end_time']
            title = highlight.get('title', f'Clip_{i+1}')
            
            # Clean title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            output_file = os.path.join(output_dir, f"{safe_title}_{i+1}.mp4")
            
            # Use ffmpeg-python with audio preservation
            (
                ffmpeg
                .input(video_path, ss=start_time, t=end_time - start_time)
                .output(output_file, vcodec='libx264', acodec='aac', avoid_negative_ts='make_zero')
                .overwrite_output()
                .run(quiet=True)
            )
            
            output_files.append(output_file)
        
        return output_files
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _create_clips_opencv(self, video_path: str, highlights: List[Dict], output_dir: str) -> List[str]:
        """Create clips using OpenCV as fallback"""
        if not CV2_AVAILABLE:
            raise Exception("OpenCV not available")
            
        output_files = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            for i, highlight in enumerate(highlights):
                start_time = highlight['start_time']
                end_time = highlight['end_time']
                title = highlight.get('title', f'Clip_{i+1}')
                
                # Clean title for filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')
                
                output_file = os.path.join(output_dir, f"{safe_title}_{i+1}.avi")  # Use AVI for OpenCV
                
                # Calculate frame numbers
                start_frame = int(start_time * fps)
                end_frame = int(end_time * fps)
                
                # Set up video writer
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
                
                # Extract frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                
                for frame_num in range(start_frame, end_frame):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                
                out.release()
                output_files.append(output_file)
            
            cap.release()
            return output_files
            
        except Exception as e:
            raise Exception(f"OpenCV processing failed: {str(e)}")
    
    def _create_clips_dummy(self, video_path: str, highlights: List[Dict], output_dir: str) -> List[str]:
        """Production mode - no dummy clips created when video processing is unavailable"""
        print("No video processing libraries available - cannot create clips")
        return []
    
    def _create_clips_moviepy(self, video_path: str, highlights: List[Dict], output_dir: str) -> List[str]:
        """Create clips using MoviePy as fallback"""
        if not MOVIEPY_AVAILABLE:
            raise Exception("MoviePy not available")
            
        try:
            from moviepy.editor import VideoFileClip
            output_files = []
            
            # Load the video once
            video = VideoFileClip(video_path)
            
            for i, highlight in enumerate(highlights):
                start_time = highlight['start_time']
                end_time = highlight['end_time']
                title = highlight.get('title', f'Clip_{i+1}')
                
                # Clean title for filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')
                
                output_file = os.path.join(output_dir, f"{safe_title}_{i+1}.mp4")
                
                # Create clip using MoviePy with audio
                clip = video.subclip(start_time, end_time)
                # Ensure audio is preserved
                clip.write_videofile(
                    output_file, 
                    codec='libx264', 
                    audio_codec='aac', 
                    verbose=False, 
                    logger=None,
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                clip.close()
                
                output_files.append(output_file)
            
            video.close()
            return output_files
            
        except Exception as e:
            raise Exception(f"Error creating clips with MoviePy: {str(e)}")
    
    def create_preview_clips(self, video_path: str, highlights: List[Dict], duration: int = 5) -> List[str]:
        """Create short preview clips for review"""
        try:
            temp_dir = tempfile.gettempdir()
            preview_files = []
            
            for i, highlight in enumerate(highlights):
                start_time = highlight['start_time']
                preview_file = os.path.join(temp_dir, f"preview_{i+1}.mp4")
                
                # Create short preview clip
                cmd = [
                    'ffmpeg',
                    '-i', video_path,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'ultrafast',  # Fast encoding for previews
                    '-crf', '28',  # Lower quality for previews
                    '-vf', 'scale=480:270',  # Small resolution for previews
                    '-y',
                    preview_file
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    preview_files.append(preview_file)
            
            return preview_files
            
        except Exception as e:
            raise Exception(f"Error creating preview clips: {str(e)}")
    
    def get_video_thumbnail(self, video_path: str, timestamp: float) -> Optional[str]:
        """Generate thumbnail at specific timestamp"""
        try:
            temp_dir = tempfile.gettempdir()
            thumbnail_path = os.path.join(temp_dir, f"thumb_{timestamp}.jpg")
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(timestamp),
                '-vframes', '1',  # Extract single frame
                '-vf', 'scale=320:180',  # Thumbnail size
                '-y',
                thumbnail_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return thumbnail_path
            else:
                return None
                
        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return None
    
    def optimize_for_platform(self, input_file: str, platform: str) -> str:
        """Optimize video for specific social media platform"""
        platform_settings = {
            'youtube_shorts': {
                'aspect_ratio': '9:16',
                'resolution': '1080x1920',
                'max_duration': 60,
                'bitrate': '2M'
            },
            'instagram_reels': {
                'aspect_ratio': '9:16', 
                'resolution': '1080x1920',
                'max_duration': 90,
                'bitrate': '3.5M'
            },
            'tiktok': {
                'aspect_ratio': '9:16',
                'resolution': '1080x1920', 
                'max_duration': 180,
                'bitrate': '2M'
            },
            'twitter': {
                'aspect_ratio': '16:9',
                'resolution': '1280x720',
                'max_duration': 140,
                'bitrate': '2M'
            }
        }
        
        if platform not in platform_settings:
            return input_file
        
        settings = platform_settings[platform]
        output_file = input_file.replace('.mp4', f'_{platform}.mp4')
        
        try:
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-vf', f'scale={settings["resolution"]}:force_original_aspect_ratio=decrease,pad={settings["resolution"]}:(ow-iw)/2:(oh-ih)/2',
                '-b:v', settings['bitrate'],
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_file
            else:
                print(f"Error optimizing for {platform}: {result.stderr}")
                return input_file
                
        except Exception as e:
            print(f"Error optimizing video: {str(e)}")
            return input_file