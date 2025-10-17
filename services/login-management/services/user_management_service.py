"""
User Management Service
Business logic for user operations
"""

from typing import Optional, Dict, Any


class UserManagementService:
    """Service for user management operations"""
    
    def __init__(self, user_model):
        self.user_model = user_model
    
    def create_or_update_user(self, oauth_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new user or update existing user from OAuth data
        
        Args:
            oauth_data: User data from OAuth provider
            
        Returns:
            User ID if successful, None otherwise
        """
        # Check if user exists
        user = self.user_model.get_user_by_email(oauth_data['email'])
        
        if not user:
            user = self.user_model.get_user_by_provider(
                oauth_data['provider'],
                oauth_data['provider_id']
            )
        
        if user:
            # Update existing user
            self.user_model.update_last_login(user['_id'])
            
            # Update profile and provider info (user might switch OAuth providers)
            update_data = {
                'name': oauth_data['name'],
                'avatar_url': oauth_data.get('avatar_url'),
                'provider': oauth_data['provider'],
                'provider_id': oauth_data['provider_id']
            }
            self.user_model.update_user(user['_id'], update_data)
            
            return user['_id']
        else:
            # Create new user
            return self.user_model.create_user(oauth_data)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.user_model.get_user_by_id(user_id)
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        return self.user_model.update_user(user_id, update_data)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user account"""
        return self.user_model.delete_user(user_id)
    
    def add_upload_record(self, user_id: str, file_type: str, file_info: Dict[str, Any]) -> bool:
        """Add file upload record to user profile"""
        upload_type = 'resumes' if 'resume' in file_type else 'job_descriptions'
        return self.user_model.add_upload(user_id, upload_type, file_info)
    
    def get_user_uploads(self, user_id: str) -> Optional[Dict[str, list]]:
        """Get user's upload history"""
        return self.user_model.get_user_uploads(user_id)
    
    @staticmethod
    def sanitize_user_data(user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from user object before sending to client
        
        Args:
            user: User data dictionary
            
        Returns:
            Sanitized user data
        """
        safe_fields = [
            '_id', 'email', 'name', 'avatar_url', 'provider',
            'created_at', 'last_login', 'settings', 'uploads'
        ]
        
        return {k: v for k, v in user.items() if k in safe_fields}
