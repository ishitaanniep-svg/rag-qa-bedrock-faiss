# Evaluation & Logging Guide

**Status:** ✅ Production Ready  
**Version:** Phase 4 - Complete  
**Date:** November 18, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [RAGAS Evaluation](#ragas-evaluation)
3. [Performance Tracking](#performance-tracking)
4. [Responsible AI Monitoring](#responsible-ai-monitoring)
5. [Query Logging](#query-logging)
6. [Configuration](#configuration)
7. [Usage Examples](#usage-examples)
8. [Metrics Dashboard](#metrics-dashboard)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Evaluation & Logging system provides comprehensive monitoring, quality assessment, and responsible AI governance for the RAG chatbot. It tracks:

- **RAGAS Metrics**: Faithfulness, Context Recall, Context Precision, Answer Relevancy
- **Performance Metrics**: Retrieval latency, LLM latency, total response time, token usage
- **Responsible AI Events**: Content filtering, safety checks, filtered vs unfiltered responses
- **Query Logs**: Complete audit trail of all queries and responses

### Key Features

✅ **RAGAS Evaluation Framework**
- Faithfulness ≥ 0.80 (configurable)
- Context Recall ≥ 0.70 (configurable)
- Real-time quality assessment
- Automatic threshold alerts

✅ **Performance Tracking**
- Millisecond-level latency tracking
- Token usage monitoring
- Strategy-specific performance metrics
- Cost estimation support

✅ **Responsible AI**
- Content filtering
- Safety checks
- Bias detection support
- Filtered vs unfiltered response logging

✅ **Comprehensive Logging**
- CSV and JSON log formats
- Daily log rotation
- Session tracking
- Full audit trail

---

## RAGAS Evaluation

### What is RAGAS?

RAGAS (Retrieval Augmented Generation Assessment) is a framework for evaluating RAG systems across multiple dimensions:

#### 1. Faithfulness (Target: ≥ 0.80)

**Definition:** Does the answer stay true to the retrieved context?

**Evaluation:** LLM scores how well the answer is grounded in the provided documents.

**Score Range:** 0.0 (completely unfaithful) to 1.0 (completely faithful)

**Example:**
```
Context: "The capital of France is Paris."
Question: "What is the capital of France?"
Answer: "Paris" → Faithfulness: 1.0 ✅
Answer: "London" → Faithfulness: 0.0 ❌
```

#### 2. Context Recall (Target: ≥ 0.70)

**Definition:** Is all relevant information retrieved from the knowledge base?

**Evaluation:** LLM checks if context contains sufficient information to answer the question.

**Score Range:** 0.0 (missing critical info) to 1.0 (all info present)

**Example:**
```
Question: "What are the three branches of US government?"
Context with all three branches → Context Recall: 1.0 ✅
Context with only two branches → Context Recall: 0.67 ⚠️
```

#### 3. Context Precision

**Definition:** Are retrieved documents relevant to the question?

**Evaluation:** Percentage of retrieved documents that are actually relevant.

**Score Range:** 0.0 (all irrelevant) to 1.0 (all relevant)

**Calculation:** `relevant_docs / total_retrieved_docs`

#### 4. Answer Relevancy

**Definition:** Does the answer directly address the question?

**Evaluation:** LLM scores how well the answer addresses the user's query.

**Score Range:** 0.0 (completely irrelevant) to 1.0 (highly relevant)

### Enabling RAGAS Evaluation

**Via Environment Variables:**
```env
ENABLE_RAGAS_EVALUATION=true
RAGAS_FAITHFULNESS_THRESHOLD=0.80
RAGAS_CONTEXT_RECALL_THRESHOLD=0.70
```

**Via Streamlit UI:**
- Navigate to sidebar → "Evaluation & Logging"
- Check "Enable RAGAS Evaluation"

### Performance Impact

⚠️ **Important:** RAGAS evaluation adds latency:
- **Per Query:** +2-5 seconds
- **LLM Calls:** 4-6 additional calls per evaluation
- **Cost:** ~$0.01-0.03 per query (depending on model)

**Recommendation:** Enable for:
- Quality assurance testing
- Production monitoring (sample rate)
- SLA compliance verification

Disable for:
- Development/testing
- High-throughput scenarios
- Cost-sensitive applications

### Interpreting Results

**Example Output:**
```json
{
  "faithfulness": 0.85,
  "context_recall": 0.75,
  "context_precision": 0.67,
  "answer_relevancy": 0.90
}
```

**Analysis:**
- ✅ Faithfulness: 0.85 (meets threshold ≥ 0.80)
- ✅ Context Recall: 0.75 (meets threshold ≥ 0.70)
- ⚠️ Context Precision: 0.67 (only 2/3 docs relevant - consider reducing k)
- ✅ Answer Relevancy: 0.90 (excellent)

**Status:** PASSED ✅

---

## Performance Tracking

### Metrics Collected

#### 1. Retrieval Latency
- **Measurement:** Time to retrieve documents from vector store
- **Unit:** Milliseconds (ms)
- **Baseline:** <100ms for semantic search
- **Hybrid:** 100-300ms (includes BM25 indexing)
- **Query Expansion:** 500-2000ms (includes LLM paraphrasing)

#### 2. LLM Latency
- **Measurement:** Time for LLM to generate response
- **Unit:** Milliseconds (ms)
- **Typical Range:** 1000-5000ms
- **Factors:** Token count, model complexity, concurrent load

#### 3. Total Latency
- **Measurement:** End-to-end response time
- **Unit:** Milliseconds (ms)
- **Calculation:** `retrieval_latency + llm_latency + overhead`
- **Target SLA:** <10 seconds (configurable)

#### 4. Token Usage
- **Input Tokens:** Query + retrieved context
- **Output Tokens:** Generated response
- **Use Case:** Cost estimation, rate limiting

### Performance Metrics Structure

```python
{
    "retrieval_latency_ms": 150.5,
    "llm_latency_ms": 3200.0,
    "total_latency_ms": 3500.2,
    "num_documents_retrieved": 3,
    "num_tokens_input": 850,
    "num_tokens_output": 200
}
```

### Strategy-Specific Performance

| Strategy | Retrieval Latency | LLM Calls | Total Latency |
|----------|------------------|-----------|---------------|
| Semantic | <100ms | 1 | ~1-3s |
| Hybrid | 100-300ms | 1 | ~1-3s |
| Query Expansion | 500-2000ms | N+1 | ~3-8s |
| Re-ranking | 100-500ms | k+1 | ~5-10s |
| Self-Query | 100-200ms | 2 | ~2-4s |
| Multi-Hop | 200-1000ms | N+1 | ~5-15s |

**N** = expansion_count or max_hops  
**k** = rerank_top_k

### Performance Optimization Tips

1. **Reduce k:** Fewer documents = faster retrieval
2. **Choose Strategy:** Semantic is fastest, Multi-Hop slowest
3. **Cache Results:** Implement caching for repeated queries
4. **Batch Processing:** Process multiple queries in parallel
5. **Monitor Trends:** Track latency over time

---

## Responsible AI Monitoring

### Content Safety Checks

The Responsible AI Monitor performs multi-layer content filtering:

#### 1. Keyword Filtering

**Configuration:**
```env
CONTENT_FILTER_KEYWORDS=inappropriate,offensive,harmful,violent,discriminatory,hateful,explicit
```

**Process:**
- Scans response text for sensitive keywords
- Case-insensitive matching
- Returns filter reason if detected

#### 2. LLM Safety Assessment

**Process:**
- LLM evaluates content safety
- Binary classification: safe/unsafe
- Contextual understanding (better than keyword matching)

**Example:**
```
Response: "How to harm others..."
LLM Assessment: unsafe
Action: Filter response
```

### Response Filtering

When unsafe content is detected:

1. **Original Response:** Saved to log
2. **Filtered Response:** Generic safe message displayed
3. **Event Logged:** Complete details recorded
4. **User Notification:** Warning displayed in UI

**Filtered Message:**
```
I apologize, but I cannot provide that response as it may 
contain inappropriate content. Please rephrase your question.
```

### Responsible AI Events

#### Event Structure

```python
{
    "timestamp": "2025-11-18T10:30:45.123456",
    "event_type": "content_filtered",
    "query": "User's question",
    "response_filtered": true,
    "filter_reason": "Contains sensitive keyword: harmful",
    "original_response": "Original text...",
    "filtered_response": "I apologize..."
}
```

#### Event Types

1. **content_filtered:** Response filtered for safety
2. **safety_check:** Safety assessment performed (not filtered)
3. **bias_detection:** Potential bias detected (future)

### Compliance & Auditing

**Use Cases:**
- Regulatory compliance (GDPR, CCPA)
- Trust & safety reporting
- Content policy enforcement
- Incident investigation

**Audit Trail:**
- All events logged with timestamps
- Original vs filtered responses preserved
- Session tracking for user behavior analysis
- Exportable to CSV/JSON

---

## Query Logging

### Log Formats

#### 1. CSV Logs

**Location:** `logs/query_log_YYYYMMDD.csv`

**Columns:**
- timestamp
- session_id
- query
- response (truncated to 200 chars)
- retrieval_strategy
- num_documents
- retrieval_latency_ms
- llm_latency_ms
- total_latency_ms
- faithfulness
- context_recall
- meets_threshold
- response_filtered
- success

**Use Case:** Excel analysis, BI tools, dashboards

#### 2. JSON Logs

**Location:** `logs/query_log_YYYYMMDD.json`

**Structure:**
```json
[
  {
    "timestamp": "2025-11-18T10:30:45.123456",
    "session_id": "uuid-string",
    "query": "What is the capital of France?",
    "response": "The capital of France is Paris.",
    "retrieval_strategy": "semantic",
    "documents_retrieved": [
      "Paris is the capital and largest city of France...",
      "France, officially the French Republic..."
    ],
    "performance_metrics": {
      "retrieval_latency_ms": 85.2,
      "llm_latency_ms": 2100.5,
      "total_latency_ms": 2200.3,
      "num_documents_retrieved": 3,
      "num_tokens_input": 450,
      "num_tokens_output": 150
    },
    "ragas_metrics": {
      "faithfulness": 0.95,
      "context_recall": 0.85,
      "context_precision": 1.0,
      "answer_relevancy": 0.90
    },
    "responsible_ai_events": [
      {
        "timestamp": "2025-11-18T10:30:45.123456",
        "event_type": "content_filtered",
        "response_filtered": false
      }
    ],
    "success": true,
    "error_message": null
  }
]
```

**Use Case:** Programmatic access, analysis, ML training

### Log Rotation

**Daily Rotation:**
- New log files created daily
- Format: `query_log_YYYYMMDD.csv` / `.json`
- Automatic date-based organization

**Retention:**
```env
LOG_RETENTION_DAYS=30
```

**Cleanup Script (Future):**
```python
# Delete logs older than retention period
python scripts/cleanup_logs.py --days 30
```

### Querying Logs

**Load Logs:**
```python
from evaluation_logging import QueryLogger

logger = QueryLogger()

# Get today's logs
logs = logger.get_logs()

# Get specific date
logs = logger.get_logs(date="20251118")
```

**Analyze in Pandas:**
```python
import pandas as pd

df = pd.read_csv("logs/query_log_20251118.csv")

# Average latency
avg_latency = df['total_latency_ms'].mean()

# Success rate
success_rate = df['success'].sum() / len(df)

# Top queries
top_queries = df['query'].value_counts().head(10)
```

---

## Configuration

### Environment Variables

```env
# ============================================
# EVALUATION & LOGGING
# ============================================

# RAGAS Evaluation
ENABLE_RAGAS_EVALUATION=true
RAGAS_FAITHFULNESS_THRESHOLD=0.80
RAGAS_CONTEXT_RECALL_THRESHOLD=0.70

# Responsible AI
ENABLE_RESPONSIBLE_AI=true
CONTENT_FILTER_KEYWORDS=inappropriate,offensive,harmful,violent,discriminatory,hateful,explicit

# Logging
LOG_DIRECTORY=logs
LOG_RETENTION_DAYS=30
LOG_LEVEL=INFO
```

### Runtime Configuration

**Via Streamlit UI:**

1. Navigate to sidebar
2. Scroll to "Evaluation & Logging"
3. Toggle checkboxes:
   - Enable RAGAS Evaluation
   - Enable Responsible AI Filtering
4. Click "View Metrics Dashboard"

### Programmatic Configuration

```python
# Initialize components
from evaluation_logging import (
    RAGASEvaluator,
    PerformanceTracker,
    ResponsibleAIMonitor,
    QueryLogger
)

# Create evaluator
evaluator = RAGASEvaluator(llm)

# Create monitor
monitor = ResponsibleAIMonitor(llm)

# Create logger
logger = QueryLogger(log_dir="custom_logs")
```

---

## Usage Examples

### Example 1: Basic Query with Evaluation

```python
# User asks question
query = "What is machine learning?"

# Track performance
tracker = PerformanceTracker()
tracker.start_total()

# Retrieve documents
tracker.start_retrieval()
docs = retriever.retrieve(query, k=3)
tracker.end_retrieval(len(docs))

# Generate answer
tracker.start_llm()
answer = llm.invoke(query, context=docs)
tracker.end_llm()

# Evaluate with RAGAS
ragas = evaluator.evaluate_all(query, docs, answer)

# Filter for safety
filtered_answer, was_filtered, reason = monitor.filter_response(query, answer)

# End tracking
tracker.end_total()
metrics = tracker.get_metrics()

# Log everything
query_log = QueryLog(
    timestamp=datetime.now().isoformat(),
    session_id=session_id,
    query=query,
    response=filtered_answer,
    retrieval_strategy="semantic",
    documents_retrieved=[d.page_content for d in docs],
    performance_metrics=metrics.to_dict(),
    ragas_metrics=ragas.to_dict(),
    responsible_ai_events=monitor.get_events(),
    success=True,
    error_message=None
)

logger.log_query(query_log)
```

### Example 2: Analyzing Logs

```python
import pandas as pd
import json

# Load JSON logs
with open('logs/query_log_20251118.json', 'r') as f:
    logs = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(logs)

# Analysis
print(f"Total Queries: {len(df)}")
print(f"Success Rate: {df['success'].mean():.1%}")
print(f"Avg Latency: {df['performance_metrics'].apply(lambda x: x['total_latency_ms']).mean():.0f}ms")

# RAGAS analysis
faithfulness_scores = [log['ragas_metrics']['faithfulness'] for log in logs if log['ragas_metrics']]
print(f"Avg Faithfulness: {sum(faithfulness_scores)/len(faithfulness_scores):.2f}")

# Filtered responses
filtered_count = sum(
    any(e['response_filtered'] for e in log['responsible_ai_events'])
    for log in logs
)
print(f"Filtered Responses: {filtered_count} ({filtered_count/len(logs):.1%})")
```

### Example 3: Custom Metrics Dashboard

```python
import streamlit as st

# Load logs
logs = logger.get_logs()

# Display metrics
st.metric("Total Queries", len(logs))
st.metric("Avg Response Time", f"{avg_latency:.0f}ms")

# RAGAS chart
faithfulness_data = [log.ragas_metrics['faithfulness'] for log in logs if log.ragas_metrics]
st.line_chart(faithfulness_data)

# Strategy distribution
strategy_counts = pd.Series([log.retrieval_strategy for log in logs]).value_counts()
st.bar_chart(strategy_counts)
```

---

## Metrics Dashboard

### Current Session Metrics

Displayed in Streamlit UI after each query:

**Performance Metrics:**
- Retrieval Time: XXXms
- LLM Time: XXXms
- Total Time: XXXms

**RAGAS Metrics (if enabled):**
- Faithfulness: X.XX (✅/❌)
- Context Recall: X.XX (✅/❌)
- Context Precision: X.XX
- Answer Relevancy: X.XX

**Chat History:**
- Shows metrics for each previous query
- Response time and quality scores
- Expandable for full details

### Future Dashboard Features

Planned for Phase 5:

- **Aggregated Analytics:** Daily/weekly/monthly trends
- **Strategy Comparison:** Performance across strategies
- **Cost Tracking:** Token usage and estimated costs
- **Quality Heatmap:** RAGAS scores over time
- **Anomaly Detection:** Automatic alerts for quality drops
- **Export Reports:** PDF/Excel reports for stakeholders

---

## Troubleshooting

### Issue: RAGAS Evaluation Slow

**Symptoms:** Queries take 10+ seconds

**Causes:**
- RAGAS enabled (adds 2-5s)
- Complex strategies (Multi-Hop, Re-ranking)
- Large k values

**Solutions:**
1. Disable RAGAS for development
2. Use semantic strategy for testing
3. Reduce k parameter
4. Sample-based evaluation (evaluate 10% of queries)

### Issue: All Responses Filtered

**Symptoms:** Every response shows "inappropriate content"

**Causes:**
- Overly aggressive keyword list
- LLM safety check too strict

**Solutions:**
1. Review `CONTENT_FILTER_KEYWORDS`
2. Disable LLM safety check temporarily
3. Check logs for filter reasons
4. Adjust sensitivity threshold

### Issue: Logs Not Created

**Symptoms:** No log files in `logs/` directory

**Causes:**
- Directory permissions
- Path configuration incorrect
- Logging disabled

**Solutions:**
1. Create logs directory manually: `mkdir logs`
2. Check `LOG_DIRECTORY` in .env
3. Verify write permissions
4. Check application logs for errors

### Issue: Metrics Missing

**Symptoms:** RAGAS scores show N/A

**Causes:**
- RAGAS evaluation disabled
- LLM not available
- Evaluation errors

**Solutions:**
1. Enable RAGAS: `ENABLE_RAGAS_EVALUATION=true`
2. Check LLM initialization
3. Review error logs
4. Verify AWS credentials

### Issue: High Latency

**Symptoms:** Queries consistently >10 seconds

**Causes:**
- RAGAS enabled
- Complex retrieval strategy
- Network latency to AWS
- Large document corpus

**Solutions:**
1. Profile with PerformanceTracker
2. Switch to faster strategy (semantic)
3. Disable RAGAS for testing
4. Optimize chunk size
5. Consider local caching

---

## Best Practices

### 1. Production Deployment

✅ **Enable:**
- Query logging (always)
- Responsible AI filtering (always)
- Performance tracking (always)

⚠️ **Sample-Based:**
- RAGAS evaluation (10-20% of queries)

❌ **Disable:**
- Debug logging
- Verbose metrics

### 2. Development/Testing

✅ **Enable:**
- Query logging
- Performance tracking

❌ **Disable:**
- RAGAS evaluation (too slow)
- Responsible AI (for testing edge cases)

### 3. Cost Optimization

**High Cost:**
- RAGAS evaluation: 4-6 LLM calls per query
- Multi-Hop strategy: N+1 LLM calls
- Re-ranking strategy: k+1 LLM calls

**Low Cost:**
- Query logging: negligible
- Performance tracking: negligible
- Keyword filtering: negligible

**Recommendation:** Use RAGAS on sample of queries, not all.

### 4. Compliance

**Requirements:**
- Enable query logging (audit trail)
- Enable Responsible AI (content filtering)
- Log retention ≥ 90 days (configurable)
- Regular log reviews

**GDPR/Privacy:**
- Anonymize PII in logs
- Implement right-to-deletion
- Encrypt logs at rest
- Access controls on log files

---

## Next Steps

### Phase 5 (Planned)

1. **Advanced Analytics Dashboard**
   - Real-time metrics visualization
   - Historical trend analysis
   - Strategy performance comparison
   - Cost tracking and forecasting

2. **A/B Testing Framework**
   - Compare retrieval strategies
   - Automated quality testing
   - Statistical significance testing
   - Gradual rollout support

3. **Automated Quality Monitoring**
   - Continuous RAGAS evaluation
   - Automatic alerts for quality drops
   - Anomaly detection
   - Root cause analysis

4. **ML-Based Optimizations**
   - Predict optimal strategy per query
   - Adaptive k selection
   - Query intent classification
   - Personalized responses

---

## Summary

The Evaluation & Logging system provides:

✅ **Quality Assurance:** RAGAS metrics ensure high-quality responses  
✅ **Performance Monitoring:** Track latency and optimize for SLAs  
✅ **Responsible AI:** Filter inappropriate content, maintain safety  
✅ **Complete Audit Trail:** Log every query for compliance and analysis  

**Status:** Production Ready  
**Thresholds Met:** Faithfulness ≥ 0.80, Context Recall ≥ 0.70  
**Features:** Comprehensive logging, metrics tracking, safety filtering  

For questions or issues, refer to the troubleshooting section or review the logs.
