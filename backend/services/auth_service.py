"""
OAuth Authentication Service
Handles Google and GitHub OAuth authentication
"""

import os
import secrets
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import jwt
from datetime import datetime, timedelta, timezone


class OAuthConfig:
    """OAuth configuration management"""
    
    def __init__(self):
        # Google OAuth
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
        
        # GitHub OAuth
        self.github_client_id = os.getenv('GITHUB_CLIENT_ID')
        self.github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        self.github_redirect_uri = os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:5000/auth/github/callback')
        
        # JWT Secret
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-jwt-secret-key-change-this-in-production')
        self.jwt_expiry_hours = int(os.getenv('JWT_EXPIRY_HOURS', '24'))


class GoogleOAuth:
    """Google OAuth handler"""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_auth_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            'client_id': self.config.google_client_id,
            'redirect_uri': self.config.google_redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'client_id': self.config.google_client_id,
                'client_secret': self.config.google_client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.google_redirect_uri
            }
            
            response = requests.post(self.token_url, data=data, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error exchanging Google code for token: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.user_info_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                'provider': 'google',
                'provider_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'avatar_url': user_data.get('picture'),
                'profile_data': user_data
            }
            
        except Exception as e:
            print(f"Error getting Google user info: {e}")
            return None


class GitHubOAuth:
    """GitHub OAuth handler"""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_info_url = "https://api.github.com/user"
        self.user_email_url = "https://api.github.com/user/emails"
    
    def get_auth_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            'client_id': self.config.github_client_id,
            'redirect_uri': self.config.github_redirect_uri,
            'scope': 'user:email',
            'state': state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'client_id': self.config.github_client_id,
                'client_secret': self.config.github_client_secret,
                'code': code
            }
            
            headers = {'Accept': 'application/json'}
            response = requests.post(self.token_url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error exchanging GitHub code for token: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from GitHub"""
        try:
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get user profile
            user_response = requests.get(self.user_info_url, headers=headers, timeout=10)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get user email (primary email)
            email_response = requests.get(self.user_email_url, headers=headers, timeout=10)
            email_response.raise_for_status()
            emails = email_response.json()
            
            primary_email = None
            for email in emails:
                if email.get('primary') and email.get('verified'):
                    primary_email = email.get('email')
                    break
            
            return {
                'provider': 'github',
                'provider_id': str(user_data.get('id')),
                'email': primary_email or user_data.get('email'),
                'name': user_data.get('name') or user_data.get('login'),
                'avatar_url': user_data.get('avatar_url'),
                'profile_data': user_data
            }
            
        except Exception as e:
            print(f"Error getting GitHub user info: {e}")
            return None


class JWTManager:
    """JWT token management"""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
    
    def generate_token(self, user_id: str, user_email: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'email': user_email,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=self.config.jwt_expiry_hours)
        }
        
        return jwt.encode(payload, self.config.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid JWT token")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token if it's still valid"""
        payload = self.verify_token(token)
        if payload:
            return self.generate_token(payload['user_id'], payload['email'])
        return None


class AuthenticationService:
    """Main authentication service"""
    
    def __init__(self):
        self.config = OAuthConfig()
        self.google_oauth = GoogleOAuth(self.config)
        self.github_oauth = GitHubOAuth(self.config)
        self.jwt_manager = JWTManager(self.config)
    
    def generate_state(self) -> str:
        """Generate secure state parameter for OAuth"""
        return secrets.token_urlsafe(32)
    
    def get_google_auth_url(self, state: str) -> str:
        """Get Google OAuth authorization URL"""
        return self.google_oauth.get_auth_url(state)
    
    def get_github_auth_url(self, state: str) -> str:
        """Get GitHub OAuth authorization URL"""
        return self.github_oauth.get_auth_url(state)
    
    def authenticate_google(self, code: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Google OAuth"""
        # Exchange code for token
        token_data = self.google_oauth.exchange_code_for_token(code)
        if not token_data or 'access_token' not in token_data:
            return None
        
        # Get user information
        user_info = self.google_oauth.get_user_info(token_data['access_token'])
        return user_info
    
    def authenticate_github(self, code: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with GitHub OAuth"""
        # Exchange code for token
        token_data = self.github_oauth.exchange_code_for_token(code)
        if not token_data or 'access_token' not in token_data:
            return None
        
        # Get user information
        user_info = self.github_oauth.get_user_info(token_data['access_token'])
        return user_info
    
    def create_session_token(self, user_id: str, user_email: str) -> str:
        """Create session token for authenticated user"""
        return self.jwt_manager.generate_token(user_id, user_email)
    
    def verify_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify session token"""
        return self.jwt_manager.verify_token(token)
    
    def is_configured(self) -> Dict[str, bool]:
        """Check if OAuth providers are properly configured"""
        return {
            'google': bool(self.config.google_client_id and self.config.google_client_secret),
            'github': bool(self.config.github_client_id and self.config.github_client_secret)
        }