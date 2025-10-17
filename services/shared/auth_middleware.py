"""
Authentication Middleware for Microservices
Handles JWT token validation and user session management
"""

import os
import jwt
import requests
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class AuthMiddleware:
    """JWT-based authentication middleware for inter-service communication"""
    
    def __init__(self, jwt_secret: Optional[str] = None):
        self.jwt_secret = jwt_secret or os.getenv('JWT_SECRET', 'your-jwt-secret-change-this-in-production')
        self.jwt_algorithm = 'HS256'
        self.token_expiry_hours = int(os.getenv('JWT_EXPIRY_HOURS', '24'))
    
    def generate_token(self, user_id: str, user_email: str, additional_claims: Optional[Dict] = None) -> str:
        """
        Generate a JWT token for authenticated user
        
        Args:
            user_id: User's unique identifier
            user_email: User's email address
            additional_claims: Optional additional claims to include in token
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'email': user_email,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, f):
        """
        Decorator to require authentication for API endpoints
        Expects JWT token in Authorization header as 'Bearer <token>'
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({
                    'success': False,
                    'error': 'Missing authorization header'
                }), 401
            
            # Extract token from "Bearer <token>" format
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format'
                }), 401
            
            token = parts[1]
            payload = self.verify_token(token)
            
            if not payload:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired token'
                }), 401
            
            # Add user info to request context
            request.user_id = payload.get('user_id')
            request.user_email = payload.get('email')
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def validate_service_token(self, token: str, service_name: str) -> bool:
        """
        Validate inter-service communication token
        
        Args:
            token: Service token
            service_name: Name of the calling service
            
        Returns:
            True if token is valid, False otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return False
        
        return payload.get('service') == service_name
    
    def generate_service_token(self, service_name: str) -> str:
        """
        Generate a token for inter-service communication
        
        Args:
            service_name: Name of the service
            
        Returns:
            JWT token for service authentication
        """
        payload = {
            'service': service_name,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
