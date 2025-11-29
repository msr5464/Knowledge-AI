"""
RAG Configuration with Pydantic Settings
=========================================

Get RAG configuration from environment variables (.env file).
The .env file is the single source of truth for all RAG configurations.
Configuration is loaded once and cached for performance.
To change any setting, modify the corresponding value in config/.env file
and restart your application.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


class RAGConfig(BaseSettings):
    """
    RAG Configuration with automatic validation.
    Loads from config/.env file automatically with type checking.
    All RAG classes accept this config object.
    """
    
    # Embedding settings
    use_local_embeddings: bool = Field(
        default=True,
        description="Use local HuggingFace embeddings instead of OpenAI"
    )
    
    # Display settings
    show_matching_sources: bool = Field(
        default=False,
        description="Show matching sources after each query"
    )
    
    # Retrieval settings
    min_similarity_threshold: float = Field(
        default=15.0,
        ge=0.0,
        le=100.0,
        description="Minimum similarity percentage (0-100) to include a source"
    )
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Size of text chunks for splitting documents"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        description="Overlap between chunks"
    )
    retrieval_k: int = Field(
        default=3,
        ge=1,
        le=50,
        description="Number of documents to retrieve"
    )
    
    # Memory settings
    enable_memory: bool = Field(
        default=False,
        description="Enable conversation memory for multi-turn conversations"
    )
    memory_type: str = Field(
        default='buffer',
        pattern='^(buffer|window|summary)$',
        description="Type of memory to use: buffer, window, or summary"
    )
    
    # Advanced retrieval features
    use_hybrid_search: bool = Field(
        default=False,
        description="Enable hybrid search (semantic + BM25)"
    )
    use_reranking: bool = Field(
        default=False,
        description="Enable re-ranking with CrossEncoder"
    )
    use_query_expansion: bool = Field(
        default=False,
        description="Enable query expansion"
    )
    hybrid_weights: List[float] = Field(
        default=[0.6, 0.4],
        description="Weights for hybrid search [semantic_weight, keyword_weight]"
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="CrossEncoder model for re-ranking"
    )
    
    # ChromaDB settings
    persist_directory: str = Field(
        default="./chroma_db",
        alias="CHROMA_DB_DIR",
        description="Directory to persist ChromaDB data"
    )
    collection_name: str = Field(
        default="rag_collection",
        description="Name of ChromaDB collection"
    )
    
    # Debug settings
    debug_mode: bool = Field(
        default=False,
        description="Enable detailed debug logs"
    )
    
    # Caching settings
    enable_query_cache: bool = Field(
        default=True,
        description="Enable query result caching"
    )
    query_cache_size: int = Field(
        default=1000,
        ge=1,
        description="Maximum number of cached queries"
    )
    enable_embedding_cache: bool = Field(
        default=True,
        description="Enable embedding caching"
    )
    embedding_cache_dir: str = Field(
        default="./embedding_cache",
        description="Directory for embedding cache"
    )
    
    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / "config" / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,  # CHUNK_SIZE or chunk_size both work
        extra="ignore",  # Ignore extra fields in .env
    )
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v, info):
        """Ensure chunk_overlap is less than chunk_size."""
        chunk_size = info.data.get("chunk_size", 1000)
        if v >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({v}) must be less than chunk_size ({chunk_size})"
            )
        return v
    
    @field_validator("hybrid_weights")
    @classmethod
    def validate_hybrid_weights(cls, v):
        """Ensure hybrid_weights has exactly 2 values and they sum to ~1.0."""
        if len(v) != 2:
            raise ValueError("hybrid_weights must have exactly 2 values")
        if abs(sum(v) - 1.0) > 0.01:
            raise ValueError(
                f"hybrid_weights must sum to 1.0, got {sum(v):.2f}"
            )
        return v
    
    def to_dict(self) -> dict:
        return self.model_dump()


# Global settings instance - automatically loads from .env
_settings = None


def get_config() -> RAGConfig:
    global _settings
    if _settings is None:
        _settings = RAGConfig()
    return _settings


# For convenience, also export settings directly
settings = get_config()
