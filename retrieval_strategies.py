"""
Advanced Retrieval Strategies for RAG System
Implements multiple retrieval patterns configurable via environment variables
"""

import os
import logging
from typing import List, Dict, Tuple, Any, Callable, Optional
from abc import ABC, abstractmethod
import json
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrieverStrategy(ABC):
    """Abstract base class for retrieval strategies"""
    
    def __init__(self, vector_store, llm=None, name: str = "base"):
        self.vector_store = vector_store
        self.llm = llm
        self.name = name
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """Retrieve documents based on query"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Return strategy information"""
        pass


class SemanticRetriever(RetrieverStrategy):
    """Basic semantic search using FAISS"""
    
    def __init__(self, vector_store, llm=None):
        super().__init__(vector_store, llm, name="semantic")
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """Standard semantic search"""
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Semantic retriever found {len(docs)} documents for: {query}")
            return docs
        except Exception as e:
            logger.error(f"Error in semantic retrieval: {str(e)}")
            return []
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "semantic",
            "description": "Basic vector similarity search using FAISS"
        }


class HybridRetriever(RetrieverStrategy):
    """Hybrid search combining BM25 (keyword) and semantic search"""
    
    def __init__(self, vector_store, llm=None, semantic_weight: float = 0.6):
        super().__init__(vector_store, llm, name="hybrid")
        self.semantic_weight = semantic_weight
        self.keyword_weight = 1.0 - semantic_weight
        self.bm25_retriever = None
    
    def set_bm25_retriever(self, documents: List[Document]):
        """Initialize BM25 retriever with documents"""
        self.bm25_retriever = BM25Retriever.from_documents(documents)
        logger.info("BM25 retriever initialized with documents")
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """Hybrid retrieval combining semantic and keyword search"""
        try:
            if not self.bm25_retriever:
                logger.warning("BM25 retriever not initialized, falling back to semantic")
                return self.vector_store.similarity_search(query, k=k)
            
            # Get semantic results
            semantic_docs = self.vector_store.similarity_search(query, k=k)
            
            # Get keyword results
            keyword_docs = self.bm25_retriever.invoke(query)[:k]
            
            # Combine and deduplicate by document content
            doc_dict = {}
            
            # Add semantic results with semantic score
            for doc in semantic_docs:
                key = doc.page_content[:100]
                if key not in doc_dict:
                    doc_dict[key] = {
                        "doc": doc,
                        "score": self.semantic_weight
                    }
                else:
                    doc_dict[key]["score"] += self.semantic_weight
            
            # Add keyword results with keyword score
            for doc in keyword_docs:
                key = doc.page_content[:100]
                if key not in doc_dict:
                    doc_dict[key] = {
                        "doc": doc,
                        "score": self.keyword_weight
                    }
                else:
                    doc_dict[key]["score"] += self.keyword_weight
            
            # Sort by combined score and return top-k
            sorted_docs = sorted(
                doc_dict.values(),
                key=lambda x: x["score"],
                reverse=True
            )
            
            result = [item["doc"] for item in sorted_docs[:k]]
            logger.info(f"Hybrid retriever found {len(result)} unique documents")
            return result
            
        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {str(e)}")
            return self.vector_store.similarity_search(query, k=k)
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "hybrid",
            "description": "Combines BM25 (keyword) and semantic search",
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight
        }


class SemanticQueryExpansionRetriever(RetrieverStrategy):
    """Expands query using LLM paraphrases and merges results"""
    
    def __init__(self, vector_store, llm, expansion_count: int = 3):
        super().__init__(vector_store, llm, name="query_expansion")
        self.expansion_count = expansion_count
    
    def _generate_paraphrases(self, query: str) -> List[str]:
        """Generate query paraphrases using LLM"""
        if not self.llm:
            return [query]
        
        try:
            prompt = f"""Generate {self.expansion_count} different ways to rephrase this question. 
Return only the questions, one per line, without numbering.

Original Question: {query}

Rephrased Questions:"""
            
            response = self.llm.invoke(prompt)
            paraphrases = response.content.strip().split('\n')
            paraphrases = [p.strip() for p in paraphrases if p.strip()][:self.expansion_count]
            
            logger.info(f"Generated {len(paraphrases)} query paraphrases")
            return paraphrases
        except Exception as e:
            logger.error(f"Error generating paraphrases: {str(e)}")
            return [query]
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """Retrieve using original + paraphrased queries"""
        try:
            queries = [query] + self._generate_paraphrases(query)
            doc_dict = {}
            
            # Execute search for each query variant
            for q in queries:
                docs = self.vector_store.similarity_search(q, k=k)
                for doc in docs:
                    key = doc.page_content[:100]
                    if key not in doc_dict:
                        doc_dict[key] = {"doc": doc, "count": 0}
                    doc_dict[key]["count"] += 1
            
            # Sort by frequency of retrieval
            sorted_docs = sorted(
                doc_dict.values(),
                key=lambda x: x["count"],
                reverse=True
            )
            
            result = [item["doc"] for item in sorted_docs[:k]]
            logger.info(f"Query expansion retriever found {len(result)} documents from {len(queries)} query variants")
            return result
            
        except Exception as e:
            logger.error(f"Error in query expansion retrieval: {str(e)}")
            return self.vector_store.similarity_search(query, k=k)
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "query_expansion",
            "description": "Expands queries with LLM paraphrases",
            "expansion_count": self.expansion_count
        }


class ContextReRankingRetriever(RetrieverStrategy):
    """Re-ranks retrieved contexts by LLM relevance scoring"""
    
    def __init__(self, vector_store, llm, rerank_top_k: int = 5):
        super().__init__(vector_store, llm, name="reranking")
        self.rerank_top_k = rerank_top_k
    
    def _score_relevance(self, query: str, doc: Document) -> float:
        """Score document relevance using LLM"""
        if not self.llm:
            return 1.0
        
        try:
            prompt = f"""Rate the relevance of this document to the query on a scale of 0-10.
Return only a single number.

Query: {query}

Document: {doc.page_content[:300]}...

Relevance Score:"""
            
            response = self.llm.invoke(prompt)
            try:
                score = float(response.content.strip())
                return min(max(score, 0), 10)
            except ValueError:
                return 5.0
        except Exception as e:
            logger.error(f"Error scoring relevance: {str(e)}")
            return 5.0
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """Retrieve and re-rank by relevance"""
        try:
            # Get initial results (get more to rerank)
            initial_docs = self.vector_store.similarity_search(query, k=self.rerank_top_k)
            
            if not initial_docs:
                return []
            
            # Score each document
            scored_docs = []
            for doc in initial_docs:
                score = self._score_relevance(query, doc)
                scored_docs.append((doc, score))
            
            # Sort by score
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            result = [doc for doc, _ in scored_docs[:k]]
            logger.info(f"Re-ranking retriever re-ranked {len(initial_docs)} to top {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Error in re-ranking retrieval: {str(e)}")
            return self.vector_store.similarity_search(query, k=k)
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "reranking",
            "description": "Re-ranks results by LLM relevance scoring",
            "rerank_top_k": self.rerank_top_k
        }


class SelfQueryRetriever(RetrieverStrategy):
    """Extracts metadata filters from query using LLM"""
    
    def __init__(self, vector_store, llm, metadata_fields: List[str] = None):
        super().__init__(vector_store, llm, name="self_query")
        self.metadata_fields = metadata_fields or ["source", "page", "type", "date"]
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract metadata filters from query using LLM"""
        if not self.llm:
            return {}
        
        try:
            fields_str = ", ".join(self.metadata_fields)
            prompt = f"""Extract metadata filters from this query if present.
Return a JSON object with extracted filters, or empty object if none found.

Available metadata fields: {fields_str}

Query: {query}

Extracted Filters (JSON only):"""
            
            response = self.llm.invoke(prompt)
            try:
                filters = json.loads(response.content.strip())
                logger.info(f"Extracted filters: {filters}")
                return filters
            except json.JSONDecodeError:
                logger.warning("Could not parse filter JSON")
                return {}
        except Exception as e:
            logger.error(f"Error extracting filters: {str(e)}")
            return {}
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """Retrieve with extracted metadata filters"""
        try:
            # Extract filters from query
            filters = self._extract_filters(query)
            
            # Perform semantic search
            docs = self.vector_store.similarity_search(query, k=k)
            
            # Filter by metadata if filters extracted
            if filters:
                filtered_docs = []
                for doc in docs:
                    match = True
                    for key, value in filters.items():
                        if key in doc.metadata:
                            if doc.metadata[key] != value:
                                match = False
                                break
                    if match:
                        filtered_docs.append(doc)
                
                docs = filtered_docs if filtered_docs else docs
                logger.info(f"Self-query filter reduced results from {len(docs)} documents")
            
            return docs[:k]
            
        except Exception as e:
            logger.error(f"Error in self-query retrieval: {str(e)}")
            return self.vector_store.similarity_search(query, k=k)
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "self_query",
            "description": "Extracts metadata filters from query",
            "metadata_fields": self.metadata_fields
        }


class MultiHopRetriever(RetrieverStrategy):
    """Decomposes complex questions into sub-queries"""
    
    def __init__(self, vector_store, llm, max_hops: int = 3):
        super().__init__(vector_store, llm, name="multihop")
        self.max_hops = max_hops
    
    def _decompose_question(self, query: str) -> List[str]:
        """Decompose complex question into sub-questions"""
        if not self.llm:
            return [query]
        
        try:
            prompt = f"""Decompose this complex question into {min(self.max_hops, 3)} simpler sub-questions.
Return only the questions, one per line, without numbering.

Original Question: {query}

Sub-questions:"""
            
            response = self.llm.invoke(prompt)
            sub_questions = response.content.strip().split('\n')
            sub_questions = [q.strip() for q in sub_questions if q.strip()][:self.max_hops]
            
            if not sub_questions:
                sub_questions = [query]
            
            logger.info(f"Decomposed into {len(sub_questions)} sub-questions")
            return sub_questions
        except Exception as e:
            logger.error(f"Error decomposing question: {str(e)}")
            return [query]
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Document]:
        """Retrieve for each sub-question and merge results"""
        try:
            # Decompose query
            sub_questions = self._decompose_question(query)
            
            doc_dict = {}
            
            # Retrieve for each sub-question
            for i, sub_q in enumerate(sub_questions):
                docs = self.vector_store.similarity_search(sub_q, k=k)
                
                for doc in docs:
                    key = doc.page_content[:100]
                    if key not in doc_dict:
                        doc_dict[key] = {"doc": doc, "hops": []}
                    doc_dict[key]["hops"].append(i)
            
            # Sort by number of hops (cross-referenced)
            sorted_docs = sorted(
                doc_dict.values(),
                key=lambda x: len(x["hops"]),
                reverse=True
            )
            
            result = [item["doc"] for item in sorted_docs[:k]]
            logger.info(f"Multi-hop retriever found {len(result)} documents across {len(sub_questions)} sub-queries")
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-hop retrieval: {str(e)}")
            return self.vector_store.similarity_search(query, k=k)
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "multihop",
            "description": "Decomposes complex questions into sub-queries",
            "max_hops": self.max_hops
        }


class StrategyFactory:
    """Factory for creating retrieval strategies"""
    
    _strategies = {
        "semantic": SemanticRetriever,
        "hybrid": HybridRetriever,
        "query_expansion": SemanticQueryExpansionRetriever,
        "reranking": ContextReRankingRetriever,
        "self_query": SelfQueryRetriever,
        "multihop": MultiHopRetriever,
    }
    
    @classmethod
    def create(cls, strategy_name: str, vector_store, llm=None, **kwargs) -> RetrieverStrategy:
        """Create a retrieval strategy by name"""
        strategy_class = cls._strategies.get(strategy_name.lower())
        
        if not strategy_class:
            logger.warning(f"Unknown strategy: {strategy_name}, falling back to semantic")
            strategy_class = SemanticRetriever
        
        return strategy_class(vector_store, llm, **kwargs)
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get list of available strategies"""
        return list(cls._strategies.keys())


def get_retrieval_strategy_from_env(vector_store, llm=None) -> RetrieverStrategy:
    """Create retrieval strategy based on environment variables"""
    
    strategy_name = os.getenv("RETRIEVAL_STRATEGY", "semantic")
    
    kwargs = {}
    
    # Hybrid settings
    if strategy_name.lower() == "hybrid":
        kwargs["semantic_weight"] = float(os.getenv("HYBRID_SEMANTIC_WEIGHT", "0.6"))
    
    # Query expansion settings
    elif strategy_name.lower() == "query_expansion":
        kwargs["expansion_count"] = int(os.getenv("QUERY_EXPANSION_COUNT", "3"))
    
    # Re-ranking settings
    elif strategy_name.lower() == "reranking":
        kwargs["rerank_top_k"] = int(os.getenv("RERANK_TOP_K", "5"))
    
    # Self-query settings
    elif strategy_name.lower() == "self_query":
        metadata_fields = os.getenv("SELF_QUERY_METADATA_FIELDS", "source,page,type,date").split(",")
        kwargs["metadata_fields"] = metadata_fields
    
    # Multi-hop settings
    elif strategy_name.lower() == "multihop":
        kwargs["max_hops"] = int(os.getenv("MULTIHOP_MAX_HOPS", "3"))
    
    strategy = StrategyFactory.create(strategy_name, vector_store, llm, **kwargs)
    logger.info(f"Initialized retrieval strategy: {strategy_name}")
    
    return strategy
