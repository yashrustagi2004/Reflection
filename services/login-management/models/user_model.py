"""
User Model for Login Management Service
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId


class UserModel:
    """User data model and database operations"""
    
    def __init__(self, db_collection):
        self.collection = db_collection
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create database indexes for performance"""
        if self.collection is not None:
            try:
                self.collection.create_index('email', unique=True)
                self.collection.create_index([('provider', 1), ('provider_id', 1)])
                self.collection.create_index('is_active')
            except Exception:
                pass
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new user
        
        Args:
            user_data: User information dictionary
            
        Returns:
            User ID if successful, None otherwise
        """
        try:
            user_doc = {
                "_id": ObjectId(),
                "email": user_data['email'],
                "name": user_data['name'],
                "provider": user_data['provider'],
                "provider_id": user_data['provider_id'],
                "avatar_url": user_data.get('avatar_url'),
                "profile_data": user_data.get('profile_data', {}),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc),
                "is_active": True,
                "settings": {
                    "notifications": True,
                    "data_sharing": True,
                    "theme": "light"
                },
                "uploads": {
                    "resumes": [],
                    "job_descriptions": []
                },
                "interview_history": [],
                "account_status": "active"
            }
            
            result = self.collection.insert_one(user_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = self.collection.find_one({"email": email})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception:
            return None
    
    def get_user_by_provider(self, provider: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get user by OAuth provider"""
        try:
            user = self.collection.find_one({
                "provider": provider,
                "provider_id": provider_id
            })
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception:
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            update_data['updated_at'] = datetime.now(timezone.utc)
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "last_login": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def add_upload(self, user_id: str, upload_type: str, file_info: Dict[str, Any]) -> bool:
        """Add file upload record"""
        try:
            file_info['uploaded_at'] = datetime.now(timezone.utc)
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$push": {f"uploads.{upload_type}": file_info},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error adding upload: {e}")
            return False
    
    def get_user_uploads(self, user_id: str) -> Optional[Dict[str, list]]:
        """Get user's upload history"""
        try:
            user = self.collection.find_one(
                {"_id": ObjectId(user_id)},
                {"uploads": 1}
            )
            return user.get('uploads', {}) if user else None
        except Exception:
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """
        Soft delete user (mark as inactive)
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_active": False,
                        "account_status": "deleted",
                        "deleted_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def is_user_active(self, user_id: str) -> bool:
        """Check if user account is active"""
        try:
            user = self.collection.find_one(
                {"_id": ObjectId(user_id)},
                {"is_active": 1}
            )
            return user.get('is_active', False) if user else False
        except Exception:
            return False
