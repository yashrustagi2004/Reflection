"""
User Model for MongoDB
Defines the user schema and database operations
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
import bcrypt


class User:
    """User model for storing user information and authentication data"""
    
    def __init__(self, db_collection):
        self.collection = db_collection
    
    @staticmethod
    def create_user_document(
        email: str,
        name: str,
        provider: str,  # 'google' or 'github'
        provider_id: str,
        avatar_url: Optional[str] = None,
        profile_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new user document"""
        return {
            "_id": ObjectId(),
            "email": email,
            "name": name,
            "provider": provider,
            "provider_id": provider_id,
            "avatar_url": avatar_url,
            "profile_data": profile_data or {},
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
            "account_status": "active"  # active, suspended, deleted
        }
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new user in the database
        Returns user ID if successful, None if failed
        """
        try:
            # Check if user already exists
            existing_user = self.collection.find_one({
                "$or": [
                    {"email": user_data["email"]},
                    {"provider_id": user_data["provider_id"], "provider": user_data["provider"]}
                ]
            })
            
            if existing_user:
                # Update last login for existing user
                self.collection.update_one(
                    {"_id": existing_user["_id"]},
                    {
                        "$set": {
                            "last_login": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                return str(existing_user["_id"])
            
            # Create new user document
            user_doc = self.create_user_document(**user_data)
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
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = self.collection.find_one({"email": email})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None
    
    def get_user_by_provider(self, provider: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get user by OAuth provider and provider ID"""
        try:
            user = self.collection.find_one({
                "provider": provider,
                "provider_id": provider_id
            })
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            print(f"Error fetching user by provider: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            update_data["updated_at"] = datetime.now(timezone.utc)
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
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
    
    def add_upload_record(self, user_id: str, upload_type: str, file_info: Dict[str, Any]) -> bool:
        """Add upload record to user's profile"""
        try:
            upload_record = {
                "filename": file_info.get("filename"),
                "original_name": file_info.get("original_name"),
                "file_path": file_info.get("file_path"),
                "file_size": file_info.get("file_size"),
                "upload_date": datetime.now(timezone.utc),
                "file_type": file_info.get("file_type")
            }
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$push": {f"uploads.{upload_type}": upload_record},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding upload record: {e}")
            return False
    
    def get_user_uploads(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's upload history"""
        try:
            user = self.collection.find_one(
                {"_id": ObjectId(user_id)},
                {"uploads": 1}
            )
            return user.get("uploads") if user else None
        except Exception as e:
            print(f"Error fetching user uploads: {e}")
            return None
    
    def soft_delete_user(self, user_id: str) -> bool:
        """Soft delete user (mark as deleted instead of removing)"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "account_status": "deleted",
                        "is_active": False,
                        "deleted_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error soft deleting user: {e}")
            return False
    
    def hard_delete_user(self, user_id: str) -> bool:
        """Permanently delete user from database"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error hard deleting user: {e}")
            return False
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        try:
            pipeline = [
                {"$match": {"_id": ObjectId(user_id)}},
                {
                    "$project": {
                        "total_resumes": {"$size": "$uploads.resumes"},
                        "total_job_descriptions": {"$size": "$uploads.job_descriptions"},
                        "total_interviews": {"$size": "$interview_history"},
                        "member_since": "$created_at",
                        "last_login": "$last_login"
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            return result[0] if result else None
        except Exception as e:
            print(f"Error fetching user stats: {e}")
            return None