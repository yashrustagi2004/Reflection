"""
Pinecone Service
Handles vector embeddings storage and retrieval for resumes and job descriptions
"""

import os
import hashlib
import logging
from typing import Dict, Optional, List, Tuple
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PineconeService:
    """Service for managing vector embeddings in Pinecone"""
    
    def __init__(self):
        """Initialize Pinecone client and embedding model"""
        self.api_key = os.getenv('PINECONE_API_KEY')
        # Updated region format for Pinecone serverless
        self.environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'interview-prep-assistant')
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        
        # Initialize embedding model (same as QA service for consistency)
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        
        try:
            self.model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"✅ Embedding model loaded: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
        
        # Initialize or connect to index
        self._init_index()
    
    def _init_index(self):
        """Initialize Pinecone index if it doesn't exist"""
        try:
            # Get list of existing indexes
            existing_indexes = [idx['name'] for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=self.environment  # Use the region directly (e.g., 'us-east-1')
                    )
                )
                logger.info(f"✅ Pinecone index created: {self.index_name}")
            else:
                logger.info(f"✅ Connected to existing Pinecone index: {self.index_name}")
            
            # Get index reference
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone index: {e}")
            raise
    
    def _generate_document_id(self, user_id: str, document_type: str, timestamp: int) -> str:
        """
        Generate a unique document ID for Pinecone
        
        Args:
            user_id: User identifier
            document_type: 'resume' or 'job_description'
            timestamp: Unix timestamp
            
        Returns:
            Unique document ID
        """
        # Create deterministic ID based on user_id, type, and timestamp
        id_string = f"{user_id}_{document_type}_{timestamp}"
        # Use hash for shorter, consistent IDs
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            ValueError: If text is empty or invalid
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        # Sanitize input (limit length to prevent memory issues)
        max_length = 5000  # characters
        if len(text) > max_length:
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            raise
    
    def store_document(
        self,
        user_id: str,
        document_type: str,
        text: str,
        timestamp: int,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store document embedding in Pinecone
        
        Args:
            user_id: User identifier
            document_type: 'resume' or 'job_description'
            text: Document text content
            timestamp: Unix timestamp
            metadata: Additional metadata to store
            
        Returns:
            Document ID in Pinecone
            
        Raises:
            ValueError: If inputs are invalid
            Exception: If storage fails
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string")
        
        if document_type not in ['resume', 'job_description']:
            raise ValueError("document_type must be 'resume' or 'job_description'")
        
        if not text or not isinstance(text, str):
            raise ValueError("text must be a non-empty string")
        
        try:
            # Generate document ID
            doc_id = self._generate_document_id(user_id, document_type, timestamp)
            
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Prepare metadata
            vector_metadata = {
                'user_id': user_id,
                'document_type': document_type,
                'timestamp': timestamp,
                'text_length': len(text),
                'text_preview': text[:200]  # Store preview for debugging
            }
            
            # Add additional metadata if provided
            if metadata:
                vector_metadata.update(metadata)
            
            # Store in Pinecone
            self.index.upsert(
                vectors=[(doc_id, embedding, vector_metadata)]
            )
            
            logger.info(f"✅ Stored {document_type} for user {user_id} with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store document in Pinecone: {e}")
            raise
    
    def retrieve_embeddings(
        self,
        user_id: str,
        document_types: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Retrieve embeddings for a user's documents
        
        Args:
            user_id: User identifier
            document_types: List of document types to retrieve (default: both)
            
        Returns:
            Dictionary mapping document_type to embedding data
        """
        if document_types is None:
            document_types = ['resume', 'job_description']
        
        results = {}
        
        try:
            # Query Pinecone for user's documents
            # Note: Pinecone doesn't support metadata-only queries in serverless
            # We'll use a workaround by fetching recent vectors
            
            for doc_type in document_types:
                # Query with a dummy vector to filter by metadata
                query_response = self.index.query(
                    vector=[0.0] * self.embedding_dimension,
                    filter={
                        'user_id': user_id,
                        'document_type': doc_type
                    },
                    top_k=1,
                    include_metadata=True,
                    include_values=True
                )
                
                if query_response['matches']:
                    match = query_response['matches'][0]
                    results[doc_type] = {
                        'id': match['id'],
                        'embedding': match['values'],
                        'metadata': match['metadata']
                    }
                    logger.info(f"✅ Retrieved {doc_type} for user {user_id}")
                else:
                    logger.warning(f"⚠️ No {doc_type} found for user {user_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve embeddings: {e}")
            return {}
    
    def delete_user_documents(self, user_id: str) -> bool:
        """
        Delete all documents for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete by filter (requires metadata indexing)
            self.index.delete(
                filter={
                    'user_id': user_id
                }
            )
            logger.info(f"✅ Deleted all documents for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete user documents: {e}")
            return False
    
    def replace_user_documents(
        self,
        user_id: str,
        resume_text: str,
        jd_text: str,
        timestamp: int,
        resume_metadata: Optional[Dict] = None,
        jd_metadata: Optional[Dict] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Replace user's existing documents with new ones.
        Deletes old embeddings and stores new ones.
        
        Args:
            user_id: User identifier
            resume_text: Resume text content
            jd_text: Job description text content
            timestamp: Unix timestamp
            resume_metadata: Resume metadata (optional)
            jd_metadata: JD metadata (optional)
            
        Returns:
            Tuple of (resume_embedding_id, jd_embedding_id)
        """
        try:
            # Step 1: Delete existing documents for this user
            logger.info(f"Replacing documents for user {user_id}")
            self.delete_user_documents(user_id)
            
            # Step 2: Store new resume
            resume_id = self.store_document(
                user_id=user_id,
                document_type='resume',
                text=resume_text,
                timestamp=timestamp,
                metadata=resume_metadata
            )
            
            # Step 3: Store new job description
            jd_id = self.store_document(
                user_id=user_id,
                document_type='job_description',
                text=jd_text,
                timestamp=timestamp,
                metadata=jd_metadata
            )
            
            logger.info(f"✅ Replaced documents for user {user_id}: resume={resume_id}, jd={jd_id}")
            return resume_id, jd_id
            
        except Exception as e:
            logger.error(f"❌ Failed to replace user documents: {e}")
            return None, None


# Global instance
_pinecone_service = None


def get_pinecone_service() -> PineconeService:
    """
    Get or create Pinecone service instance (singleton pattern)
    
    Returns:
        PineconeService instance
    """
    global _pinecone_service
    
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    
    return _pinecone_service
