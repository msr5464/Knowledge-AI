"""
RAG Service
===========
Service layer for RAG operations.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.multi_format_rag import MultiFormatRAG
from src.settings import get_config


class RAGService:
    """Service for managing RAG operations."""
    
    def __init__(self):
        """Initialize RAG service with configuration."""
        # Get storage paths from environment
        self.storage_dir = Path(os.getenv('STORAGE_DIR', 'storage'))
        self.documents_dir = Path(os.getenv('DOCUMENTS_DIR', 'storage/documents'))
        self.chroma_db_dir = Path(os.getenv('CHROMA_DB_DIR', 'storage/chroma_db'))
        self.embedding_cache_dir = Path(os.getenv('EMBEDDING_CACHE_DIR', 'storage/embedding_cache'))
        self.metadata_file = self.storage_dir / 'documents_metadata.json'
        
        # Create directories if they don't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_db_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Get RAG configuration
        config = get_config()
        
        # Override paths in config
        config.persist_directory = str(self.chroma_db_dir.absolute())
        config.embedding_cache_dir = str(self.embedding_cache_dir.absolute())
        
        # Initialize RAG system
        self.rag = MultiFormatRAG(config=config)
        
        # Load existing document metadata
        self.documents: Dict[str, Dict[str, Any]] = {}
        self._load_document_metadata()
        
        # Load existing documents into RAG system
        self._load_existing_documents()
    
    def _load_document_metadata(self):
        """Load document metadata from persistent storage."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.documents = json.load(f)
                print(f"✅ Loaded {len(self.documents)} document(s) from metadata file")
            except Exception as e:
                print(f"⚠️  Failed to load document metadata: {e}")
                self.documents = {}
        else:
            self.documents = {}
    
    def _save_document_metadata(self):
        """Save document metadata to persistent storage."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save document metadata: {e}")
    
    def _load_existing_documents(self):
        """Load existing documents from storage directory into RAG system."""
        from src.chromadb_helper import ChromaDBHelper
        
        # Ensure vectorstore is loaded for checking
        self.rag._load_vectorstore_if_needed()
        
        existing_files = []
        skipped_files = []
        
        for doc_info in self.documents.values():
            doc_path = Path(doc_info['path'])
            if doc_path.exists():
                # Check if documents from this file already exist in ChromaDB
                if self.rag.vectorstore:
                    file_exists = ChromaDBHelper.check_documents_exist_by_file_path(
                        self.rag.vectorstore, str(doc_path)
                    )
                    if file_exists:
                        skipped_files.append(doc_path)
                        continue
                existing_files.append(doc_path)
        
        if skipped_files:
            print(f"⏭️  Skipping {len(skipped_files)} document(s) already in ChromaDB:")
            for skipped_file in skipped_files:
                print(f"   - {skipped_file.name}")
        
        if existing_files:
            print(f"📚 Loading {len(existing_files)} existing document(s) into RAG system...")
            try:
                self.rag.add_files(existing_files, replace_if_exists=False)
                print(f"✅ Loaded {len(existing_files)} document(s) into RAG system")
            except Exception as e:
                print(f"⚠️  Failed to load some documents: {e}")
        elif not skipped_files:
            print("ℹ️  No existing documents to load")
        
        # Ensure retriever is initialized if vectorstore exists (for querying existing documents)
        if self.rag.vectorstore and not self.rag.retriever:
            try:
                # Check if vectorstore has any documents
                count = self.rag.vectorstore._collection.count()
                if count > 0:
                    # Initialize retriever from existing vectorstore
                    self.rag.retriever = self.rag.vectorstore.as_retriever(
                        search_kwargs={"k": self.rag.retrieval_k}
                    )
                    # Initialize hybrid retriever if hybrid search is enabled
                    if self.rag.use_hybrid_search:
                        self.rag._init_keyword_retriever()
                    print(f"✅ Initialized retriever from existing ChromaDB ({count} documents)")
            except Exception as e:
                print(f"⚠️  Failed to initialize retriever: {e}")
    
    def _find_existing_document(self, file_name: str) -> Optional[str]:
        """Find existing document by filename (case-insensitive)."""
        file_name_lower = file_name.lower()
        for doc_id, doc_info in self.documents.items():
            if doc_info['name'].lower() == file_name_lower:
                return doc_id
        return None
    
    def upload_document(self, file_path: Path, file_name: str) -> Dict[str, Any]:
        """
        Upload and process a document.
        If a document with the same filename exists, it will be replaced.
        
        Args:
            file_path: Path to uploaded file
            file_name: Original file name
            
        Returns:
            Document metadata
        """
        # Check if document with same filename already exists
        existing_doc_id = self._find_existing_document(file_name)
        
        if existing_doc_id:
            # Delete existing document first
            print(f"🔄 Replacing existing document: {file_name}")
            delete_result = self.delete_document(existing_doc_id)
            if not delete_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to delete existing document: {delete_result.get('error', 'Unknown error')}",
                    'message': f'Failed to replace document {file_name}'
                }
        
        # Generate new document ID
        doc_id = str(uuid.uuid4())
        
        # Save file to documents directory
        saved_path = self.documents_dir / f"{doc_id}_{file_name}"
        
        # Copy file
        import shutil
        shutil.copy2(file_path, saved_path)
        
        # Add to RAG system
        try:
            self.rag.add_files([saved_path], replace_if_exists=True)
            
            # Track document
            self.documents[doc_id] = {
                'id': doc_id,
                'name': file_name,
                'path': str(saved_path),
                'uploaded_at': datetime.now().isoformat(),
                'status': 'processed'
            }
            
            # Save metadata persistently
            self._save_document_metadata()
            
            message = f'Document {file_name} uploaded and processed successfully'
            if existing_doc_id:
                message = f'Document {file_name} replaced successfully'
            
            return {
                'success': True,
                'document_id': doc_id,
                'message': message,
                'replaced': existing_doc_id is not None
            }
        except Exception as e:
            # Remove file if processing failed
            if saved_path.exists():
                saved_path.unlink()
            
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to process document {file_name}'
            }
    
    def query(self, question: str, session_id: Optional[str] = None, bypass_cache: bool = False, use_rag: bool = True) -> Dict[str, Any]:
        """
        Query the RAG system or LLM directly.
        
        Args:
            question: User question
            session_id: Optional session ID for conversation context
            bypass_cache: If True, skip cache and force fresh LLM query
            use_rag: If True, use RAG with documents; If False, query LLM directly
            
        Returns:
            Query result
        """
        try:
            if use_rag:
                result = self.rag.query(question, bypass_cache=bypass_cache)
                
                return {
                    'success': True,
                    'answer': result.get('answer', ''),
                    'sources': result.get('sources', []),
                    'source_documents': result.get('source_documents', []),
                    'query_time_ms': result.get('query_time_ms', 0),
                    'cache_hit': result.get('cache_hit', False),
                    'mode': 'rag'
                }
            else:
                # Direct LLM query without RAG
                import time
                start_time = time.time()
                
                from langchain_core.prompts import ChatPromptTemplate
                from src.rag_helpers import extract_answer_from_llm_result
                
                # Direct LLM system message (no context)
                DIRECT_LLM_MESSAGE = """You are a helpful AI assistant. Answer questions directly and clearly based on your knowledge.

Instructions:
- Provide direct, clear, and accurate answers
- Use markdown formatting for better readability
- Format lists using numbered lists (1., 2., 3.) or bullet points
- Be concise but thorough
- If you don't know something, say so directly without disclaimers"""
                
                llm = self.rag.llm
                if not llm:
                    return {
                        'success': False,
                        'error': 'LLM not available',
                        'message': 'LLM is not configured'
                    }
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", DIRECT_LLM_MESSAGE),
                    ("human", "{question}")
                ])
                
                chain = prompt | llm
                result = chain.invoke({"question": question})
                answer = extract_answer_from_llm_result(result)
                
                query_time_ms = int((time.time() - start_time) * 1000)
                
                return {
                    'success': True,
                    'answer': answer,
                    'sources': [],
                    'source_documents': [],
                    'query_time_ms': query_time_ms,
                    'cache_hit': False,
                    'mode': 'direct_llm'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process query'
            }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents."""
        return list(self.documents.values())
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Delete a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Deletion result
        """
        if doc_id not in self.documents:
            return {
                'success': False,
                'error': 'Document not found'
            }
        
        doc_info = self.documents[doc_id]
        doc_path = Path(doc_info['path'])
        
        try:
            # Remove from RAG system (remove documents by file path)
            if doc_path.exists() and self.rag.vectorstore:
                try:
                    from src.chromadb_helper import ChromaDBHelper
                    removed_count = ChromaDBHelper.remove_documents_by_file_path(
                        self.rag.vectorstore, 
                        str(doc_path),
                        return_count=True
                    )
                    if removed_count > 0:
                        print(f"🗑️  Removed {removed_count} document chunk(s) from ChromaDB")
                except Exception as e:
                    print(f"⚠️  Failed to remove from ChromaDB: {e}")
            
            # Remove file
            if doc_path.exists():
                doc_path.unlink()
            
            # Remove from tracking
            del self.documents[doc_id]
            
            # Save metadata persistently
            self._save_document_metadata()
            
            return {
                'success': True,
                'message': f'Document {doc_info["name"]} deleted successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to delete document'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            doc_count = self.rag.vectorstore._collection.count() if self.rag.vectorstore else 0
            
            return {
                'success': True,
                'total_documents': len(self.documents),
                'total_chunks': doc_count,
                'rag_config': {
                    'use_hybrid_search': self.rag.use_hybrid_search,
                    'use_reranking': self.rag.use_reranking,
                    'enable_query_cache': self.rag.enable_query_cache,
                    'enable_embedding_cache': self.rag.enable_embedding_cache
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_chromadb_contents(self) -> Dict[str, Any]:
        """
        Get ChromaDB collection contents.
        
        Returns:
            ChromaDB data including documents, metadata, and collection info
        """
        try:
            if not self.rag.vectorstore:
                return {
                    'success': True,
                    'collection_name': None,
                    'total_chunks': 0,
                    'chunks': [],
                    'message': 'No documents in ChromaDB yet'
                }
            
            chromadb_data = self.rag.get_chromadb_data()
            
            # Format chunks for display
            chunks = []
            for idx, (doc_id, doc_text, metadata) in enumerate(zip(
                chromadb_data.get('document_ids', []),
                chromadb_data.get('documents', []),
                chromadb_data.get('metadatas', [])
            )):
                file_path = metadata.get('file_path', 'N/A') if metadata else 'N/A'
                # Extract document ID from file path (format: {doc_id}_{filename})
                doc_id_from_path = None
                if file_path != 'N/A':
                    file_name = Path(file_path).name
                    if '_' in file_name:
                        doc_id_from_path = file_name.split('_')[0]
                    # Also try to find document by matching file path
                    for stored_doc_id, doc_info in self.documents.items():
                        if doc_info.get('path') == file_path or doc_info.get('name') in file_name:
                            doc_id_from_path = stored_doc_id
                            break
                
                chunks.append({
                    'id': doc_id,
                    'index': idx + 1,
                    'content': doc_text[:500] + '...' if len(doc_text) > 500 else doc_text,
                    'content_full': doc_text,
                    'content_length': len(doc_text),
                    'metadata': metadata or {},
                    'file_path': file_path,
                    'source': metadata.get('source', 'N/A') if metadata else 'N/A',
                    'document_id': doc_id_from_path  # Document ID for download link
                })
            
            return {
                'success': True,
                'collection_name': chromadb_data.get('collection_name', 'N/A'),
                'total_chunks': chromadb_data.get('total_documents', 0),
                'has_embeddings': chromadb_data.get('has_embeddings', False),
                'embedding_dimension': chromadb_data.get('embedding_dimension'),
                'chunks': chunks
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve ChromaDB contents'
            }
    
    def reset_chromadb(self, delete_all: bool = True) -> Dict[str, Any]:
        """
        Reset ChromaDB by deleting all collections and storage files.
        
        Deletes:
        - All ChromaDB collections (vector data)
        - All files in storage/documents
        - All files in storage/chroma_db (except chroma.sqlite3 related files)
        - All files in storage/embedding_cache
        - Document metadata file
        
        Args:
            delete_all: If True, deletes all collections. Default: True
            
        Returns:
            Reset result with counts of deleted items
        """
        try:
            import shutil
            
            # Delete ChromaDB collections
            self.rag.delete_chromadb(delete_all=delete_all)
            
            # Clear query cache to prevent cached answers from being returned after reset
            if hasattr(self.rag, 'query_cache') and self.rag.query_cache is not None:
                self.rag.query_cache.clear()
                print("✅ Cleared query cache")
            
            # Ensure vectorstore is completely cleared in MultiFormatRAG and child RAGs
            if hasattr(self.rag, '_pdf_rag'):
                self.rag._pdf_rag.vectorstore = None
                self.rag._pdf_rag.retriever = None
                self.rag._pdf_rag.all_documents = []
                # Clear query cache in child RAGs if they have it
                if hasattr(self.rag._pdf_rag, 'query_cache') and self.rag._pdf_rag.query_cache is not None:
                    self.rag._pdf_rag.query_cache.clear()
            if hasattr(self.rag, '_csv_excel_rag'):
                self.rag._csv_excel_rag.vectorstore = None
                self.rag._csv_excel_rag.retriever = None
                self.rag._csv_excel_rag.all_documents = []
                # Clear query cache in child RAGs if they have it
                if hasattr(self.rag._csv_excel_rag, 'query_cache') and self.rag._csv_excel_rag.query_cache is not None:
                    self.rag._csv_excel_rag.query_cache.clear()
            if hasattr(self.rag, '_text_rag'):
                self.rag._text_rag.vectorstore = None
                self.rag._text_rag.retriever = None
                self.rag._text_rag.all_documents = []
                # Clear query cache in child RAGs if they have it
                if hasattr(self.rag._text_rag, 'query_cache') and self.rag._text_rag.query_cache is not None:
                    self.rag._text_rag.query_cache.clear()
            
            deleted_counts = {
                'documents': 0,
                'chroma_db_files': 0,
                'embedding_cache_files': 0
            }
            
            # Delete all files in documents directory
            if self.documents_dir.exists():
                for file_path in self.documents_dir.iterdir():
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            deleted_counts['documents'] += 1
                        except Exception as e:
                            print(f"⚠️  Failed to delete file {file_path}: {e}")
            
            # Delete files in chroma_db directory, but preserve chroma.sqlite3 related files
            # ChromaDB uses chroma.sqlite3 as its main database file - we should NOT delete it
            # However, we can delete collection-specific data files if they exist
            if self.chroma_db_dir.exists():
                for item in self.chroma_db_dir.iterdir():
                    if item.is_file():
                        # Preserve chroma.sqlite3 and related files (chroma.sqlite3-shm, chroma.sqlite3-wal)
                        if 'chroma.sqlite3' in item.name:
                            continue  # Skip chroma.sqlite3 related files
                        try:
                            item.unlink()
                            deleted_counts['chroma_db_files'] += 1
                        except Exception as e:
                            print(f"⚠️  Failed to delete {item}: {e}")
                    elif item.is_dir():
                        # Delete subdirectories (collections)
                        try:
                            shutil.rmtree(item)
                            deleted_counts['chroma_db_files'] += 1
                        except Exception as e:
                            print(f"⚠️  Failed to delete directory {item}: {e}")
            
            # Delete all files in embedding_cache directory
            if self.embedding_cache_dir.exists():
                for item in self.embedding_cache_dir.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                            deleted_counts['embedding_cache_files'] += 1
                        elif item.is_dir():
                            shutil.rmtree(item)
                            deleted_counts['embedding_cache_files'] += 1
                    except Exception as e:
                        print(f"⚠️  Failed to delete {item}: {e}")
            
            # Clear document metadata
            self.documents = {}
            if self.metadata_file.exists():
                try:
                    self.metadata_file.unlink()
                except Exception as e:
                    print(f"⚠️  Failed to delete metadata file: {e}")
            
            # Build success message
            message_parts = []
            if deleted_counts['documents'] > 0:
                message_parts.append(f"{deleted_counts['documents']} document file(s)")
            if deleted_counts['chroma_db_files'] > 0:
                message_parts.append(f"{deleted_counts['chroma_db_files']} ChromaDB file(s)")
            if deleted_counts['embedding_cache_files'] > 0:
                message_parts.append(f"{deleted_counts['embedding_cache_files']} embedding cache file(s)")
            
            # Add query cache clearing to message
            cache_cleared = hasattr(self.rag, 'query_cache') and self.rag.query_cache is not None
            if cache_cleared:
                message_parts.append("query cache")
            
            if message_parts:
                message = f'Database reset successfully. Deleted {", ".join(message_parts)} and all vector data.'
            else:
                message = 'Database reset successfully. All storage cleared.'
            
            total_deleted = deleted_counts['documents'] + deleted_counts['chroma_db_files'] + deleted_counts['embedding_cache_files']
            
            return {
                'success': True,
                'message': message,
                'deleted_files': total_deleted,
                'details': deleted_counts
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to reset database'
            }

