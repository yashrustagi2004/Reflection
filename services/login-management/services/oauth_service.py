"""
OAuth Service for Google and GitHub Authentication
"""

import os
import secrets
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode


class OAuthService:
    """Handles OAuth authentication with Google and GitHub"""
    
    def __init__(self):
        # Google OAuth Configuration
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/google/callback')
        
        # GitHub OAuth Configuration
        self.github_client_id = os.getenv('GITHUB_CLIENT_ID')
        self.github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        self.github_redirect_uri = os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:5000/api/auth/github/callback')
        
        # OAuth URLs
        self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        self.github_auth_url = "https://github.com/login/oauth/authorize"
        self.github_token_url = "https://github.com/login/oauth/access_token"
        self.github_userinfo_url = "https://api.github.com/user"
    
    def get_config_status(self) -> Dict[str, bool]:
        """Check which OAuth providers are configured"""
        return {
            'google': bool(self.google_client_id and self.google_client_secret),
            'github': bool(self.github_client_id and self.github_client_secret)
        }
    
    # ==================== Google OAuth ====================
    
    def get_google_auth_url(self) -> Tuple[str, str]:
        """
        Generate Google OAuth authorization URL
        
        Returns:
            Tuple of (auth_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': self.google_redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{self.google_auth_url}?{urlencode(params)}"
        return auth_url, state
    
    def handle_google_callback(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange Google authorization code for user information
        
        Args:
            code: Authorization code from Google
            
        Returns:
            User data dictionary or None if failed
        """
        try:
            # Exchange code for access token
            token_data = {
                'code': code,
                'client_id': self.google_client_id,
                'client_secret': self.google_client_secret,
                'redirect_uri': self.google_redirect_uri,
                'grant_type': 'authorization_code'
            }
            
            token_response = requests.post(
                self.google_token_url,
                data=token_data,
                timeout=10
            )
            
            if token_response.status_code != 200:
                return None
            
            token_json = token_response.json()
            access_token = token_json.get('access_token')
            
            if not access_token:
                return None
            
            # Get user information
            headers = {'Authorization': f'Bearer {access_token}'}
            userinfo_response = requests.get(
                self.google_userinfo_url,
                headers=headers,
                timeout=10
            )
            
            if userinfo_response.status_code != 200:
                return None
            
            userinfo = userinfo_response.json()
            
            return {
                'email': userinfo.get('email'),
                'name': userinfo.get('name'),
                'provider': 'google',
                'provider_id': userinfo.get('id'),
                'avatar_url': userinfo.get('picture'),
                'profile_data': userinfo
            }
            
        except Exception as e:
            print(f"Error in Google OAuth: {e}")
            return None
    
    # ==================== GitHub OAuth ====================
    
    def get_github_auth_url(self) -> Tuple[str, str]:
        """
        Generate GitHub OAuth authorization URL
        
        Returns:
            Tuple of (auth_url, state)
        """
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.github_client_id,
            'redirect_uri': self.github_redirect_uri,
            'scope': 'user:email',
            'state': state
        }
        
        auth_url = f"{self.github_auth_url}?{urlencode(params)}"
        return auth_url, state
    
    def handle_github_callback(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange GitHub authorization code for user information
        
        Args:
            code: Authorization code from GitHub
            
        Returns:
            User data dictionary or None if failed
        """
        try:
            # Exchange code for access token
            token_data = {
                'client_id': self.github_client_id,
                'client_secret': self.github_client_secret,
                'code': code,
                'redirect_uri': self.github_redirect_uri
            }
            
            headers = {'Accept': 'application/json'}
            token_response = requests.post(
                self.github_token_url,
                data=token_data,
                headers=headers,
                timeout=10
            )
            
            if token_response.status_code != 200:
                return None
            
            token_json = token_response.json()
            access_token = token_json.get('access_token')
            
            if not access_token:
                return None
            
            # Get user information
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/vnd.github+json'
            }
            userinfo_response = requests.get(
                self.github_userinfo_url,
                headers=headers,
                timeout=10
            )
            
            if userinfo_response.status_code != 200:
                return None
            
            userinfo = userinfo_response.json()
            
            # Get user's primary email if not public
            email = userinfo.get('email')
            if not email:
                email_response = requests.get(
                    'https://api.github.com/user/emails',
                    headers=headers,
                    timeout=10
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next(
                        (e['email'] for e in emails if e['primary']),
                        None
                    )
                    email = primary_email or emails[0]['email'] if emails else None
            
            return {
                'email': email,
                'name': userinfo.get('name') or userinfo.get('login'),
                'provider': 'github',
                'provider_id': str(userinfo.get('id')),
                'avatar_url': userinfo.get('avatar_url'),
                'profile_data': userinfo
            }
            
        except Exception as e:
            print(f"Error in GitHub OAuth: {e}")
            return None
