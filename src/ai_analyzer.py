"""
AI Analysis module for Athena Video Editor
Handles audio transcription, scene detection, and highlight identification
"""

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper not available - AI transcription disabled")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not available - scene detection disabled")

import numpy as np
from typing import List, Dict, Tuple, Optional
import re
from collections import Counter
import tempfile
import os

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class AIAnalyzer:
    """AI-powered video content analyzer"""
    
    def __init__(self):
        self.whisper_model = None
        self.load_whisper_model()
        
    def load_whisper_model(self, model_size: str = "base"):
        """Load Whisper model for transcription"""
        if not WHISPER_AVAILABLE:
            print("Whisper not available - transcription disabled")
            return
            
        try:
            print(f"Loading Whisper model: {model_size}")
            self.whisper_model = whisper.load_model(model_size)
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.whisper_model = None
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio using Whisper"""
        if not WHISPER_AVAILABLE or not self.whisper_model:
            print("Whisper not available - transcription disabled")
            # Return empty transcript for production mode
            return {
                'text': "",
                'segments': []
            }
        
        try:
            print("Starting transcription...")
            result = self.whisper_model.transcribe(
                audio_path,
                word_timestamps=True,
                verbose=False
            )
            
            # Process segments with word-level timestamps
            processed_segments = []
            for segment in result['segments']:
                processed_segment = {
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'words': segment.get('words', [])
                }
                processed_segments.append(processed_segment)
            
            return {
                'text': result['text'],
                'segments': processed_segments,
                'language': result['language']
            }
            
        except Exception as e:
            raise Exception(f"Error during transcription: {str(e)}")
    
    def detect_scene_changes(self, video_path: str, threshold: float = 0.3) -> List[float]:
        """Detect scene changes in video using histogram comparison"""
        if not CV2_AVAILABLE:
            print("OpenCV not available - scene change detection disabled")
            # Return empty scene changes for production mode
            return []
            
        try:
            cap = cv2.VideoCapture(video_path)
            scene_changes = [0.0]  # Always include start
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            prev_hist = None
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Calculate histogram for current frame
                hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                
                if prev_hist is not None:
                    # Compare with previous frame
                    correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    
                    # If correlation is low, it's likely a scene change
                    if correlation < (1 - threshold):
                        timestamp = frame_count / fps
                        scene_changes.append(timestamp)
                
                prev_hist = hist
                frame_count += 1
            
            cap.release()
            return scene_changes
            
        except Exception as e:
            raise Exception(f"Error detecting scene changes: {str(e)}")
    
    def find_highlights(self, transcript: Dict, scene_changes: List[float], sensitivity: float = 0.6, max_clips: int = 8) -> List[Dict]:
        """Identify highlight segments using AI analysis with configurable sensitivity"""
        try:
            segments = transcript['segments']
            highlights = []
            
            # Keywords that often indicate interesting content
            highlight_keywords = [
                'funny', 'hilarious', 'amazing', 'incredible', 'wow', 'crazy',
                'important', 'key', 'main', 'point', 'remember', 'crucial',
                'story', 'happened', 'experience', 'learned', 'realized',
                'question', 'answer', 'explain', 'understand', 'think',
                'believe', 'opinion', 'feel', 'emotional', 'excited',
                'surprised', 'shocked', 'unexpected', 'interesting'
            ]
            
            # Adjust threshold based on sensitivity (higher sensitivity = lower threshold)
            score_threshold = max(1, int(5 * (1 - sensitivity)))
            
            # Analyze each segment
            for i, segment in enumerate(segments):
                text = segment['text'].lower()
                score = 0
                
                # Keyword scoring
                for keyword in highlight_keywords:
                    if keyword in text:
                        score += 1
                
                # Length scoring (prefer medium-length segments)
                duration = segment['end'] - segment['start']
                if 10 <= duration <= 60:  # 10-60 seconds is good for clips
                    score += 2
                elif 5 <= duration <= 90:
                    score += 1
                
                # Question/answer patterns
                if '?' in segment['text']:
                    score += 2
                
                # Emotional indicators (caps, exclamation)
                if '!' in segment['text'] or segment['text'].isupper():
                    score += 1
                
                # Scene change alignment (prefer segments near scene changes)
                segment_start = segment['start']
                for scene_time in scene_changes:
                    if abs(segment_start - scene_time) < 5:  # Within 5 seconds
                        score += 1
                        break
                
                # If score is high enough, consider it a highlight
                if score >= score_threshold:
                    highlights.append({
                        'start_time': segment['start'],
                        'end_time': segment['end'],
                        'text': segment['text'],
                        'score': score,
                        'title': self._generate_clip_title(segment['text']),
                        'duration': duration
                    })
            
            # Sort by score and return top highlights
            highlights.sort(key=lambda x: x['score'], reverse=True)
            
            # Merge overlapping or adjacent highlights
            merged_highlights = self._merge_highlights(highlights)
            
            # Limit to user-specified number of clips
            return merged_highlights[:max_clips]
            
        except Exception as e:
            raise Exception(f"Error finding highlights: {str(e)}")
    
    def create_interval_clips(self, video_info: Dict, interval: int, duration: int) -> List[Dict]:
        """Create clips at fixed intervals"""
        try:
            clips = []
            video_duration = video_info.get('duration', 300)  # Default 5 minutes if unknown
            
            current_time = 0
            clip_index = 1
            
            while current_time + duration <= video_duration:
                clips.append({
                    'start_time': current_time,
                    'end_time': current_time + duration,
                    'text': f"Interval clip {clip_index}",
                    'score': 5,  # Standard score for interval clips
                    'title': f"Clip {clip_index:02d}",
                    'duration': duration
                })
                
                current_time += interval
                clip_index += 1
                
                # Safety limit
                if len(clips) >= 20:
                    break
            
            return clips
            
        except Exception as e:
            raise Exception(f"Error creating interval clips: {str(e)}")
    
    def create_hybrid_clips(self, transcript: Dict, scene_changes: List[float], video_info: Dict, ai_clips: int, backup_clips: int) -> List[Dict]:
        """Create a hybrid of AI-generated and interval-based clips"""
        try:
            # Get AI-generated highlights
            ai_highlights = self.find_highlights(transcript, scene_changes, sensitivity=0.7, max_clips=ai_clips)
            
            # Get interval-based backup clips
            interval_clips = self.create_interval_clips(video_info, interval=90, duration=30)
            
            # Filter out interval clips that overlap with AI clips
            filtered_interval_clips = []
            for interval_clip in interval_clips:
                overlaps = False
                for ai_clip in ai_highlights:
                    if (interval_clip['start_time'] < ai_clip['end_time'] and 
                        interval_clip['end_time'] > ai_clip['start_time']):
                        overlaps = True
                        break
                
                if not overlaps:
                    filtered_interval_clips.append(interval_clip)
            
            # Take the requested number of backup clips
            backup_clips_selected = filtered_interval_clips[:backup_clips]
            
            # Combine and sort by start time
            all_clips = ai_highlights + backup_clips_selected
            all_clips.sort(key=lambda x: x['start_time'])
            
            return all_clips
            
        except Exception as e:
            raise Exception(f"Error creating hybrid clips: {str(e)}")
    
    def _generate_clip_title(self, text: str) -> str:
        """Generate a title for a clip based on its content"""
        # Clean and truncate text
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        
        # Take first few meaningful words
        title_words = []
        for word in words[:6]:  # Max 6 words
            if len(word) > 2 and word.lower() not in ['the', 'and', 'but', 'for', 'are', 'with']:
                title_words.append(word.capitalize())
        
        title = ' '.join(title_words) if title_words else 'Highlight'
        return title[:50]  # Max 50 characters
    
    def _merge_highlights(self, highlights: List[Dict]) -> List[Dict]:
        """Merge overlapping or adjacent highlight segments"""
        if not highlights:
            return []
        
        # Sort by start time
        highlights.sort(key=lambda x: x['start_time'])
        
        merged = []
        current = highlights[0].copy()
        
        for next_highlight in highlights[1:]:
            # If highlights overlap or are very close (within 5 seconds)
            if next_highlight['start_time'] <= current['end_time'] + 5:
                # Merge them
                current['end_time'] = max(current['end_time'], next_highlight['end_time'])
                current['text'] += ' ' + next_highlight['text']
                current['score'] = max(current['score'], next_highlight['score'])
                current['duration'] = current['end_time'] - current['start_time']
                
                # Update title if the new segment has higher score
                if next_highlight['score'] > current['score']:
                    current['title'] = next_highlight['title']
            else:
                # No overlap, add current to merged list and start new one
                merged.append(current)
                current = next_highlight.copy()
        
        # Add the last highlight
        merged.append(current)
        
        # Filter out highlights that are too short or too long
        filtered = []
        for highlight in merged:
            duration = highlight['duration']
            if 5 <= duration <= 120:  # Between 5 seconds and 2 minutes
                filtered.append(highlight)
        
        return filtered
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Basic sentiment analysis of text"""
        positive_words = [
            'good', 'great', 'awesome', 'amazing', 'excellent', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'excited', 'wonderful'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry',
            'frustrated', 'disappointed', 'worried', 'concerned'
        ]
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = positive_count / len(words)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = negative_count / len(words)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': min(confidence, 1.0),
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def extract_topics(self, transcript: Dict, num_topics: int = 5) -> List[Dict]:
        """Extract main topics from transcript using TF-IDF"""
        try:
            # Combine all text
            all_text = ' '.join([seg['text'] for seg in transcript['segments']])
            
            # Simple topic extraction using keyword frequency
            words = re.findall(r'\b\w+\b', all_text.lower())
            
            # Filter out common words
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
                'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was',
                'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
                'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
                'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
                'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
                'his', 'her', 'its', 'our', 'their', 'a', 'an'
            }
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Count word frequency
            word_counts = Counter(filtered_words)
            
            # Get top topics
            topics = []
            for word, count in word_counts.most_common(num_topics):
                topics.append({
                    'topic': word.capitalize(),
                    'frequency': count,
                    'relevance': count / len(filtered_words)
                })
            
            return topics
            
        except Exception as e:
            print(f"Error extracting topics: {str(e)}")
            return []