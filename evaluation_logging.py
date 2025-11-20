"""
Evaluation & Logging Module for RAG System
Implements RAGAS metrics, performance tracking, and responsible AI logging
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import csv

from langchain_core.documents import Document

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RAGMetrics:
    """RAGAS evaluation metrics"""
    faithfulness: float
    context_recall: float
    context_precision: float
    answer_relevancy: float
    
    def meets_threshold(self) -> bool:
        """Check if metrics meet minimum thresholds"""
        return (
            self.faithfulness >= float(os.getenv("RAGAS_FAITHFULNESS_THRESHOLD", "0.80")) and
            self.context_recall >= float(os.getenv("RAGAS_CONTEXT_RECALL_THRESHOLD", "0.70"))
        )
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    retrieval_latency_ms: float
    llm_latency_ms: float
    total_latency_ms: float
    num_documents_retrieved: int
    num_tokens_input: int
    num_tokens_output: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResponsibleAIEvent:
    """Responsible AI event tracking"""
    timestamp: str
    event_type: str  # "content_filtered", "safety_check", "bias_detection"
    query: str
    response_filtered: bool
    filter_reason: Optional[str]
    original_response: Optional[str]
    filtered_response: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryLog:
    """Complete query log entry"""
    timestamp: str
    session_id: str
    query: str
    response: str
    retrieval_strategy: str
    documents_retrieved: List[str]
    performance_metrics: Dict[str, Any]
    ragas_metrics: Optional[Dict[str, float]]
    responsible_ai_events: List[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RAGASEvaluator:
    """RAGAS-based evaluation for RAG systems"""
    
    def __init__(self, llm=None):
        """
        Initialize RAGAS evaluator
        
        Args:
            llm: Language model for evaluation
        """
        self.llm = llm
        self.faithfulness_threshold = float(os.getenv("RAGAS_FAITHFULNESS_THRESHOLD", "0.80"))
        self.context_recall_threshold = float(os.getenv("RAGAS_CONTEXT_RECALL_THRESHOLD", "0.70"))
    
    def evaluate_faithfulness(self, query: str, context: List[Document], answer: str) -> float:
        """
        Evaluate faithfulness: Does the answer stay true to the context?
        Score: 0.0 to 1.0
        """
        if not self.llm:
            logger.warning("LLM not available for faithfulness evaluation")
            return 0.5
        
        try:
            context_text = "\n\n".join([doc.page_content for doc in context])
            
            prompt = f"""Evaluate if the answer is faithful to the given context.
Score from 0.0 (completely unfaithful) to 1.0 (completely faithful).
Return ONLY a number between 0.0 and 1.0.

Context:
{context_text}

Question: {query}

Answer: {answer}

Faithfulness Score:"""
            
            response = self.llm.invoke(prompt)
            score = float(response.content.strip())
            score = max(0.0, min(1.0, score))
            
            logger.info(f"Faithfulness score: {score:.3f}")
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating faithfulness: {str(e)}")
            return 0.5
    
    def evaluate_context_recall(self, query: str, context: List[Document], ground_truth: str = None) -> float:
        """
        Evaluate context recall: Is all relevant information retrieved?
        Score: 0.0 to 1.0
        
        If ground_truth not provided, estimates based on query coverage
        """
        if not self.llm:
            logger.warning("LLM not available for context recall evaluation")
            return 0.5
        
        try:
            context_text = "\n\n".join([doc.page_content for doc in context])
            
            if ground_truth:
                # With ground truth: check if context contains all needed info
                prompt = f"""Evaluate if the context contains all information needed to answer based on ground truth.
Score from 0.0 (missing critical info) to 1.0 (all info present).
Return ONLY a number between 0.0 and 1.0.

Context:
{context_text}

Question: {query}

Ground Truth Answer: {ground_truth}

Context Recall Score:"""
            else:
                # Without ground truth: estimate coverage
                prompt = f"""Evaluate if the context contains sufficient information to answer the question.
Score from 0.0 (insufficient) to 1.0 (comprehensive).
Return ONLY a number between 0.0 and 1.0.

Context:
{context_text}

Question: {query}

Context Recall Score:"""
            
            response = self.llm.invoke(prompt)
            score = float(response.content.strip())
            score = max(0.0, min(1.0, score))
            
            logger.info(f"Context recall score: {score:.3f}")
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating context recall: {str(e)}")
            return 0.5
    
    def evaluate_context_precision(self, query: str, context: List[Document]) -> float:
        """
        Evaluate context precision: Are retrieved documents relevant?
        Score: 0.0 to 1.0
        """
        if not self.llm or not context:
            return 0.5
        
        try:
            relevant_count = 0
            
            for doc in context:
                prompt = f"""Is this document relevant to answering the question?
Answer with ONLY 'yes' or 'no'.

Question: {query}

Document: {doc.page_content[:500]}...

Relevant:"""
                
                response = self.llm.invoke(prompt)
                if "yes" in response.content.lower():
                    relevant_count += 1
            
            score = relevant_count / len(context)
            logger.info(f"Context precision score: {score:.3f} ({relevant_count}/{len(context)} relevant)")
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating context precision: {str(e)}")
            return 0.5
    
    def evaluate_answer_relevancy(self, query: str, answer: str) -> float:
        """
        Evaluate answer relevancy: Does the answer address the question?
        Score: 0.0 to 1.0
        """
        if not self.llm:
            return 0.5
        
        try:
            prompt = f"""Evaluate if the answer is relevant to the question.
Score from 0.0 (completely irrelevant) to 1.0 (highly relevant).
Return ONLY a number between 0.0 and 1.0.

Question: {query}

Answer: {answer}

Answer Relevancy Score:"""
            
            response = self.llm.invoke(prompt)
            score = float(response.content.strip())
            score = max(0.0, min(1.0, score))
            
            logger.info(f"Answer relevancy score: {score:.3f}")
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating answer relevancy: {str(e)}")
            return 0.5
    
    def evaluate_all(
        self,
        query: str,
        context: List[Document],
        answer: str,
        ground_truth: str = None
    ) -> RAGMetrics:
        """
        Evaluate all RAGAS metrics
        
        Args:
            query: User question
            context: Retrieved documents
            answer: Generated answer
            ground_truth: Optional ground truth answer
        
        Returns:
            RAGMetrics object with all scores
        """
        logger.info("Starting RAGAS evaluation...")
        
        faithfulness = self.evaluate_faithfulness(query, context, answer)
        context_recall = self.evaluate_context_recall(query, context, ground_truth)
        context_precision = self.evaluate_context_precision(query, context)
        answer_relevancy = self.evaluate_answer_relevancy(query, answer)
        
        metrics = RAGMetrics(
            faithfulness=faithfulness,
            context_recall=context_recall,
            context_precision=context_precision,
            answer_relevancy=answer_relevancy
        )
        
        logger.info(f"RAGAS Metrics: {metrics.to_dict()}")
        logger.info(f"Meets thresholds: {metrics.meets_threshold()}")
        
        return metrics


class PerformanceTracker:
    """Track performance metrics for retrieval and generation"""
    
    def __init__(self):
        self.retrieval_start = None
        self.retrieval_end = None
        self.llm_start = None
        self.llm_end = None
        self.total_start = None
        self.total_end = None
        self.num_documents = 0
        self.num_tokens_input = 0
        self.num_tokens_output = 0
    
    def start_total(self):
        """Start total timing"""
        self.total_start = time.time()
    
    def start_retrieval(self):
        """Start retrieval timing"""
        self.retrieval_start = time.time()
    
    def end_retrieval(self, num_documents: int):
        """End retrieval timing"""
        self.retrieval_end = time.time()
        self.num_documents = num_documents
    
    def start_llm(self):
        """Start LLM timing"""
        self.llm_start = time.time()
    
    def end_llm(self, num_tokens_input: int = 0, num_tokens_output: int = 0):
        """End LLM timing"""
        self.llm_end = time.time()
        self.num_tokens_input = num_tokens_input
        self.num_tokens_output = num_tokens_output
    
    def end_total(self):
        """End total timing"""
        self.total_end = time.time()
    
    def get_metrics(self) -> PerformanceMetrics:
        """Calculate and return performance metrics"""
        retrieval_latency = (
            (self.retrieval_end - self.retrieval_start) * 1000
            if self.retrieval_start and self.retrieval_end
            else 0.0
        )
        
        llm_latency = (
            (self.llm_end - self.llm_start) * 1000
            if self.llm_start and self.llm_end
            else 0.0
        )
        
        total_latency = (
            (self.total_end - self.total_start) * 1000
            if self.total_start and self.total_end
            else 0.0
        )
        
        return PerformanceMetrics(
            retrieval_latency_ms=round(retrieval_latency, 2),
            llm_latency_ms=round(llm_latency, 2),
            total_latency_ms=round(total_latency, 2),
            num_documents_retrieved=self.num_documents,
            num_tokens_input=self.num_tokens_input,
            num_tokens_output=self.num_tokens_output
        )


class ResponsibleAIMonitor:
    """Monitor and log responsible AI events"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.events = []
        
        # Content filtering keywords (configurable)
        self.sensitive_keywords = os.getenv(
            "CONTENT_FILTER_KEYWORDS",
            "inappropriate,offensive,harmful,violent,discriminatory"
        ).split(",")
    
    def check_content_safety(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if content is safe
        
        Returns:
            (is_safe, reason)
        """
        text_lower = text.lower()
        
        # Basic keyword filtering
        for keyword in self.sensitive_keywords:
            if keyword.strip().lower() in text_lower:
                return False, f"Contains sensitive keyword: {keyword}"
        
        # LLM-based safety check (if available)
        if self.llm:
            try:
                prompt = f"""Evaluate if this content is safe and appropriate.
Answer with ONLY 'safe' or 'unsafe'.

Content: {text[:500]}

Safety Assessment:"""
                
                response = self.llm.invoke(prompt)
                if "unsafe" in response.content.lower():
                    return False, "LLM safety check failed"
            except Exception as e:
                logger.warning(f"LLM safety check error: {str(e)}")
        
        return True, None
    
    def filter_response(self, query: str, response: str) -> Tuple[str, bool, Optional[str]]:
        """
        Filter response for safety
        
        Returns:
            (filtered_response, was_filtered, reason)
        """
        is_safe, reason = self.check_content_safety(response)
        
        if not is_safe:
            logger.warning(f"Response filtered: {reason}")
            
            # Log event
            event = ResponsibleAIEvent(
                timestamp=datetime.now().isoformat(),
                event_type="content_filtered",
                query=query,
                response_filtered=True,
                filter_reason=reason,
                original_response=response,
                filtered_response="I apologize, but I cannot provide that response as it may contain inappropriate content. Please rephrase your question."
            )
            self.events.append(event)
            
            return event.filtered_response, True, reason
        
        # Log non-filtered event
        event = ResponsibleAIEvent(
            timestamp=datetime.now().isoformat(),
            event_type="content_filtered",
            query=query,
            response_filtered=False,
            filter_reason=None,
            original_response=response,
            filtered_response=None
        )
        self.events.append(event)
        
        return response, False, None
    
    def get_events(self) -> List[ResponsibleAIEvent]:
        """Get all logged events"""
        return self.events
    
    def clear_events(self):
        """Clear event log"""
        self.events = []


class QueryLogger:
    """Log all queries and responses"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # CSV log file
        self.csv_file = self.log_dir / f"query_log_{datetime.now().strftime('%Y%m%d')}.csv"
        self._init_csv()
        
        # JSON log file
        self.json_file = self.log_dir / f"query_log_{datetime.now().strftime('%Y%m%d')}.json"
    
    def _init_csv(self):
        """Initialize CSV file with headers"""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'session_id',
                    'query',
                    'response',
                    'retrieval_strategy',
                    'num_documents',
                    'retrieval_latency_ms',
                    'llm_latency_ms',
                    'total_latency_ms',
                    'faithfulness',
                    'context_recall',
                    'meets_threshold',
                    'response_filtered',
                    'success'
                ])
    
    def log_query(self, query_log: QueryLog):
        """Log a complete query"""
        
        # Log to CSV
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                perf = query_log.performance_metrics
                ragas = query_log.ragas_metrics or {}
                
                filtered = any(
                    event.get('response_filtered', False)
                    for event in query_log.responsible_ai_events
                )
                
                writer.writerow([
                    query_log.timestamp,
                    query_log.session_id,
                    query_log.query,
                    query_log.response[:200],  # Truncate for CSV
                    query_log.retrieval_strategy,
                    perf.get('num_documents_retrieved', 0),
                    perf.get('retrieval_latency_ms', 0),
                    perf.get('llm_latency_ms', 0),
                    perf.get('total_latency_ms', 0),
                    ragas.get('faithfulness', 'N/A'),
                    ragas.get('context_recall', 'N/A'),
                    ragas.get('meets_threshold', 'N/A') if ragas else 'N/A',
                    filtered,
                    query_log.success
                ])
        except Exception as e:
            logger.error(f"Error writing to CSV: {str(e)}")
        
        # Log to JSON
        try:
            logs = []
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            logs.append(query_log.to_dict())
            
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing to JSON: {str(e)}")
        
        logger.info(f"Query logged: {query_log.timestamp}")
    
    def get_logs(self, date: str = None) -> List[QueryLog]:
        """Retrieve logs for a specific date"""
        if date:
            json_file = self.log_dir / f"query_log_{date}.json"
        else:
            json_file = self.json_file
        
        if not json_file.exists():
            return []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                logs_data = json.load(f)
                return [QueryLog(**log) for log in logs_data]
        except Exception as e:
            logger.error(f"Error reading logs: {str(e)}")
            return []
