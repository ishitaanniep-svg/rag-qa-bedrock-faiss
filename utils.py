"""
Utility functions for document processing and vector store management
"""

import os
import json
from typing import List, Dict, Tuple
from pathlib import Path
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from retrieval_strategies import (
    get_retrieval_strategy_from_env,
    StrategyFactory,
    RetrieverStrategy
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handle PDF document loading and processing"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load a single PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of Document objects
        """
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            logger.info(f"Loaded {len(pages)} pages from {Path(file_path).name}")
            return pages
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            return []
    
    def load_multiple_pdfs(self, file_paths: List[str]) -> Tuple[List[Document], int]:
        """
        Load multiple PDF files
        
        Args:
            file_paths: List of PDF file paths
            
        Returns:
            Tuple of (all_documents, total_pages)
        """
        all_documents = []
        total_pages = 0
        
        for file_path in file_paths:
            documents = self.load_pdf(file_path)
            all_documents.extend(documents)
            total_pages += len(documents)
        
        return all_documents, total_pages
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def process_pdfs(self, file_paths: List[str]) -> Tuple[List[Document], int, int]:
        """
        Complete pipeline: load and split PDFs
        
        Args:
            file_paths: List of PDF file paths
            
        Returns:
            Tuple of (chunks, total_pages, total_chunks)
        """
        documents, total_pages = self.load_multiple_pdfs(file_paths)
        chunks = self.split_documents(documents)
        return chunks, total_pages, len(chunks)


class VectorStoreManager:
    """Manage FAISS vector store operations"""
    
    def __init__(self, store_path: str = "faiss_store"):
        """
        Initialize vector store manager
        
        Args:
            store_path: Path to save/load vector store
        """
        self.store_path = store_path
        self.metadata_file = os.path.join(store_path, "metadata.json")
    
    def create_store(
        self,
        documents: List[Document],
        embeddings
    ) -> FAISS:
        """
        Create FAISS vector store from documents
        
        Args:
            documents: List of Document objects
            embeddings: Embeddings model
            
        Returns:
            FAISS vector store
        """
        try:
            vector_store = FAISS.from_documents(documents, embeddings)
            logger.info(f"Created FAISS vector store with {len(documents)} documents")
            return vector_store
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def save_store(self, vector_store: FAISS, metadata: Dict = None):
        """
        Save vector store and metadata locally
        
        Args:
            vector_store: FAISS vector store to save
            metadata: Optional metadata to save
        """
        try:
            os.makedirs(self.store_path, exist_ok=True)
            vector_store.save_local(self.store_path)
            logger.info(f"Saved vector store to {self.store_path}")
            
            # Save metadata
            if metadata:
                with open(self.metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2, default=str)
                logger.info("Saved metadata")
        
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise
    
    def load_store(self, embeddings):
        """
        Load vector store from local storage
        
        Args:
            embeddings: Embeddings model
            
        Returns:
            FAISS vector store or None
        """
        try:
            if not os.path.exists(self.store_path):
                logger.warning(f"Vector store not found at {self.store_path}")
                return None
            
            vector_store = FAISS.load_local(
                self.store_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"Loaded vector store from {self.store_path}")
            return vector_store
        
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return None
    
    def get_metadata(self) -> Dict:
        """
        Get stored metadata
        
        Returns:
            Metadata dictionary or empty dict
        """
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load metadata: {str(e)}")
        
        return {}
    
    def delete_store(self):
        """Delete vector store"""
        try:
            import shutil
            if os.path.exists(self.store_path):
                shutil.rmtree(self.store_path)
                logger.info(f"Deleted vector store at {self.store_path}")
        except Exception as e:
            logger.error(f"Error deleting vector store: {str(e)}")


class RAGConfig:
    """Configuration for RAG application"""
    
    # AWS Settings
    AWS_REGION = "us-east-1"
    AWS_ACCESS_KEY_ID = "AKIA3KIMWZKIZW3VIROT"
    AWS_SECRET_ACCESS_KEY = "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"
    EMBEDDING_MODEL = "amazon.titan-embed-text-v1"
    LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Document Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # RAG Settings
    RETRIEVAL_K = 3
    TEMPERATURE = 0.7
    MAX_TOKENS = 2048
    
    # Storage
    VECTOR_STORE_PATH = "faiss_store"
    
    @classmethod
    def to_dict(cls) -> Dict:
        """Convert config to dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and key.isupper()
        }


def save_config(config_path: str = "config.json"):
    """Save configuration to file"""
    try:
        with open(config_path, "w") as f:
            json.dump(RAGConfig.to_dict(), f, indent=2)
        logger.info(f"Saved configuration to {config_path}")
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")


def load_config(config_path: str = "config.json") -> Dict:
    """Load configuration from file"""
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
    
    return RAGConfig.to_dict()


class RetrieverManager:
    """Manages retrieval strategy selection and configuration"""
    
    def __init__(self, vector_store: FAISS, llm=None):
        """
        Initialize retriever manager
        
        Args:
            vector_store: FAISS vector store instance
            llm: LLM instance for advanced strategies
        """
        self.vector_store = vector_store
        self.llm = llm
        self.retriever = None
        self.current_strategy = None
    
    def initialize_strategy(self, strategy_name: str = None, **kwargs) -> RetrieverStrategy:
        """
        Initialize retrieval strategy
        
        Args:
            strategy_name: Name of strategy to use (from .env or parameter)
            **kwargs: Additional configuration parameters
            
        Returns:
            Initialized retrieval strategy
        """
        if strategy_name is None:
            strategy_name = os.getenv("RETRIEVAL_STRATEGY", "semantic")
        
        try:
            self.retriever = StrategyFactory.create(
                strategy_name,
                self.vector_store,
                self.llm,
                **kwargs
            )
            self.current_strategy = strategy_name
            
            # Special handling for hybrid retriever
            if strategy_name.lower() == "hybrid":
                try:
                    # Load all documents for BM25 indexing
                    all_docs = self.vector_store.similarity_search("", k=1000)
                    if hasattr(self.retriever, 'set_bm25_retriever'):
                        self.retriever.set_bm25_retriever(all_docs)
                except Exception as e:
                    logger.warning(f"Could not initialize BM25 for hybrid: {str(e)}")
            
            logger.info(f"Initialized retrieval strategy: {strategy_name}")
            return self.retriever
        except Exception as e:
            logger.error(f"Error initializing retrieval strategy: {str(e)}")
            # Fallback to semantic
            self.retriever = StrategyFactory.create("semantic", self.vector_store, self.llm)
            self.current_strategy = "semantic"
            return self.retriever
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """
        Retrieve documents using current strategy
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            **kwargs: Additional parameters
            
        Returns:
            List of retrieved documents
        """
        if self.retriever is None:
            self.initialize_strategy()
        
        return self.retriever.retrieve(query, k=k, **kwargs)
    
    def switch_strategy(self, strategy_name: str, **kwargs) -> RetrieverStrategy:
        """
        Switch to a different retrieval strategy
        
        Args:
            strategy_name: Name of new strategy
            **kwargs: Additional configuration
            
        Returns:
            New retrieval strategy
        """
        old_strategy = self.current_strategy
        self.initialize_strategy(strategy_name, **kwargs)
        logger.info(f"Switched retrieval strategy from {old_strategy} to {strategy_name}")
        return self.retriever
    
    def get_strategy_info(self) -> Dict:
        """Get information about current strategy"""
        if self.retriever:
            return self.retriever.get_info()
        return {"strategy": "none", "status": "not initialized"}
    
    def list_available_strategies(self) -> List[str]:
        """List all available retrieval strategies"""
        return StrategyFactory.get_available_strategies()
