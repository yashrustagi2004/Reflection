"""
Database Configuration and Connection Manager
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('DATABASE_NAME', 'Reflection')
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,  # 10 second connection timeout
                socketTimeoutMS=20000,   # 20 second socket timeout
                maxPoolSize=50,          # Maximum connection pool size
                minPoolSize=5,           # Minimum connection pool size
                maxIdleTimeMS=30000,     # Close connections after 30 seconds of inactivity
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a collection from the database"""
        if self.database is None:
            logger.error("Database not connected")
            return None
        
        return self.database[collection_name]
    
    def create_indexes(self):
        """Create necessary database indexes for better performance"""
        try:
            users_collection = self.get_collection('users')
            
            if users_collection is not None:
                # Create indexes for users collection
                users_collection.create_index("email", unique=True)
                users_collection.create_index([("provider", 1), ("provider_id", 1)], unique=True)
                users_collection.create_index("created_at")
                users_collection.create_index("last_login")
                users_collection.create_index("account_status")
                
                logger.info("Database indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health and connection status"""
        try:
            if self.client is None:
                return {"status": "error", "message": "No database connection"}
            
            # Ping database
            self.client.admin.command('ping')
            
            # Get server info
            server_info = self.client.server_info()
            
            # Get database stats
            db_stats = self.database.command("dbstats")
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "mongodb_version": server_info.get("version"),
                "collections": len(self.database.list_collection_names()),
                "storage_size": db_stats.get("storageSize", 0),
                "data_size": db_stats.get("dataSize", 0)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global database instance
db_config = DatabaseConfig()


def get_database() -> Optional[Database]:
    """Get database instance"""
    return db_config.database


def get_users_collection() -> Optional[Collection]:
    """Get users collection"""
    return db_config.get_collection('users')


def init_database() -> bool:
    """Initialize database connection and setup"""
    success = db_config.connect()
    if success:
        db_config.create_indexes()
    return success


def close_database():
    """Close database connection"""
    db_config.disconnect()