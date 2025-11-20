"""
Quick Test Script for Evaluation & Logging System
Run this to verify all components work correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules import correctly"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from evaluation_logging import (
            RAGASEvaluator,
            PerformanceTracker,
            ResponsibleAIMonitor,
            QueryLogger,
            RAGMetrics,
            PerformanceMetrics,
            ResponsibleAIEvent,
            QueryLog
        )
        print("✅ All imports successful")
        print("  - RAGASEvaluator")
        print("  - PerformanceTracker")
        print("  - ResponsibleAIMonitor")
        print("  - QueryLogger")
        print("  - RAGMetrics")
        print("  - PerformanceMetrics")
        print("  - ResponsibleAIEvent")
        print("  - QueryLog")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_performance_tracker():
    """Test PerformanceTracker functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Performance Tracker")
    print("=" * 60)
    
    try:
        from evaluation_logging import PerformanceTracker
        import time
        
        tracker = PerformanceTracker()
        
        # Simulate query
        tracker.start_total()
        tracker.start_retrieval()
        time.sleep(0.05)  # 50ms
        tracker.end_retrieval(3)
        
        tracker.start_llm()
        time.sleep(0.1)  # 100ms
        tracker.end_llm(100, 50)
        tracker.end_total()
        
        metrics = tracker.get_metrics()
        
        print("✅ PerformanceTracker works")
        print(f"  - Retrieval latency: {metrics.retrieval_latency_ms:.2f}ms")
        print(f"  - LLM latency: {metrics.llm_latency_ms:.2f}ms")
        print(f"  - Total latency: {metrics.total_latency_ms:.2f}ms")
        print(f"  - Documents retrieved: {metrics.num_documents_retrieved}")
        print(f"  - Input tokens: {metrics.num_tokens_input}")
        print(f"  - Output tokens: {metrics.num_tokens_output}")
        return True
    except Exception as e:
        print(f"❌ PerformanceTracker test failed: {e}")
        return False


def test_responsible_ai_monitor():
    """Test ResponsibleAIMonitor functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: Responsible AI Monitor")
    print("=" * 60)
    
    try:
        from evaluation_logging import ResponsibleAIMonitor
        
        monitor = ResponsibleAIMonitor()
        
        # Test safe content
        safe_text = "This is a normal response about Python programming."
        is_safe, reason = monitor.check_content_safety(safe_text)
        print(f"✅ Safe content check: {is_safe} (reason: {reason})")
        
        # Test filtered content
        unsafe_text = "This contains harmful content that should be filtered."
        is_safe, reason = monitor.check_content_safety(unsafe_text)
        print(f"✅ Unsafe content check: {is_safe} (reason: {reason})")
        
        # Test filtering
        query = "What is Python?"
        response = "Python is a programming language with harmful implications."
        filtered, was_filtered, filter_reason = monitor.filter_response(query, response)
        
        print(f"✅ Response filtering works")
        print(f"  - Was filtered: {was_filtered}")
        print(f"  - Reason: {filter_reason}")
        print(f"  - Events logged: {len(monitor.get_events())}")
        
        return True
    except Exception as e:
        print(f"❌ ResponsibleAIMonitor test failed: {e}")
        return False


def test_query_logger():
    """Test QueryLogger functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: Query Logger")
    print("=" * 60)
    
    try:
        from evaluation_logging import QueryLogger, QueryLog
        from datetime import datetime
        import tempfile
        import os
        
        # Use temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = QueryLogger(log_dir=temp_dir)
            
            # Create test log entry
            test_log = QueryLog(
                timestamp=datetime.now().isoformat(),
                session_id="test-session",
                query="What is AI?",
                response="AI is artificial intelligence.",
                retrieval_strategy="semantic",
                documents_retrieved=["doc1", "doc2"],
                performance_metrics={
                    "retrieval_latency_ms": 100,
                    "llm_latency_ms": 2000,
                    "total_latency_ms": 2100,
                    "num_documents_retrieved": 2,
                    "num_tokens_input": 50,
                    "num_tokens_output": 20
                },
                ragas_metrics={
                    "faithfulness": 0.85,
                    "context_recall": 0.75,
                    "context_precision": 1.0,
                    "answer_relevancy": 0.90
                },
                responsible_ai_events=[],
                success=True,
                error_message=None
            )
            
            # Log it
            logger.log_query(test_log)
            
            # Verify files created
            csv_exists = logger.csv_file.exists()
            json_exists = logger.json_file.exists()
            
            print(f"✅ QueryLogger works")
            print(f"  - CSV log created: {csv_exists}")
            print(f"  - JSON log created: {json_exists}")
            print(f"  - Log directory: {temp_dir}")
            
            # Try to read back
            logs = logger.get_logs()
            print(f"  - Logs retrieved: {len(logs)}")
            
            return csv_exists and json_exists
    except Exception as e:
        print(f"❌ QueryLogger test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ragas_metrics():
    """Test RAGMetrics dataclass"""
    print("\n" + "=" * 60)
    print("TEST 5: RAGAS Metrics")
    print("=" * 60)
    
    try:
        from evaluation_logging import RAGMetrics
        
        # Test metrics that meet threshold
        metrics_pass = RAGMetrics(
            faithfulness=0.85,
            context_recall=0.75,
            context_precision=0.80,
            answer_relevancy=0.90
        )
        
        print(f"✅ Metrics (passing): {metrics_pass.to_dict()}")
        print(f"  - Meets threshold: {metrics_pass.meets_threshold()}")
        
        # Test metrics that don't meet threshold
        metrics_fail = RAGMetrics(
            faithfulness=0.70,  # Below 0.80
            context_recall=0.65,  # Below 0.70
            context_precision=0.50,
            answer_relevancy=0.60
        )
        
        print(f"✅ Metrics (failing): {metrics_fail.to_dict()}")
        print(f"  - Meets threshold: {metrics_fail.meets_threshold()}")
        
        return True
    except Exception as e:
        print(f"❌ RAGMetrics test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("EVALUATION & LOGGING - SYSTEM TEST")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Performance Tracker": test_performance_tracker(),
        "Responsible AI": test_responsible_ai_monitor(),
        "Query Logger": test_query_logger(),
        "RAGAS Metrics": test_ragas_metrics()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("System is ready for use!")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review errors above")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
