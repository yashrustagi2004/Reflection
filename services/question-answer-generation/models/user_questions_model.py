"""
User Questions Model
MongoDB schema for storing user-specific interview questions
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pymongo.collection import Collection
from bson import ObjectId
import logging

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from shared.database import get_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserQuestionsModel:
    """Model for managing user-specific interview questions"""
    
    COLLECTION_NAME = 'user_questions'
    
    @staticmethod
    def get_collection() -> Optional[Collection]:
        """Get the user_questions collection"""
        return get_collection(UserQuestionsModel.COLLECTION_NAME)
    
    @staticmethod
    def create_user_questions(
        user_id: str,
        resume_embedding_id: str,
        jd_embedding_id: str,
        questions: List[Dict],
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Create or update user questions document
        
        Args:
            user_id: User identifier
            resume_embedding_id: Pinecone ID for resume embedding
            jd_embedding_id: Pinecone ID for JD embedding
            questions: List of question dictionaries
            metadata: Additional metadata (optional)
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            collection = UserQuestionsModel.get_collection()
            if collection is None:
                logger.error("Failed to get user_questions collection")
                return None
            
            # Validate inputs
            if not user_id or not isinstance(user_id, str):
                raise ValueError("user_id must be a non-empty string")
            
            if not questions or not isinstance(questions, list):
                raise ValueError("questions must be a non-empty list")
            
            # Prepare document
            document = {
                'user_id': user_id,
                'resume_embedding_id': resume_embedding_id,
                'jd_embedding_id': jd_embedding_id,
                'questions': questions,
                'total_questions': len(questions),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }
            
            # Add metadata if provided
            if metadata:
                document['metadata'] = metadata
            
            # Check if user already has questions
            existing = collection.find_one({'user_id': user_id})
            
            if existing:
                # Update existing document
                result = collection.update_one(
                    {'user_id': user_id},
                    {
                        '$set': {
                            'resume_embedding_id': resume_embedding_id,
                            'jd_embedding_id': jd_embedding_id,
                            'questions': questions,
                            'total_questions': len(questions),
                            'updated_at': datetime.utcnow(),
                        }
                    }
                )
                doc_id = str(existing['_id'])
                logger.info(f"✅ Updated questions for user {user_id}")
            else:
                # Insert new document
                result = collection.insert_one(document)
                doc_id = str(result.inserted_id)
                logger.info(f"✅ Created questions for user {user_id}")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create/update user questions: {e}")
            return None
    
    @staticmethod
    def get_user_questions(user_id: str) -> Optional[Dict]:
        """
        Get questions for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            Questions document or None if not found
        """
        try:
            collection = UserQuestionsModel.get_collection()
            if collection is None:
                logger.error("Failed to get user_questions collection")
                return None
            
            document = collection.find_one({'user_id': user_id})
            
            if document:
                # Convert ObjectId to string for JSON serialization
                document['_id'] = str(document['_id'])
                logger.info(f"✅ Retrieved {len(document.get('questions', []))} questions for user {user_id}")
                return document
            else:
                logger.warning(f"⚠️ No questions found for user {user_id}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user questions: {e}")
            return None
    
    @staticmethod
    def delete_user_questions(user_id: str) -> bool:
        """
        Delete questions for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = UserQuestionsModel.get_collection()
            if collection is None:
                logger.error("Failed to get user_questions collection")
                return False
            
            result = collection.delete_one({'user_id': user_id})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Deleted questions for user {user_id}")
                return True
            else:
                logger.warning(f"⚠️ No questions found to delete for user {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete user questions: {e}")
            return False
    
    @staticmethod
    def add_question_to_user(
        user_id: str,
        question: Dict
    ) -> bool:
        """
        Add a single question to user's question list
        
        Args:
            user_id: User identifier
            question: Question dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = UserQuestionsModel.get_collection()
            if collection is None:
                logger.error("Failed to get user_questions collection")
                return False
            
            result = collection.update_one(
                {'user_id': user_id},
                {
                    '$push': {'questions': question},
                    '$inc': {'total_questions': 1},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Added question for user {user_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to add question for user {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to add question: {e}")
            return False
    
    @staticmethod
    def update_question_status(
        user_id: str,
        question_id: int,
        status: Dict
    ) -> bool:
        """
        Update status/progress for a specific question
        
        Args:
            user_id: User identifier
            question_id: Question ID within the questions array
            status: Status update dictionary (e.g., {'answered': True, 'score': 85})
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = UserQuestionsModel.get_collection()
            if collection is None:
                logger.error("Failed to get user_questions collection")
                return False
            
            # Update specific question in array
            result = collection.update_one(
                {
                    'user_id': user_id,
                    'questions.id': question_id
                },
                {
                    '$set': {
                        'questions.$.status': status,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Updated question {question_id} status for user {user_id}")
                return True
            else:
                logger.warning(f"⚠️ Question {question_id} not found for user {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to update question status: {e}")
            return False
    
    @staticmethod
    def get_questions_by_category(
        user_id: str,
        category: str
    ) -> List[Dict]:
        """
        Get questions filtered by category
        
        Args:
            user_id: User identifier
            category: Question category
            
        Returns:
            List of questions in the category
        """
        try:
            document = UserQuestionsModel.get_user_questions(user_id)
            
            if not document:
                return []
            
            questions = document.get('questions', [])
            filtered = [q for q in questions if q.get('category') == category]
            
            logger.info(f"✅ Found {len(filtered)} {category} questions for user {user_id}")
            return filtered
            
        except Exception as e:
            logger.error(f"❌ Failed to filter questions by category: {e}")
            return []
    
    @staticmethod
    def create_indexes():
        """
        Create database indexes for better query performance
        """
        try:
            collection = UserQuestionsModel.get_collection()
            if collection is None:
                logger.error("Failed to get user_questions collection")
                return False
            
            # Create index on user_id (unique)
            collection.create_index('user_id', unique=True)
            
            # Create index on created_at for sorting
            collection.create_index('created_at')
            
            logger.info("✅ Created indexes for user_questions collection")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
            return False
