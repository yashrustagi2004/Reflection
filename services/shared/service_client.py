"""
Service Client for Inter-Microservice Communication
Provides secure HTTP client for service-to-service calls
"""

import os
import requests
from typing import Optional, Dict, Any
from .auth_middleware import AuthMiddleware


class ServiceClient:
    """HTTP client for secure inter-service communication"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.auth = AuthMiddleware()
        self.timeout = 30  # seconds
        
        # Service URLs - read from environment or use defaults
        self.service_urls = {
            'login-management': os.getenv('LOGIN_MANAGEMENT_URL', 'http://localhost:5001'),
            'file-parsing': os.getenv('FILE_PARSING_URL', 'http://localhost:5002'),
            'question-answer-generation': os.getenv('QA_GENERATION_URL', 'http://localhost:5003'),
            'answer-analysis': os.getenv('ANSWER_ANALYSIS_URL', 'http://localhost:5004'),
            'resources': os.getenv('RESOURCES_URL', 'http://localhost:5005'),
        }
    
    def _get_service_headers(self, user_token: Optional[str] = None) -> Dict[str, str]:
        """
        Generate headers for service request
        
        Args:
            user_token: Optional user JWT token to forward
            
        Returns:
            Headers dictionary
        """
        headers = {
            'Content-Type': 'application/json',
            'X-Service-Name': self.service_name,
        }
        
        # Include service authentication token
        service_token = self.auth.generate_service_token(self.service_name)
        headers['X-Service-Token'] = service_token
        
        # Forward user token if provided
        if user_token:
            headers['Authorization'] = f'Bearer {user_token}'
        
        return headers
    
    def get(self, service: str, endpoint: str, user_token: Optional[str] = None, 
            params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request to another service
        
        Args:
            service: Target service name
            endpoint: API endpoint path
            user_token: Optional user JWT token
            params: Optional query parameters
            
        Returns:
            Response data as dictionary
        """
        try:
            url = f"{self.service_urls.get(service)}{endpoint}"
            headers = self._get_service_headers(user_token)
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Service communication error: {str(e)}'
            }
    
    def post(self, service: str, endpoint: str, data: Dict[str, Any] = None, 
             user_token: Optional[str] = None, files: Dict = None) -> Dict[str, Any]:
        """
        Make POST request to another service
        
        Args:
            service: Target service name
            endpoint: API endpoint path
            data: Request body data (for JSON requests)
            user_token: Optional user JWT token
            files: Optional files for multipart form data
            
        Returns:
            Response data as dictionary
        """
        try:
            url = f"{self.service_urls.get(service)}{endpoint}"
            headers = self._get_service_headers(user_token)
            
            # Handle file uploads differently
            if files:
                # Remove Content-Type for multipart form data
                headers.pop('Content-Type', None)
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data,  # Additional form data if needed
                    timeout=self.timeout
                )
            else:
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Service communication error: {str(e)}'
            }
    
    def put(self, service: str, endpoint: str, data: Dict[str, Any],
            user_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Make PUT request to another service
        
        Args:
            service: Target service name
            endpoint: API endpoint path
            data: Request body data
            user_token: Optional user JWT token
            
        Returns:
            Response data as dictionary
        """
        try:
            url = f"{self.service_urls.get(service)}{endpoint}"
            headers = self._get_service_headers(user_token)
            
            response = requests.put(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Service communication error: {str(e)}'
            }
    
    def delete(self, service: str, endpoint: str, user_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Make DELETE request to another service
        
        Args:
            service: Target service name
            endpoint: API endpoint path
            user_token: Optional user JWT token
            
        Returns:
            Response data as dictionary
        """
        try:
            url = f"{self.service_urls.get(service)}{endpoint}"
            headers = self._get_service_headers(user_token)
            
            response = requests.delete(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Service communication error: {str(e)}'
            }
