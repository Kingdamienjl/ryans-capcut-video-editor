"""
Social Media Integration Manager for Athena Video Editor
Handles API connections and uploads to various platforms
"""

import os
import json
import requests
from typing import Dict, List, Optional
from pathlib import Path

class SocialMediaManager:
    def __init__(self):
        self.config_dir = Path.home() / ".athena_video_editor"
        self.config_dir.mkdir(exist_ok=True)
        self.credentials_file = self.config_dir / "social_credentials.json"
        self.credentials = self.load_credentials()
        
    def load_credentials(self) -> Dict:
        """Load stored social media credentials"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading credentials: {e}")
        return {}
    
    def save_credentials(self, platform: str, credentials: Dict):
        """Save credentials for a platform"""
        try:
            self.credentials[platform] = credentials
            with open(self.credentials_file, 'w') as f:
                json.dump(self.credentials, f, indent=2)
        except Exception as e:
            print(f"Error saving credentials: {e}")
    
    def setup_youtube_api(self, api_key: str, client_id: str, client_secret: str) -> bool:
        """Setup YouTube API credentials"""
        try:
            credentials = {
                'api_key': api_key,
                'client_id': client_id,
                'client_secret': client_secret
            }
            self.save_credentials('youtube', credentials)
            return True
        except Exception as e:
            print(f"Error setting up YouTube API: {e}")
            return False
    
    def setup_tiktok_api(self, client_key: str, client_secret: str) -> bool:
        """Setup TikTok API credentials"""
        try:
            credentials = {
                'client_key': client_key,
                'client_secret': client_secret
            }
            self.save_credentials('tiktok', credentials)
            return True
        except Exception as e:
            print(f"Error setting up TikTok API: {e}")
            return False
    
    def setup_instagram_api(self, access_token: str, business_account_id: str) -> bool:
        """Setup Instagram Basic Display API credentials"""
        try:
            credentials = {
                'access_token': access_token,
                'business_account_id': business_account_id
            }
            self.save_credentials('instagram', credentials)
            return True
        except Exception as e:
            print(f"Error setting up Instagram API: {e}")
            return False
    
    def setup_twitter_api(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str) -> bool:
        """Setup Twitter API credentials"""
        try:
            credentials = {
                'api_key': api_key,
                'api_secret': api_secret,
                'access_token': access_token,
                'access_token_secret': access_token_secret
            }
            self.save_credentials('twitter', credentials)
            return True
        except Exception as e:
            print(f"Error setting up Twitter API: {e}")
            return False
    
    def test_platform_connection(self, platform: str) -> bool:
        """Test connection to a social media platform"""
        if platform not in self.credentials:
            return False
            
        try:
            if platform == 'youtube':
                return self._test_youtube_connection()
            elif platform == 'tiktok':
                return self._test_tiktok_connection()
            elif platform == 'instagram':
                return self._test_instagram_connection()
            elif platform == 'twitter':
                return self._test_twitter_connection()
            else:
                return False
        except Exception as e:
            print(f"Error testing {platform} connection: {e}")
            return False
    
    def _test_youtube_connection(self) -> bool:
        """Test YouTube API connection"""
        try:
            creds = self.credentials.get('youtube', {})
            api_key = creds.get('api_key')
            if not api_key:
                return False
                
            # Test API call to YouTube
            url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true&key={api_key}"
            response = requests.get(url)
            return response.status_code == 200
        except:
            return False
    
    def _test_tiktok_connection(self) -> bool:
        """Test TikTok API connection"""
        try:
            creds = self.credentials.get('tiktok', {})
            client_key = creds.get('client_key')
            if not client_key:
                return False
            # TikTok API test would go here
            return True  # Placeholder
        except:
            return False
    
    def _test_instagram_connection(self) -> bool:
        """Test Instagram API connection"""
        try:
            creds = self.credentials.get('instagram', {})
            access_token = creds.get('access_token')
            if not access_token:
                return False
                
            # Test Instagram Basic Display API
            url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
            response = requests.get(url)
            return response.status_code == 200
        except:
            return False
    
    def _test_twitter_connection(self) -> bool:
        """Test Twitter API connection"""
        try:
            creds = self.credentials.get('twitter', {})
            api_key = creds.get('api_key')
            if not api_key:
                return False
            # Twitter API test would go here
            return True  # Placeholder
        except:
            return False
    
    def upload_to_platform(self, platform: str, video_path: str, title: str, description: str, tags: List[str] = None) -> bool:
        """Upload video to specified platform"""
        if platform not in self.credentials:
            raise Exception(f"No credentials found for {platform}")
            
        try:
            if platform == 'youtube':
                return self._upload_to_youtube(video_path, title, description, tags)
            elif platform == 'tiktok':
                return self._upload_to_tiktok(video_path, title, description, tags)
            elif platform == 'instagram':
                return self._upload_to_instagram(video_path, title, description, tags)
            elif platform == 'twitter':
                return self._upload_to_twitter(video_path, title, description, tags)
            else:
                raise Exception(f"Unsupported platform: {platform}")
        except Exception as e:
            print(f"Error uploading to {platform}: {e}")
            return False
    
    def _upload_to_youtube(self, video_path: str, title: str, description: str, tags: List[str] = None) -> bool:
        """Upload video to YouTube Shorts"""
        # This would implement YouTube Data API v3 upload
        # Requires OAuth2 flow and proper authentication
        print(f"YouTube upload: {title} - Feature requires OAuth2 setup")
        return False  # Placeholder
    
    def _upload_to_tiktok(self, video_path: str, title: str, description: str, tags: List[str] = None) -> bool:
        """Upload video to TikTok"""
        # This would implement TikTok Content Posting API
        print(f"TikTok upload: {title} - Feature requires API approval")
        return False  # Placeholder
    
    def _upload_to_instagram(self, video_path: str, title: str, description: str, tags: List[str] = None) -> bool:
        """Upload video to Instagram Reels"""
        # This would implement Instagram Content Publishing API
        print(f"Instagram upload: {title} - Feature requires Business account")
        return False  # Placeholder
    
    def _upload_to_twitter(self, video_path: str, title: str, description: str, tags: List[str] = None) -> bool:
        """Upload video to Twitter/X"""
        # This would implement Twitter API v2 media upload
        print(f"Twitter upload: {title} - Feature requires API v2 access")
        return False  # Placeholder
    
    def get_platform_requirements(self, platform: str) -> Dict:
        """Get API requirements for each platform"""
        requirements = {
            'youtube': {
                'name': 'YouTube Data API v3',
                'requirements': [
                    'Google Cloud Console project',
                    'YouTube Data API v3 enabled',
                    'OAuth2 client credentials',
                    'Channel verification required'
                ],
                'setup_url': 'https://console.cloud.google.com/',
                'docs_url': 'https://developers.google.com/youtube/v3'
            },
            'tiktok': {
                'name': 'TikTok Content Posting API',
                'requirements': [
                    'TikTok for Developers account',
                    'App approval required',
                    'Content Posting API access',
                    'Business verification may be required'
                ],
                'setup_url': 'https://developers.tiktok.com/',
                'docs_url': 'https://developers.tiktok.com/doc/content-posting-api-get-started'
            },
            'instagram': {
                'name': 'Instagram Content Publishing API',
                'requirements': [
                    'Facebook Developer account',
                    'Instagram Business account',
                    'Facebook App with Instagram permissions',
                    'Content Publishing API access'
                ],
                'setup_url': 'https://developers.facebook.com/',
                'docs_url': 'https://developers.facebook.com/docs/instagram-api'
            },
            'twitter': {
                'name': 'Twitter API v2',
                'requirements': [
                    'Twitter Developer account',
                    'API v2 access (Essential/Elevated)',
                    'App authentication',
                    'Media upload permissions'
                ],
                'setup_url': 'https://developer.twitter.com/',
                'docs_url': 'https://developer.twitter.com/en/docs/twitter-api'
            },
            'facebook': {
                'name': 'Facebook Graph API',
                'requirements': [
                    'Facebook Developer account',
                    'Facebook App',
                    'Pages API permissions',
                    'Video upload permissions'
                ],
                'setup_url': 'https://developers.facebook.com/',
                'docs_url': 'https://developers.facebook.com/docs/graph-api'
            }
        }
        return requirements.get(platform, {})