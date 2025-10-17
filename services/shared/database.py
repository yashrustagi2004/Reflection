"""
Shared Database Configuration
Centralized MongoDB connection management
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Singleton database connection manager"""
    
    _instance = None
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            self.database_name = os.getenv('DATABASE_NAME', 'Reflection')
            self.initialized = False
    
    def connect(self) -> bool:
        """Establish database connection"""
        if self._client is not None:
            return True
        
        try:
            self._client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
                maxPoolSize=50,
                minPoolSize=5,
                maxIdleTimeMS=30000,
            )
            
            # Test connection
            self._client.admin.command('ping')
            self._database = self._client[self.database_name]
            
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    def get_database(self) -> Optional[Database]:
        """Get database instance"""
        if not self.initialized:
            self.connect()
        return self._database
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get specific collection"""
        db = self.get_database()
        if db is not None:
            return db[collection_name]
        return None
    
    def disconnect(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            self.initialized = False
            logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_database() -> Optional[Database]:
    """Get database instance"""
    return db_manager.get_database()


def get_collection(collection_name: str) -> Optional[Collection]:
    """Get specific collection"""
    return db_manager.get_collection(collection_name)
