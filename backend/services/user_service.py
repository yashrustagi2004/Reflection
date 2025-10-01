"""
User Service
Handles user-related business logic
"""

from typing import Optional, Dict, Any
from backend.models.user import User
from backend.config.database import get_users_collection
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations"""
    
    def __init__(self):
        self.users_collection = None
        self.user_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the user service with database connection"""
        try:
            self.users_collection = get_users_collection()
            if self.users_collection is not None:
                self.user_model = User(self.users_collection)
                logger.info("User service initialized successfully")
            else:
                logger.error("Failed to initialize user service - no database connection")
        except Exception as e:
            logger.error(f"Error initializing user service: {e}")
    
    def _ensure_initialized(self):
        """Ensure the service is initialized, retry if not"""
        if self.user_model is None:
            self._initialize()
        return self.user_model is not None
    
    def create_or_update_user_from_oauth(self, oauth_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new user or update existing user from OAuth data
        Returns user ID if successful
        """
        if not self._ensure_initialized():
            logger.error("User model not initialized")
            return None
        
        try:
            # Validate required fields
            required_fields = ['email', 'name', 'provider', 'provider_id']
            for field in required_fields:
                if not oauth_data.get(field):
                    logger.error(f"Missing required field: {field}")
                    return None
            
            # Check if user exists by email or provider ID
            existing_user = self.user_model.get_user_by_email(oauth_data['email'])
            if not existing_user:
                existing_user = self.user_model.get_user_by_provider(
                    oauth_data['provider'], 
                    oauth_data['provider_id']
                )
            
            if existing_user:
                # Update existing user
                update_data = {
                    'name': oauth_data['name'],
                    'avatar_url': oauth_data.get('avatar_url'),
                    'profile_data': oauth_data.get('profile_data', {}),
                    'last_login': oauth_data.get('last_login')
                }
                
                success = self.user_model.update_last_login(existing_user['_id'])
                if success:
                    # Update other fields if they've changed
                    self.user_model.update_user(existing_user['_id'], update_data)
                    return existing_user['_id']
                else:
                    logger.error("Failed to update user login time")
                    return None
            else:
                # Create new user
                user_id = self.user_model.create_user(oauth_data)
                if user_id:
                    logger.info(f"Created new user: {user_id}")
                    return user_id
                else:
                    logger.error("Failed to create new user")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in create_or_update_user_from_oauth: {e}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        if not self._ensure_initialized():
            return None
        
        try:
            user = self.user_model.get_user_by_id(user_id)
            if user and user.get('account_status') == 'active':
                # Remove sensitive information
                safe_profile = {
                    'id': user['_id'],
                    'email': user['email'],
                    'name': user['name'],
                    'avatar_url': user.get('avatar_url'),
                    'provider': user['provider'],
                    'created_at': user['created_at'],
                    'last_login': user['last_login'],
                    'settings': user.get('settings', {}),
                    'uploads': user.get('uploads', {'resumes': [], 'job_descriptions': []})
                }
                return safe_profile
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def update_user_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """Update user settings"""
        if not self._ensure_initialized():
            return False
        
        try:
            # Validate settings - now only theme is allowed
            allowed_settings = {'theme'}
            filtered_settings = {k: v for k, v in settings.items() if k in allowed_settings}
            
            # Validate theme value
            if 'theme' in filtered_settings and filtered_settings['theme'] not in ['light', 'dark']:
                filtered_settings['theme'] = 'light'  # Default to light
            
            if not filtered_settings:
                return False
            
            return self.user_model.update_user(user_id, {'settings': filtered_settings})
        except Exception as e:
            logger.error(f"Error updating user settings: {e}")
            return False
    
    def add_user_upload(self, user_id: str, upload_type: str, file_info: Dict[str, Any]) -> bool:
        """Add upload record to user profile"""
        if not self._ensure_initialized():
            return False
        
        try:
            valid_types = ['resumes', 'job_descriptions']
            if upload_type not in valid_types:
                logger.error(f"Invalid upload type: {upload_type}")
                return False
            
            return self.user_model.add_upload_record(user_id, upload_type, file_info)
        except Exception as e:
            logger.error(f"Error adding user upload: {e}")
            return False
    
    def get_user_uploads(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's upload history"""
        if not self._ensure_initialized():
            return None
        
        try:
            return self.user_model.get_user_uploads(user_id)
        except Exception as e:
            logger.error(f"Error getting user uploads: {e}")
            return None
    
    def get_user_statistics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        if not self._ensure_initialized():
            return None
        
        try:
            return self.user_model.get_user_stats(user_id)
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return None
    
    def delete_user_account(self, user_id: str, hard_delete: bool = False) -> bool:
        """
        Delete user account
        Args:
            user_id: User ID to delete
            hard_delete: If True, permanently delete. If False, soft delete (mark as deleted)
        """
        if not self._ensure_initialized():
            return False
        
        try:
            if hard_delete:
                # Permanently delete user and all associated data
                success = self.user_model.hard_delete_user(user_id)
                if success:
                    logger.info(f"User {user_id} permanently deleted")
                    # TODO: Delete user files from storage
                    self._delete_user_files(user_id)
                return success
            else:
                # Soft delete - mark as deleted but keep data
                success = self.user_model.soft_delete_user(user_id)
                if success:
                    logger.info(f"User {user_id} soft deleted")
                return success
        except Exception as e:
            logger.error(f"Error deleting user account: {e}")
            return False
    
    def _delete_user_files(self, user_id: str):
        """Delete user's uploaded files from storage"""
        try:
            # Get user's file information
            uploads = self.get_user_uploads(user_id)
            if not uploads:
                return
            
            import os
            
            # Delete resume files
            for resume in uploads.get('resumes', []):
                file_path = resume.get('file_path')
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted resume file: {file_path}")
            
            # Delete job description files
            for jd in uploads.get('job_descriptions', []):
                file_path = jd.get('file_path')
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted job description file: {file_path}")
                    
        except Exception as e:
            logger.error(f"Error deleting user files: {e}")
    
    def reactivate_user(self, user_id: str) -> bool:
        """Reactivate a soft-deleted user account"""
        if not self._ensure_initialized():
            return False
        
        try:
            update_data = {
                'account_status': 'active',
                'is_active': True,
                'deleted_at': None
            }
            return self.user_model.update_user(user_id, update_data)
        except Exception as e:
            logger.error(f"Error reactivating user: {e}")
            return False
    
    def is_user_active(self, user_id: str) -> bool:
        """Check if user account is active"""
        if not self._ensure_initialized():
            return False
        
        try:
            user = self.user_model.get_user_by_id(user_id)
            return user and user.get('account_status') == 'active' and user.get('is_active', False)
        except Exception as e:
            logger.error(f"Error checking user status: {e}")
            return False