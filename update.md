# User Document Management - Design Decision

## One Resume + One Job Description Per User

### Design Principle

Each user can have exactly **one resume** and **one job description** stored in the system at any time.

### Why This Design?

1. **Clarity**: Users practice for one specific job at a time
2. **Simplicity**: No confusion about which resume/JD generated which questions
3. **Storage Efficiency**: Prevents unlimited accumulation of embeddings
4. **User Experience**: Clear workflow - upload new documents to start fresh practice session

### Behavior

When a user uploads new documents:

```
┌─────────────────────────────────────────────────────┐
│  User Upload New Resume + JD                        │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Step 1: Delete Old Embeddings from Pinecone        │
│  - Removes previous resume embedding                │
│  - Removes previous JD embedding                    │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Step 2: Store New Embeddings in Pinecone           │
│  - Generates new resume embedding                   │
│  - Generates new JD embedding                       │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Step 3: Replace Questions in MongoDB               │
│  - Old questions are replaced with new ones         │
│  - Questions tailored to new resume + JD            │
└─────────────────────────────────────────────────────┘
```

### Implementation

**Pinecone Service:**
```python
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
    """
    # 1. Delete all existing documents for user
    self.delete_user_documents(user_id)
    
    # 2. Store new resume
    resume_id = self.store_document(...)
    
    # 3. Store new JD
    jd_id = self.store_document(...)
    
    return resume_id, jd_id
```

**File Parsing Service:**
```python
# Uses replace instead of store
resume_id, jd_id = pinecone_service.replace_user_documents(
    user_id=user_id,
    resume_text=resume_text,
    jd_text=jd_text,
    timestamp=timestamp,
    resume_metadata={...},
    jd_metadata={...}
)
```

**MongoDB (Questions):**
```python
# Questions are also replaced (via upsert)
if existing:
    # Update existing document
    collection.update_one({'user_id': user_id}, {...})
else:
    # Insert new document
    collection.insert_one({...})
```

### User Workflow

1. **First Upload**:
   - User uploads resume + JD
   - Embeddings stored in Pinecone
   - Questions generated and saved to MongoDB
   - User practices with these questions

2. **Second Upload (New Job)**:
   - User uploads new resume + new JD
   - **Old embeddings deleted** from Pinecone
   - **New embeddings stored** in Pinecone
   - **Old questions replaced** in MongoDB
   - **New questions generated** based on new documents
   - User practices with new questions

3. **Previous Work**:
   - Previous questions are **not** preserved
   - Previous embeddings are **not** preserved
   - User starts fresh with new job preparation

### Alternative Approaches Considered

#### ❌ Multi-Resume Support
**Not Chosen Because:**
- Complexity: Which resume/JD pair generated which questions?
- Storage: Unlimited growth in Pinecone vectors
- UX: User confusion about which documents to use
- Cost: More vectors = higher Pinecone usage

**If Needed in Future:**
- Add `session_id` or `application_id` to track different job applications
- Store multiple resume/JD pairs with timestamps
- Let user select which pair to practice with

#### ❌ Keep Old Questions as History
**Not Chosen Because:**
- Scope: Current focus is on active preparation, not historical tracking
- Storage: MongoDB growth for inactive data
- Relevance: Old questions become outdated quickly

**If Needed in Future:**
- Add `archived_questions` collection
- Move old questions to archive before generating new ones
- Let user view history but not practice with old questions

### Benefits of Current Approach

✅ **Simple & Clear**: One set of active documents per user  
✅ **Storage Efficient**: Predictable Pinecone usage (2 vectors per user)  
✅ **No Confusion**: Questions always match current resume/JD  
✅ **Cost Effective**: Minimal vector storage costs  
✅ **Fast**: No need to search through multiple document versions  

### Limitations

⚠️ **No History**: Previous documents and questions are lost  
⚠️ **Single Job**: Can't prepare for multiple jobs simultaneously  
⚠️ **No Versioning**: Can't compare questions from different resume versions  

### Future Enhancements

If multi-document support is needed:

```python
# Add session/application tracking
{
    "user_id": "user123",
    "applications": [
        {
            "application_id": "app1",
            "company": "Google",
            "position": "SWE",
            "resume_embedding_id": "abc123",
            "jd_embedding_id": "def456",
            "questions_ref": "questions_app1",
            "created_at": "2025-11-07",
            "active": true
        },
        {
            "application_id": "app2",
            "company": "Microsoft",
            "position": "SDE",
            "resume_embedding_id": "ghi789",
            "jd_embedding_id": "jkl012",
            "questions_ref": "questions_app2",
            "created_at": "2025-11-05",
            "active": false
        }
    ]
}
```

**Pinecone Metadata:**
```python
{
    "user_id": "user123",
    "application_id": "app1",
    "document_type": "resume",
    "timestamp": 1699315200
}
```

**Query:**
```python
# Get documents for specific application
embeddings = pinecone_service.retrieve_embeddings(
    user_id="user123",
    application_id="app1"
)
```

### Testing

**Test Case 1: First Upload**
```python
# Upload resume + JD
result = upload_documents(user_id="user123", resume="...", jd="...")
assert result.success == True

# Verify in Pinecone
vectors = pinecone.query(filter={"user_id": "user123"})
assert len(vectors) == 2  # resume + jd

# Verify in MongoDB
questions = db.user_questions.find_one({"user_id": "user123"})
assert questions is not None
```

**Test Case 2: Second Upload (Replace)**
```python
# Upload new documents
result = upload_documents(user_id="user123", resume="new...", jd="new...")
assert result.success == True

# Verify old vectors deleted, new stored
vectors = pinecone.query(filter={"user_id": "user123"})
assert len(vectors) == 2  # Still only 2 (replaced)

# Verify questions updated
new_questions = db.user_questions.find_one({"user_id": "user123"})
assert new_questions.updated_at > original_time
```

**Test Case 3: Multiple Users**
```python
# User A uploads
upload_documents(user_id="userA", resume="A_resume", jd="A_jd")

# User B uploads
upload_documents(user_id="userB", resume="B_resume", jd="B_jd")

# Verify isolation
vectors_A = pinecone.query(filter={"user_id": "userA"})
vectors_B = pinecone.query(filter={"user_id": "userB"})
assert len(vectors_A) == 2
assert len(vectors_B) == 2
assert vectors_A != vectors_B
```

### Summary

The **one resume + one JD per user** design provides a simple, efficient, and cost-effective solution for the current use case. It ensures users focus on one job preparation at a time without confusion or unnecessary complexity.

If multiple job applications need to be tracked simultaneously, the architecture can be extended with `application_id` or `session_id` without breaking the current implementation.

---

**Design Decision Date**: November 7, 2025  
**Version**: 2.1.0  
**Status**: ✅ Implemented  
**Review Required**: If use case changes to support multiple simultaneous job preparations
