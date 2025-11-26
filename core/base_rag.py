"""
Base RAG Class
==============

Common RAG functionality shared across different document types.
"""

import os
import time
from typing import List, Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import all dependencies from centralized imports module
try:
    from .imports import (
        RecursiveCharacterTextSplitter, Chroma, OpenAIEmbeddings, ChatOpenAI,
        Document, ChatPromptTemplate, BM25Retriever, CrossEncoder,
        LANGCHAIN_AVAILABLE, BM25_AVAILABLE, ENSEMBLE_AVAILABLE,
        RERANKER_AVAILABLE, OLLAMA_AVAILABLE, USE_NEW_OLLAMA
    )
except ImportError:
    try:
        from core.imports import (
            RecursiveCharacterTextSplitter, Chroma, OpenAIEmbeddings, ChatOpenAI,
            Document, ChatPromptTemplate, BM25Retriever, CrossEncoder,
            LANGCHAIN_AVAILABLE, BM25_AVAILABLE, ENSEMBLE_AVAILABLE,
            RERANKER_AVAILABLE, OLLAMA_AVAILABLE, USE_NEW_OLLAMA
        )
    except ImportError:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from imports import (
            RecursiveCharacterTextSplitter, Chroma, OpenAIEmbeddings, ChatOpenAI,
            Document, ChatPromptTemplate, BM25Retriever, CrossEncoder,
            LANGCHAIN_AVAILABLE, BM25_AVAILABLE, ENSEMBLE_AVAILABLE,
            RERANKER_AVAILABLE, OLLAMA_AVAILABLE, USE_NEW_OLLAMA
        )

try:
    from .rag_helpers import (
        import_chromadb_helper, SimpleMemory, calculate_similarity, deduplicate_documents,
        calculate_file_hash, calculate_content_hash, add_file_metadata_to_documents, debug_log,
        RAG_SYSTEM_MESSAGE, extract_answer_from_llm_result, expand_query, extract_cited_sources,
        rerank_documents
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from rag_helpers import (
        import_chromadb_helper, SimpleMemory, calculate_similarity, deduplicate_documents,
        calculate_file_hash, calculate_content_hash, add_file_metadata_to_documents, debug_log,
        RAG_SYSTEM_MESSAGE, extract_answer_from_llm_result, expand_query, extract_cited_sources,
        rerank_documents
    )

# Try to import caching modules
try:
    from .caching import QueryCache, EmbeddingCache, CachedEmbeddings
    CACHING_AVAILABLE = True
except ImportError:
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from caching import QueryCache, EmbeddingCache, CachedEmbeddings
        CACHING_AVAILABLE = True
    except ImportError:
        CACHING_AVAILABLE = False


class BaseRAG:
    """Base RAG class with common functionality."""
    
    def __init__(self, use_local_embeddings: bool = True, show_matching_scores: bool = False, 
                 show_chromadb_data: bool = False, show_matching_sources: bool = True,
                 min_similarity_threshold: float = 30.0,
                 chunk_size: int = 1000, chunk_overlap: int = 200, retrieval_k: int = 3,
                 enable_memory: bool = False, memory_type: str = 'buffer',
                 use_hybrid_search: bool = False, use_reranking: bool = False,
                 use_query_expansion: bool = False, hybrid_weights: List[float] = None,
                 reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
                 persist_directory: str = "./chroma_db", collection_name: str = "rag_collection",
                 debug_mode: bool = False, config: Optional[object] = None,
                 enable_query_cache: bool = False, query_cache_size: int = 1000,
                 enable_embedding_cache: bool = False, embedding_cache_dir: str = "./embedding_cache"):
        """
        Initialize RAG system.
        
        Args:
            use_local_embeddings: Use local HuggingFace embeddings instead of OpenAI
            show_matching_scores: If True, print similarity scores for retrieved documents
            show_chromadb_data: If True, allow ChromaDB inspection to be displayed
            show_matching_sources: If True, print matching sources after each query
            min_similarity_threshold: Minimum similarity percentage (0-100) to include a source
            chunk_size: Size of text chunks for splitting documents
            chunk_overlap: Overlap between chunks
            retrieval_k: Number of documents to retrieve
            enable_memory: If True, enable conversation memory for multi-turn conversations
            memory_type: Type of memory to use ('buffer', 'window', 'summary')
            use_hybrid_search: Enable hybrid search (semantic + BM25)
            use_reranking: Enable re-ranking with CrossEncoder
            use_query_expansion: Enable query expansion
            hybrid_weights: Weights for hybrid search [semantic_weight, keyword_weight]
            reranker_model: CrossEncoder model for re-ranking
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of ChromaDB collection
            debug_mode: If True, print detailed debug logs. Default: False
            config: Optional RAGConfig object. If provided, overrides individual parameters.
            enable_query_cache: Enable query result caching. Default: False
            query_cache_size: Maximum number of cached queries. Default: 1000
            enable_embedding_cache: Enable embedding caching. Default: False
            embedding_cache_dir: Directory for embedding cache. Default: "./embedding_cache"
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain required")
        
        # If config object is provided, use it to override parameters
        if config:
            try:
                # Try relative import first (when used as module)
                try:
                    from .settings import RAGConfig
                except ImportError:
                    # Fallback to absolute import (when run as script)
                    from settings import RAGConfig
                if isinstance(config, RAGConfig):
                    config_dict = config.to_dict()
                    use_local_embeddings = config_dict.get('use_local_embeddings', use_local_embeddings)
                    show_matching_scores = config_dict.get('show_matching_scores', show_matching_scores)
                    show_chromadb_data = config_dict.get('show_chromadb_data', show_chromadb_data)
                    show_matching_sources = config_dict.get('show_matching_sources', show_matching_sources)
                    min_similarity_threshold = config_dict.get('min_similarity_threshold', min_similarity_threshold)
                    chunk_size = config_dict.get('chunk_size', chunk_size)
                    chunk_overlap = config_dict.get('chunk_overlap', chunk_overlap)
                    retrieval_k = config_dict.get('retrieval_k', retrieval_k)
                    enable_memory = config_dict.get('enable_memory', enable_memory)
                    memory_type = config_dict.get('memory_type', memory_type)
                    use_hybrid_search = config_dict.get('use_hybrid_search', use_hybrid_search)
                    use_reranking = config_dict.get('use_reranking', use_reranking)
                    use_query_expansion = config_dict.get('use_query_expansion', use_query_expansion)
                    hybrid_weights = config_dict.get('hybrid_weights', hybrid_weights)
                    reranker_model = config_dict.get('reranker_model', reranker_model)
                    persist_directory = config_dict.get('persist_directory', persist_directory)
                    collection_name = config_dict.get('collection_name', collection_name)
                    debug_mode = config_dict.get('debug_mode', debug_mode)
                    enable_query_cache = config_dict.get('enable_query_cache', enable_query_cache)
                    query_cache_size = config_dict.get('query_cache_size', query_cache_size)
                    enable_embedding_cache = config_dict.get('enable_embedding_cache', enable_embedding_cache)
                    embedding_cache_dir = config_dict.get('embedding_cache_dir', embedding_cache_dir)
            except ImportError:
                pass  # If config module not available, use individual parameters
        
        self.show_matching_scores = show_matching_scores
        self.show_chromadb_data = show_chromadb_data
        self.show_matching_sources = show_matching_sources
        self.min_similarity_threshold = min_similarity_threshold
        self.retrieval_k = retrieval_k
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.debug_mode = debug_mode
        
        self._init_embeddings(use_local_embeddings)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.vectorstore = None
        self.llm = None
        self.retriever = None
        self.memory = None
        self.enable_memory = enable_memory
        
        self.use_hybrid_search = use_hybrid_search and BM25_AVAILABLE
        self.use_reranking = use_reranking and RERANKER_AVAILABLE
        self.use_query_expansion = use_query_expansion
        self.hybrid_weights = hybrid_weights or [0.6, 0.4]
        self.reranker_model = reranker_model
        
        self.keyword_retriever = None
        self.hybrid_retriever = None
        self.reranker = None
        self.all_documents = []
        self.ensemble_available = ENSEMBLE_AVAILABLE
        
        if self.use_reranking:
            try:
                self.reranker = CrossEncoder(self.reranker_model)
                debug_log(f"✅ Re-ranker initialized: {self.reranker_model}", self.debug_mode)
            except Exception as e:
                if self.debug_mode:
                    print(f"⚠️  Failed to initialize re-ranker: {e}")
                self.use_reranking = False
        
        self._init_llm()
        
        if self.enable_memory:
            self._init_memory(memory_type)
        
        # Initialize caching if available
        self.enable_query_cache = enable_query_cache and CACHING_AVAILABLE
        self.enable_embedding_cache = enable_embedding_cache and CACHING_AVAILABLE
        
        if CACHING_AVAILABLE:
            # Initialize query cache
            self.query_cache = QueryCache(
                max_size=query_cache_size,
                enabled=self.enable_query_cache
            )
            
            # Initialize embedding cache
            self.embedding_cache = EmbeddingCache(
                cache_dir=embedding_cache_dir,
                enabled=self.enable_embedding_cache
            )
            
            # Wrap embeddings with caching if enabled
            if self.enable_embedding_cache:
                original_embeddings = self.embeddings
                self.embeddings = CachedEmbeddings(original_embeddings, self.embedding_cache)
                self._original_embeddings = original_embeddings
        else:
            self.query_cache = None
            self.embedding_cache = None
        
        # Print caching status if enabled (always print, not just in debug mode)
        if self.enable_query_cache or self.enable_embedding_cache:
            print("✅ Caching enabled:")
            if self.enable_query_cache:
                print(f"   - Query cache: enabled (max size: {query_cache_size})")
            if self.enable_embedding_cache:
                print(f"   - Embedding cache: enabled (dir: {embedding_cache_dir})")
    
    def _init_embeddings(self, use_local_embeddings: bool):
        """Initialize embeddings."""
        if use_local_embeddings or not os.getenv("OPENAI_API_KEY"):
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                debug_log("✅ Using local embeddings (langchain-huggingface)", self.debug_mode)
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                import warnings
                warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_community")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                debug_log("✅ Using local embeddings (langchain_community - deprecated)", self.debug_mode)
                debug_log("💡 Tip: Install 'langchain-huggingface' to remove deprecation warning", self.debug_mode)
        else:
            self.embeddings = OpenAIEmbeddings()
            debug_log("✅ Using OpenAI embeddings", self.debug_mode)
    
    def _init_llm(self):
        """Initialize LLM."""
        # Check for explicit LLM preference from environment
        llm_provider = os.getenv("LLM_PROVIDER", "").lower()
        
        # Check if OpenAI API key is set and valid (not a placeholder)
        openai_key = os.getenv("OPENAI_API_KEY", "")
        has_valid_openai_key = (
            openai_key and 
            openai_key.strip() != "" and 
            not openai_key.startswith("your-") and
            "api-key" not in openai_key.lower()
        )
        
        # Use OpenAI only if explicitly requested or if valid key is provided and Ollama not preferred
        if llm_provider == "openai" or (has_valid_openai_key and llm_provider != "ollama"):
            self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
            debug_log("✅ Using OpenAI LLM", self.debug_mode)
        elif OLLAMA_AVAILABLE or llm_provider == "ollama":
            if USE_NEW_OLLAMA:
                from langchain_ollama import ChatOllama
            else:
                from langchain_community.chat_models import ChatOllama
            
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
            try:
                self.llm = ChatOllama(
                    model=ollama_model,
                    base_url=ollama_base_url,
                    temperature=0
                )
                debug_log(f"✅ Using Ollama LLM ({ollama_model})", self.debug_mode)
            except Exception as e:
                if self.debug_mode:
                    print(f"⚠️  Failed to initialize Ollama: {e}")
                    print("⚠️  Make sure Ollama is running: ollama serve")
                self.llm = None
        else:
            if self.debug_mode:
                print("⚠️  No OpenAI API key and Ollama not available.")
                print("⚠️  Using simple template-based responses.")
            self.llm = None
    
    def _init_memory(self, memory_type: str = 'buffer'):
        """Initialize conversation memory."""
        if memory_type == 'buffer':
            self.memory = SimpleMemory(memory_type='buffer')
            debug_log("✅ Using SimpleMemory (stores all messages)", self.debug_mode)
        elif memory_type == 'window':
            self.memory = SimpleMemory(memory_type='window', max_messages=5)
            debug_log("✅ Using SimpleMemory with window (stores last 5 exchanges)", self.debug_mode)
        elif memory_type == 'summary':
            self.memory = SimpleMemory(memory_type='buffer')
            debug_log("✅ Using SimpleMemory (summary mode not yet implemented, using buffer)", self.debug_mode)
        else:
            self.memory = SimpleMemory(memory_type='buffer')
            debug_log(f"✅ Using SimpleMemory (unknown type '{memory_type}', using buffer)", self.debug_mode)
    
    def _get_or_create_vectorstore(self, documents: List[Document], show_log: bool = True):
        """Get existing ChromaDB collection or create a new one with persistent storage."""
        ChromaDBHelper = import_chromadb_helper()
        return ChromaDBHelper.get_or_create_vectorstore(
            documents=documents,
            embeddings=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
            show_log=show_log
        )
    
    def _load_vectorstore_if_needed(self):
        """Load vectorstore if it doesn't exist (needed for duplicate checking)."""
        if self.vectorstore is None:
            from langchain_core.documents import Document
            empty_docs = [Document(page_content="temp")]
            self.vectorstore = self._get_or_create_vectorstore(empty_docs, show_log=True)
            # Remove the temp document if it was added
            try:
                results = self.vectorstore._collection.get()
                if results.get('ids') and results.get('documents'):
                    for idx, doc in enumerate(results.get('documents', [])):
                        if doc == "temp":
                            self.vectorstore._collection.delete(ids=[results['ids'][idx]])
                            break
            except:
                pass
    
    def _remove_existing_documents(self, file_paths: List[Path], replace_if_exists: bool) -> int:
        """
        Remove existing documents from the same files if replacing.
        
        Args:
            file_paths: List of file paths to check
            replace_if_exists: If True, remove existing documents
            
        Returns:
            Total count of removed documents
        """
        if not replace_if_exists or not self.vectorstore:
            return 0
        
        ChromaDBHelper = import_chromadb_helper()
        removed_count = 0
        
        for file_path in file_paths:
            removed = ChromaDBHelper.remove_documents_by_file_path(
                self.vectorstore, str(file_path), return_count=True
            )
            removed_count += removed
            # Also remove from all_documents list
            self.all_documents = [doc for doc in self.all_documents 
                                if doc.metadata.get('file_path') != str(file_path)]
        
        return removed_count
    
    def _add_documents_to_vectorstore(self, splits: List[Document], success_message: str = "Documents indexed!"):
        """
        Add documents to vectorstore and update retrievers.
        
        Args:
            splits: List of Document objects to add
            success_message: Success message to display
        """
        # Store documents for BM25 (needed for hybrid search)
        self.all_documents.extend(splits)
        
        # Add documents to vectorstore
        if self.vectorstore is None:
            # If vectorstore doesn't exist, create new one
            self.vectorstore = self._get_or_create_vectorstore(splits, show_log=False)
        else:
            try:
                # Try to check if collection exists and has documents
                count = self.vectorstore._collection.count()
                if count == 0:
                    # If collection is empty, recreate with new documents
                    self.vectorstore = self._get_or_create_vectorstore(splits, show_log=False)
                else:
                    # Add to existing vectorstore
                    self.vectorstore.add_documents(splits)
            except Exception:
                # Collection doesn't exist or error accessing it, create new one
                self.vectorstore = self._get_or_create_vectorstore(splits, show_log=False)
        
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.retrieval_k})
        
        # Re-initialize keyword retriever with all documents
        if self.use_hybrid_search:
            self._init_keyword_retriever()
        
        final_count = self.vectorstore._collection.count()
        print(f"✅ {success_message} (Total: {final_count} documents)")
    
    def add_documents_from_texts(self, documents: List[str]):
        """Add documents from text strings."""
        print(f"📚 Adding {len(documents)} documents...")
        
        docs = [Document(page_content=text.strip()) for text in documents]
        splits = self.text_splitter.split_documents(docs)
        print(f"📄 Split into {len(splits)} chunks")
        
        self.all_documents.extend(splits)
        self.vectorstore = self._get_or_create_vectorstore(splits)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.retrieval_k})
        
        if self.use_hybrid_search:
            self._init_keyword_retriever()
        
        print("✅ Documents indexed!")
    
    def query(self, question: str, bypass_cache: bool = False) -> Dict[str, Any]:
        """
        Query the RAG system with caching and performance tracking.
        
        Args:
            question: User question
            bypass_cache: If True, skip cache and force fresh LLM query
            
        Returns:
            Query result dictionary with answer, sources, and metadata
        """
        start_time = time.time()
        cache_hit = False
        
        # Check query cache if enabled and not bypassed
        if self.enable_query_cache and self.query_cache and not bypass_cache:
            cached_result = self.query_cache.get(
                question,
                retrieval_k=self.retrieval_k,
                use_hybrid_search=self.use_hybrid_search,
                use_reranking=self.use_reranking,
                min_similarity_threshold=self.min_similarity_threshold
            )
            
            if cached_result:
                cache_hit = True
                elapsed_time = (time.time() - start_time) * 1000
                
                # Add cache metadata
                result = cached_result.copy()
                result['cache_hit'] = True
                result['query_time_ms'] = elapsed_time
                
                # Clean cached answer: remove source citations but preserve formatting
                import re
                answer = result.get('answer', '')
                if answer:
                    # Remove all source citations
                    answer = re.sub(r'\[Source\s+\d+\]', '', answer)
                    # Remove "Based on the retrieved context" prefix
                    answer = re.sub(r'Based on the retrieved context\s*:?\s*', '', answer, flags=re.IGNORECASE)
                    # Remove any remaining source references
                    answer = re.sub(r'\[Source\s+\d+\]\s*', '', answer)
                    # Preserve formatting: normalize whitespace but keep line breaks
                    answer = re.sub(r'[ \t]+', ' ', answer)  # Multiple spaces/tabs to single space
                    answer = re.sub(r'\n{3,}', '\n\n', answer)  # 3+ newlines to 2
                    answer = re.sub(r' *\n *', '\n', answer)  # Clean up spaces around newlines
                    answer = answer.strip()
                    result['answer'] = answer
                    print(f"✅ Answer: {answer}")
                else:
                    # Fallback: try to extract answer from other fields
                    if 'source_documents' in result and result['source_documents']:
                        # If no answer but we have sources, at least show we have cached data
                        print("✅ Answer: (Cached - see sources below)")
                
                # Print source information if available (matching base class format)
                if self.show_matching_sources:
                    sources = result.get('sources', [])
                    source_documents = result.get('source_documents', [])
                    
                    if sources or source_documents:
                        # Use source_documents if available (more complete), otherwise use sources
                        if source_documents:
                            cited_count = len(source_documents)
                            if self.min_similarity_threshold > 0.0:
                                print(f"📄 Retrieved {cited_count} relevant chunk(s) above {self.min_similarity_threshold}% threshold")
                            else:
                                print(f"📄 Retrieved {cited_count} relevant chunk(s)")
                            print("\n📚 Sources:")
                            print("-" * 60)
                            for doc_info in source_documents:
                                source_id = doc_info.get('source_id', 0)
                                content = doc_info.get('content', '')
                                content_preview = content[:100] if len(content) > 100 else content
                                print(f"[Source {source_id}] {content_preview}...")
                        elif sources:
                            cited_count = len(sources)
                            if self.min_similarity_threshold > 0.0:
                                print(f"📄 Retrieved {cited_count} relevant chunk(s) above {self.min_similarity_threshold}% threshold")
                            else:
                                print(f"📄 Retrieved {cited_count} relevant chunk(s)")
                            print("\n📚 Sources:")
                            print("-" * 60)
                            for i, source in enumerate(sources, 1):
                                if isinstance(source, dict):
                                    content = source.get('content', '')
                                    similarity = source.get('similarity_percent')
                                    content_preview = content[:100] if len(content) > 100 else content
                                    if similarity is not None:
                                        print(f"[Source {i}] Similarity: {similarity:.2f}% - {content_preview}...")
                                    else:
                                        print(f"[Source {i}] {content_preview}...")
                                else:
                                    print(f"[Source {i}] {str(source)[:100]}...")
                
                print(f"⏱️  Query time: {elapsed_time:.2f}ms")
                return result
        
        # Cache miss - execute query
        # Call the actual query implementation
        result = self._query_impl(question)
        
        # Calculate query time
        elapsed_time = (time.time() - start_time) * 1000
        
        # Add performance metadata
        result['cache_hit'] = False
        result['query_time_ms'] = elapsed_time
        
        # Clean answer before caching: remove source citations but preserve formatting
        import re
        answer = result.get('answer', '')
        if answer:
            # Remove all source citations
            answer = re.sub(r'\[Source\s+\d+\]', '', answer)
            # Remove "Based on the retrieved context" prefix
            answer = re.sub(r'Based on the retrieved context\s*:?\s*', '', answer, flags=re.IGNORECASE)
            # Remove any remaining source references
            answer = re.sub(r'\[Source\s+\d+\]\s*', '', answer)
            # Preserve formatting: normalize whitespace but keep line breaks
            answer = re.sub(r'[ \t]+', ' ', answer)  # Multiple spaces/tabs to single space
            answer = re.sub(r'\n{3,}', '\n\n', answer)  # 3+ newlines to 2
            answer = re.sub(r' *\n *', '\n', answer)  # Clean up spaces around newlines
            answer = answer.strip()
            result['answer'] = answer
        
        # Cache the result if enabled (with cleaned answer)
        if self.enable_query_cache and self.query_cache:
            self.query_cache.set(
                question,
                result,
                retrieval_k=self.retrieval_k,
                use_hybrid_search=self.use_hybrid_search,
                use_reranking=self.use_reranking,
                min_similarity_threshold=self.min_similarity_threshold
            )
        
        print(f"⏱️  Query time: {elapsed_time:.2f}ms")
        return result
    
    def _query_impl(self, question: str) -> Dict[str, Any]:
        """Internal query implementation (moved from query method)."""
        if not self.retriever:
            raise ValueError("No documents added")
        
        print(f"❓ Question: {question}")
        
        expanded_queries = expand_query(question, self.use_query_expansion)
        if len(expanded_queries) > 1:
            print(f"🔍 Expanded queries: {len(expanded_queries)}")
        
        all_docs = []
        for query in expanded_queries:
            if self.use_hybrid_search and self.hybrid_retriever:
                docs = self.hybrid_retriever.get_relevant_documents(query)
            else:
                docs = self.retriever.invoke(query)
            all_docs.extend(docs)
        
        initial_retrieval_count = len(all_docs)
        unique_docs = deduplicate_documents(all_docs)
        if len(unique_docs) < len(all_docs):
            print(f"🔄 Deduplicated: {len(all_docs)} → {len(unique_docs)} documents")
        
        rerank_scores = []
        if self.use_reranking:
            reranked = rerank_documents(question, unique_docs, self.reranker, top_k=self.retrieval_k * 2)
            final_docs = [doc for _, doc in reranked]
            rerank_scores = [float(score) for score, _ in reranked]
            if rerank_scores:
                print(f"📊 Re-ranked top score: {rerank_scores[0]:.4f}")
        else:
            final_docs = unique_docs[:self.retrieval_k * 2]
        
        docs = final_docs
        initial_count = len(docs)
        
        needs_scores = self.min_similarity_threshold > 0.0 or self.show_matching_scores
        sources_with_scores = []
        filtered_docs = []
        sources_above_threshold = 0
        
        if needs_scores:
            docs_with_scores = self.vectorstore.similarity_search_with_score(question, k=len(docs))
            score_map = {doc.page_content: (doc, score) for doc, score in docs_with_scores}
            
            if self.show_matching_scores:
                print("\n📊 Matching Scores:")
                print("-" * 60)
                for i, doc in enumerate(docs, 1):
                    doc_with_score = score_map.get(doc.page_content)
                    if doc_with_score:
                        original_doc, distance = doc_with_score
                        similarity, similarity_percent = calculate_similarity(distance)
                        content_preview = doc.page_content[:150]
                        print(f"[{i}] Similarity: {similarity_percent:.2f}% (Distance: {distance:.4f})")
                        print(f"    Content: {content_preview}...")
                    else:
                        content_preview = doc.page_content[:150]
                        print(f"[{i}] Similarity: N/A")
                        print(f"    Content: {content_preview}...")
            
            for i, doc in enumerate(docs, 1):
                doc_with_score = score_map.get(doc.page_content)
                
                if doc_with_score:
                    original_doc, distance = doc_with_score
                    similarity, similarity_percent = calculate_similarity(distance)
                    
                    if similarity_percent >= self.min_similarity_threshold:
                        filtered_docs.append(doc)
                        sources_above_threshold += 1
                        sources_with_scores.append({
                            "content": doc.page_content[:150],
                            "similarity": similarity,
                            "similarity_percent": similarity_percent,
                            "distance": distance,
                            "doc_id": doc.metadata.get('id', '') if doc.metadata else ''
                        })
                else:
                    filtered_docs.append(doc)
                    sources_with_scores.append({
                        "content": doc.page_content[:150],
                        "similarity": None,
                        "similarity_percent": None,
                        "distance": None,
                        "doc_id": doc.metadata.get('id', '') if doc.metadata else ''
                    })
        else:
            filtered_docs = docs
            sources_above_threshold = len(docs)
            for doc in docs:
                sources_with_scores.append({
                    "content": doc.page_content[:150],
                    "similarity": None,
                    "similarity_percent": None,
                    "distance": None,
                    "doc_id": doc.metadata.get('id', '') if doc.metadata else ''
                })
        
        if not filtered_docs and docs:
            print(f"⚠️  No documents passed {self.min_similarity_threshold}% threshold, using top {min(3, len(docs))} retrieved documents")
            filtered_docs = docs[:min(3, len(docs))]
            sources_above_threshold = len(filtered_docs)
            for i, doc in enumerate(filtered_docs, 1):
                if i > len(sources_with_scores):
                    sources_with_scores.append({
                        "content": doc.page_content[:150],
                        "similarity": None,
                        "similarity_percent": None,
                        "distance": None,
                        "doc_id": doc.metadata.get('id', '') if doc.metadata else ''
                    })
        
        docs = filtered_docs
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            # Don't include source numbers in context - LLM will cite naturally if needed
            context_parts.append(doc.page_content)
        
        context = "\n\n".join(context_parts)
        
        if self.llm:
            try:
                if self.enable_memory and self.memory:
                    from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
                    
                    prompt = ChatPromptTemplate.from_messages([
                        SystemMessagePromptTemplate.from_template(RAG_SYSTEM_MESSAGE),
                        MessagesPlaceholder(variable_name="chat_history"),
                        HumanMessagePromptTemplate.from_template("Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
                    ])
                    
                    chat_history = self.memory.messages if hasattr(self.memory, 'messages') else []
                    
                    chain = prompt | self.llm
                    result = chain.invoke({
                        "context": context,
                        "question": question,
                        "chat_history": chat_history
                    })
                    
                    answer = extract_answer_from_llm_result(result)
                    
                    self.memory.save_context(
                        {"input": question},
                        {"output": answer}
                    )
                else:
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", RAG_SYSTEM_MESSAGE),
                        ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
                    ])
                    
                    chain = prompt | self.llm
                    result = chain.invoke({"context": context, "question": question})
                    
                    answer = extract_answer_from_llm_result(result)
            except Exception as e:
                print(f"⚠️  Error generating answer with LLM: {e}")
                # Fallback: use full context without source citations
                answer = context
        else:
            # Fallback when no LLM: provide full context without source citations
            answer = context
        
        # Clean answer: remove source citations but preserve formatting
        import re
        # Remove all source citations
        answer = re.sub(r'\[Source\s+\d+\]', '', answer)
        # Remove "Based on the retrieved context" prefix
        answer = re.sub(r'Based on the retrieved context\s*:?\s*', '', answer, flags=re.IGNORECASE)
        # Remove any remaining source references
        answer = re.sub(r'\[Source\s+\d+\]\s*', '', answer)
        # Preserve formatting: normalize whitespace but keep line breaks
        answer = re.sub(r'[ \t]+', ' ', answer)  # Multiple spaces/tabs to single space
        answer = re.sub(r'\n{3,}', '\n\n', answer)  # 3+ newlines to 2
        answer = re.sub(r' *\n *', '\n', answer)  # Clean up spaces around newlines
        answer = answer.strip()
        
        print(f"✅ Answer: {answer}")
        
        # Extract cited sources for metadata (but don't include in answer text)
        cited_source_numbers = extract_cited_sources(answer)
        
        cited_count = len(cited_source_numbers)
        
        if self.show_matching_sources:
            if self.min_similarity_threshold > 0.0:
                if sources_above_threshold > cited_count:
                    print(f"📄 {sources_above_threshold} source(s) passed {self.min_similarity_threshold}% threshold, {cited_count} cited in answer (out of {initial_count} retrieved)")
                else:
                    print(f"📄 Using {cited_count} source(s) above {self.min_similarity_threshold}% threshold out of {initial_count} retrieved")
            else:
                print(f"📄 Retrieved {cited_count} relevant chunks")
        
        if self.show_matching_sources:
            print("\n📚 Sources:")
            print("-" * 60)
            for i, doc in enumerate(docs, 1):
                if i in cited_source_numbers:
                    content_preview = doc.page_content[:100]
                    print(f"[Source {i}] {content_preview}...")
        
        cited_docs = [doc for i, doc in enumerate(docs, 1) if i in cited_source_numbers]
        cited_sources_with_scores = [
            sources_with_scores[i-1] for i in cited_source_numbers if i <= len(sources_with_scores)
        ]
        
        result = {
            "answer": answer,
            "sources": cited_sources_with_scores,
            "source_documents": [
                {
                    "source_id": i,
                    "content": doc.page_content,
                    "metadata": doc.metadata if doc.metadata else {}
                }
                for i, doc in enumerate(docs, 1)
                if i in cited_source_numbers
            ],
            "all_retrieved_documents": len(docs)
        }
        
        if self.use_hybrid_search or self.use_reranking or len(expanded_queries) > 1:
            result['advanced_retrieval'] = {
                'initial_count': initial_retrieval_count,
                'after_deduplication': len(unique_docs),
                'final_count': len(final_docs),
                'used_hybrid_search': self.use_hybrid_search and self.hybrid_retriever is not None,
                'used_reranking': self.use_reranking and len(rerank_scores) > 0,
                'used_query_expansion': len(expanded_queries) > 1
            }
            
            if rerank_scores:
                result['rerank_scores'] = rerank_scores[:len(cited_source_numbers)]
        
        return result
    
    def clear_memory(self):
        """Clear conversation memory."""
        if self.memory:
            try:
                self.memory.clear()
                print("✅ Conversation memory cleared")
            except Exception as e:
                print(f"⚠️  Error clearing memory: {e}")
    
    def get_memory_summary(self) -> str:
        """Get a summary of the conversation history."""
        if not self.memory or not self.enable_memory:
            return "No memory enabled"
        
        try:
            messages = self.memory.messages if hasattr(self.memory, 'messages') else []
            if messages:
                return f"Conversation has {len(messages)} messages ({len(messages)//2} exchanges)"
            else:
                return "No conversation history"
        except Exception as e:
            return f"Error accessing memory: {e}"
    
    def inspect_chromadb(self):
        """Inspect ChromaDB contents."""
        ChromaDBHelper = import_chromadb_helper()
        ChromaDBHelper.inspect_collection(self.vectorstore, self.show_chromadb_data)
    
    def get_chromadb_data(self) -> dict:
        """Get ChromaDB data as dictionary."""
        ChromaDBHelper = import_chromadb_helper()
        return ChromaDBHelper.get_collection_data(self.vectorstore)
    
    def delete_chromadb(self, collection_name: str = None, delete_all: bool = False):
        """
        Delete ChromaDB collection entirely.
        
        Args:
            collection_name: Specific collection name to delete
            delete_all: If True, deletes all ChromaDB collections
        """
        ChromaDBHelper = import_chromadb_helper()
        
        ChromaDBHelper.delete_collection(
            collection_name=collection_name,
            persist_directory=self.persist_directory,
            delete_all=delete_all
        )
        
        self.vectorstore = None
        self.retriever = None
        self.all_documents = []
        self.keyword_retriever = None
        self.hybrid_retriever = None
    
    def _init_keyword_retriever(self):
        """Initialize BM25 keyword retriever for hybrid search."""
        if not BM25_AVAILABLE or not self.use_hybrid_search or not self.all_documents:
            return
        
        self.keyword_retriever = BM25Retriever.from_documents(self.all_documents)
        self.keyword_retriever.k = self.retrieval_k
        
        if self.ensemble_available:
            from langchain.retrievers import EnsembleRetriever
            self.hybrid_retriever = EnsembleRetriever(
                retrievers=[self.retriever, self.keyword_retriever],
                weights=self.hybrid_weights
            )
    
