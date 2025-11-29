"""
RAG Helper Utilities
====================

Utility functions and classes for RAG operations.
"""

import sys
import re
import hashlib
from pathlib import Path
from typing import List, Optional, Any
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage


def debug_log(message: str, debug_mode: bool = False):
    """
    Print debug message only if debug_mode is enabled.
    
    Args:
        message: Message to print
        debug_mode: If True, print the message. Default: False
    """
    if debug_mode:
        print(message)


def import_chromadb_helper():
    """Import ChromaDBHelper with fallback for direct script execution."""
    try:
        from .chromadb_helper import ChromaDBHelper
        return ChromaDBHelper
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.chromadb_helper import ChromaDBHelper
        return ChromaDBHelper


class SimpleMemory:
    """Simple in-memory conversation history."""
    
    def __init__(self, memory_type='buffer', max_messages=None):
        self.memory_type = memory_type
        self.max_messages = max_messages
        self.chat_history = []
        self.memory_key = "chat_history"
    
    def save_context(self, inputs: dict, outputs: dict):
        """Save a conversation turn."""
        question = inputs.get('input', '')
        answer = outputs.get('output', '')
        
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))
        
        if self.memory_type == 'window' and self.max_messages:
            if len(self.chat_history) > self.max_messages * 2:
                self.chat_history = self.chat_history[-self.max_messages * 2:]
    
    def clear(self):
        """Clear conversation history."""
        self.chat_history = []
    
    @property
    def messages(self):
        """Get conversation messages."""
        return self.chat_history


def calculate_similarity(distance: float) -> tuple:
    """
    Convert cosine distance to similarity score.
    
    Args:
        distance: Cosine distance (0-2, where 0 = identical, 2 = opposite)
    
    Returns:
        Tuple of (similarity, similarity_percent)
    """
    similarity = 1 - (distance / 2)
    return similarity, similarity * 100


def deduplicate_documents(documents: List[Document]) -> List[Document]:
    """
    Remove duplicate documents based on content hash.
    
    Args:
        documents: List of documents
    
    Returns:
        List of unique documents
    """
    seen = set()
    unique_docs = []
    
    for doc in documents:
        content_hash = hash(doc.page_content[:200])
        if content_hash not in seen:
            seen.add(content_hash)
            unique_docs.append(doc)
    
    return unique_docs


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file.
    
    Args:
        file_path: Path to file
    
    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_content_hash(content: str) -> str:
    """
    Calculate SHA256 hash of content string.
    
    Args:
        content: Content string
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def add_file_metadata_to_documents(documents: List[Document], file_path: Optional[Path] = None, 
                                   file_hash: Optional[str] = None) -> List[Document]:
    """
    Add file metadata to documents for tracking and deduplication.
    
    Args:
        documents: List of Document objects
        file_path: Path to source file
        file_hash: Hash of the file/content
    
    Returns:
        List of Document objects with metadata
    """
    import time
    
    for doc in documents:
        if not doc.metadata:
            doc.metadata = {}
        
        if file_path:
            doc.metadata['file_path'] = str(file_path.absolute())
            doc.metadata['file_name'] = file_path.name
        
        if file_hash:
            doc.metadata['file_hash'] = file_hash
        
        doc.metadata['upload_timestamp'] = time.time()
    
    return documents


# RAG System Message Template
RAG_SYSTEM_MESSAGE = """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Read the context carefully and extract relevant information from ALL provided sources
- Answer the question directly and confidently based on the information in the context
- Do NOT include source citations like [Source 1] or [Source 2] in your answer - just provide the answer directly
- Do NOT use disclaimers like "The information is not available in the provided context" or "I was unable to find"
- If information is partially available, provide what you can determine directly without disclaimers
- If you can infer or deduce information from the context, provide that answer directly
- Be direct and clear-cut - avoid being overly cautious or politically correct
- Be thorough and extract all relevant details from the context
- For questions asking for lists (like "what are..."), provide a complete list from all sources
- If this is a follow-up question, use the conversation history to understand the context
- Provide complete answers without truncation

FORMATTING REQUIREMENTS:
- Use proper line breaks and spacing between sections
- Format lists using markdown bullet points (- or *)
- Use numbered lists (1., 2., 3.) for sequential items
- Add blank lines between different items or sections
- Use markdown formatting:
  * **Bold** for emphasis on important terms
  * Use headers (##) for major sections if needed
  * Use proper spacing - add a blank line before and after lists
- For test cases or structured data, format each item on a new line with proper indentation
- Ensure readability with clear separation between items
- Do NOT run everything together in a single paragraph - break it into logical sections and format it properly into multiple lines
- If formatting is passed by user, follow the formatting instructions strictly.
"""


def extract_answer_from_llm_result(result: Any) -> str:
    """
    Extract answer text from LLM result object.
    
    Args:
        result: LLM result object (can be various types)
    
    Returns:
        Answer string
    """
    if hasattr(result, 'content'):
        return result.content
    elif isinstance(result, str):
        return result
    else:
        return str(result)


def expand_query(query: str, use_query_expansion: bool = False) -> List[str]:
    """
    Expand query with alternative phrasings.
    
    Args:
        query: Original query string
        use_query_expansion: If True, expand the query
    
    Returns:
        List of query strings (original + expansions)
    """
    if not use_query_expansion:
        return [query]
    
    expanded = [query]
    if "?" in query:
        expanded.append(query.replace("?", "").strip())
    
    return expanded


def extract_cited_sources(answer: str) -> set:
    """
    Extract cited source numbers from answer text.
    
    Args:
        answer: Answer text containing source citations like [Source 1], [Source 2]
    
    Returns:
        Set of cited source numbers (1-indexed). Empty set if no citations found.
    """
    source_pattern = r'\[Source\s+(\d+)\]'
    matches = re.findall(source_pattern, answer, re.IGNORECASE)
    cited_source_numbers = {int(num) for num in matches}
    
    return cited_source_numbers


def rerank_documents(query: str, documents: List[Document], reranker: Any, top_k: int) -> List[tuple]:
    """
    Re-rank documents using CrossEncoder.
    
    Args:
        query: Query string
        documents: List of documents to re-rank
        reranker: CrossEncoder instance (or None)
        top_k: Number of top documents to return
    
    Returns:
        List of tuples (score, document) sorted by score descending
    """
    if not reranker:
        return [(0.0, doc) for doc in documents[:top_k]]
    
    try:
        pairs = [[query, doc.page_content] for doc in documents]
        scores = reranker.predict(pairs)
        scored_docs = list(zip(scores, documents))
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return scored_docs[:top_k]
    except Exception as e:
        print(f"⚠️  Error re-ranking documents: {e}")
        return [(0.0, doc) for doc in documents[:top_k]]

