# Advanced Retrieval Strategies Implementation Guide

## Overview

This guide documents the implementation of Phase 3: Advanced RAG Patterns for the RAG Q&A Chatbot system.

---

## Architecture

### Module Structure

```
app.py                      # Streamlit UI (updated with strategy controls)
utils.py                    # Utility classes (updated with RetrieverManager)
retrieval_strategies.py     # NEW: All retrieval strategy implementations
requirements.txt            # Dependencies
.env.example               # Configuration template (updated)
```

### Strategy Hierarchy

```
RetrieverStrategy (Abstract Base)
├── SemanticRetriever
├── HybridRetriever
├── SemanticQueryExpansionRetriever
├── ContextReRankingRetriever
├── SelfQueryRetriever
└── MultiHopRetriever

StrategyFactory (Factory Pattern)
└── Creates and manages retriever instances

RetrieverManager (NEW in utils.py)
└── Orchestrates strategy switching and retrieval
```

---

## Implemented Strategies

### 1. Semantic Retriever (Baseline)
**Location:** `retrieval_strategies.py` - `SemanticRetriever` class

**What it does:** Basic vector similarity search using FAISS

**How it works:**
- Query vectorized using Titan embeddings
- FAISS finds k most similar documents
- No additional processing

**When to use:**
- Baseline for comparison
- Simple, fast queries
- Single-topic documents

**Configuration:** No additional config needed

---

### 2. Hybrid Retriever
**Location:** `retrieval_strategies.py` - `HybridRetriever` class

**What it does:** Combines BM25 (keyword) and semantic search

**How it works:**
1. Execute semantic search (FAISS)
2. Execute keyword search (BM25)
3. Combine results using weighted scoring:
   - Semantic score: configurable weight (default 0.6)
   - Keyword score: 1 - semantic weight (default 0.4)
4. Deduplicate and sort by combined score
5. Return top-k results

**When to use:**
- Mixed query types (keywords + semantic)
- Technical documents with specific terms
- When you need both exact matches and conceptual matches

**Configuration:**
```env
RETRIEVAL_STRATEGY=hybrid
HYBRID_SEMANTIC_WEIGHT=0.6  # 60% semantic, 40% keyword
```

**Example:**
- Query: "Python library for machine learning"
- Semantic: Finds documents about ML frameworks
- Keyword: Finds documents with exact terms "Python" and "library"
- Combined: Best matches from both approaches

---

### 3. Semantic Query Expansion Retriever
**Location:** `retrieval_strategies.py` - `SemanticQueryExpansionRetriever` class

**What it does:** Generates paraphrases of the query and merges results

**How it works:**
1. LLM generates N paraphrases of the original query
2. Execute semantic search for each query variant
3. Track which documents appear across searches
4. Sort by frequency of retrieval
5. Return top-k most relevant documents

**When to use:**
- Ambiguous or complex questions
- Different ways to phrase the same concept
- Improving recall on varied terminology

**Configuration:**
```env
RETRIEVAL_STRATEGY=query_expansion
QUERY_EXPANSION_COUNT=3  # Generate 3 paraphrases
```

**Example:**
- Original: "What are the benefits?"
- Paraphrases:
  - "What are the advantages?"
  - "What are the positive aspects?"
  - "What value does this provide?"
- Documents found by multiple paraphrases ranked higher

---

### 4. Context Re-ranking Retriever
**Location:** `retrieval_strategies.py` - `ContextReRankingRetriever` class

**What it does:** Re-ranks retrieved contexts by LLM relevance scoring

**How it works:**
1. Perform initial semantic search (get top rerank_top_k)
2. For each document, score relevance using LLM (0-10 scale)
3. Sort by relevance score
4. Return top-k highest scoring documents

**When to use:**
- High precision needed
- When semantic similarity isn't perfect
- Quality over speed trade-offs acceptable
- Complex topics with nuanced relevance

**Configuration:**
```env
RETRIEVAL_STRATEGY=reranking
RERANK_TOP_K=5  # Score top 5, return top 3
```

**Cost Note:** LLM call per document - slower but higher quality

---

### 5. Self-Query Retriever
**Location:** `retrieval_strategies.py` - `SelfQueryRetriever` class

**What it does:** Extracts metadata filters from query using LLM

**How it works:**
1. LLM extracts structured metadata filters from query
2. Perform semantic search
3. Filter results by extracted metadata
4. Return filtered top-k results

**When to use:**
- Documents with rich metadata (date, type, author)
- Queries with implicit filters ("recent", "research papers", "2024")
- Structured knowledge bases

**Configuration:**
```env
RETRIEVAL_STRATEGY=self_query
SELF_QUERY_METADATA_FIELDS=source,page,type,date
```

**Example:**
- Query: "Recent research on AI from 2024"
- Extracted filters: {"date": "2024", "type": "research"}
- Results: Filtered to 2024 research papers only

**Requirements:** Documents must have metadata fields set

---

### 6. Multi-Hop Retriever
**Location:** `retrieval_strategies.py` - `MultiHopRetriever` class

**What it does:** Decomposes complex questions into sub-queries

**How it works:**
1. LLM decomposes complex question into N sub-questions
2. Execute semantic search for each sub-question
3. Track which documents appear in multiple hops
4. Prioritize documents found by multiple queries
5. Return top-k results

**When to use:**
- Complex, multi-part questions
- Questions requiring synthesis across topics
- "How" and "Why" questions needing multiple perspectives

**Configuration:**
```env
RETRIEVAL_STRATEGY=multihop
MULTIHOP_MAX_HOPS=3  # Decompose into max 3 sub-questions
```

**Example:**
- Complex Q: "How does machine learning improve with neural networks?"
- Sub-questions:
  1. "What is machine learning?"
  2. "What are neural networks?"
  3. "How are neural networks used in ML?"
- Documents addressing multiple sub-questions ranked higher

---

## Configuration Guide

### Environment Variables

Create a `.env` file in your project root:

```env
# Select active strategy
RETRIEVAL_STRATEGY=semantic

# Hybrid settings
HYBRID_SEMANTIC_WEIGHT=0.6

# Query expansion settings
QUERY_EXPANSION_COUNT=3

# Re-ranking settings
RERANK_TOP_K=5

# Self-query settings
SELF_QUERY_METADATA_FIELDS=source,page,type,date

# Multi-hop settings
MULTIHOP_MAX_HOPS=3

# General settings
RETRIEVAL_TOP_K=3
```

### Runtime Configuration (Streamlit UI)

1. **Strategy Selection:**
   - Sidebar → Settings → "Retrieval Strategy"
   - Dropdown to switch between strategies
   - Changes apply immediately

2. **Strategy Details:**
   - Click "Strategy Details" expander
   - Shows current configuration

3. **Retrieval Parameters:**
   - "Number of similar documents to retrieve" slider
   - Adjust top-k (1-5 documents)

---

## Code Integration

### In Your Application

#### 1. Import Required Classes
```python
from utils import RetrieverManager
from retrieval_strategies import StrategyFactory
```

#### 2. Initialize Retriever Manager
```python
retriever_manager = RetrieverManager(
    vector_store=faiss_vector_store,
    llm=bedrock_llm
)

# Initialize with strategy from .env
retriever_manager.initialize_strategy()
```

#### 3. Use in Queries
```python
# Retrieve using current strategy
documents = retriever_manager.retrieve(
    query="Your question here",
    k=3
)
```

#### 4. Switch Strategies
```python
# Runtime strategy switching
retriever_manager.switch_strategy("hybrid")

# List available strategies
strategies = retriever_manager.list_available_strategies()
```

---

## Performance Comparison

| Strategy | Speed | Quality | LLM Calls | Best For |
|----------|-------|---------|-----------|----------|
| Semantic | ⚡⚡⚡ | ⭐⭐ | 0 | Baseline, speed |
| Hybrid | ⚡⚡ | ⭐⭐⭐ | 0 | Mixed queries |
| Query Expansion | ⚡ | ⭐⭐⭐ | N (paraphrases) | Ambiguous Q |
| Re-ranking | ⚠️ | ⭐⭐⭐⭐ | k (docs) | High precision |
| Self-Query | ⚡ | ⭐⭐⭐ | 1 | Filtered results |
| Multi-Hop | ⚠️ | ⭐⭐⭐⭐ | N (sub-Q) + k | Complex Q |

---

## Troubleshooting

### Strategy Not Found
```
Error: Unknown strategy: xyz, falling back to semantic
```
**Solution:** Check RETRIEVAL_STRATEGY in .env for typos. Valid: `semantic`, `hybrid`, `query_expansion`, `reranking`, `self_query`, `multihop`

### BM25 Not Initialized
```
Warning: BM25 retriever not initialized, falling back to semantic
```
**Solution:** Hybrid strategy requires documents in vector store. Ensure documents loaded before using hybrid.

### LLM Call Errors
**Symptom:** Timeouts or errors with query_expansion, re-ranking, multihop

**Solution:** 
- Check AWS credentials
- Verify Bedrock access
- Reduce max_hops or expansion_count
- Increase timeout settings

### Performance Issues
**Slow with re-ranking or multi-hop?**
- These call LLM multiple times - expected
- Use lower k values
- Consider switching to semantic for quick feedback

---

## Advanced Usage

### Custom Strategy
Extend `RetrieverStrategy` base class:

```python
from retrieval_strategies import RetrieverStrategy

class CustomRetriever(RetrieverStrategy):
    def retrieve(self, query: str, k: int = 3, **kwargs):
        # Your custom logic here
        pass
    
    def get_info(self):
        return {
            "name": "custom",
            "description": "My custom strategy"
        }
```

### Combining Strategies
```python
# Use different strategies for different queries
if "recent" in query.lower():
    retriever_manager.switch_strategy("self_query")
elif len(query.split()) > 15:
    retriever_manager.switch_strategy("multihop")
else:
    retriever_manager.switch_strategy("hybrid")
```

---

## Testing Guide

### Unit Tests
```python
# Test individual strategies
from retrieval_strategies import SemanticRetriever, HybridRetriever

def test_semantic():
    retriever = SemanticRetriever(vector_store, llm)
    docs = retriever.retrieve("test query", k=3)
    assert len(docs) <= 3

def test_hybrid():
    retriever = HybridRetriever(vector_store, llm)
    retriever.set_bm25_retriever(all_documents)
    docs = retriever.retrieve("test query", k=3)
    assert len(docs) <= 3
```

### Performance Testing
```python
import time

queries = [
    "Simple query",
    "More complex query about multiple topics",
    "Very long and detailed question..."
]

for strategy in ["semantic", "hybrid", "query_expansion"]:
    retriever_manager.switch_strategy(strategy)
    for query in queries:
        start = time.time()
        docs = retriever_manager.retrieve(query)
        elapsed = time.time() - start
        print(f"{strategy}: {elapsed:.2f}s")
```

---

## Migration Guide

### From Basic Semantic Search
**Before:**
```python
docs = vector_store.similarity_search(query, k=3)
```

**After:**
```python
docs = retriever_manager.retrieve(query, k=3)
# Automatically uses configured strategy
```

---

## Next Steps

1. **Test each strategy** with your documents
2. **Benchmark performance** for your use case
3. **Configure .env** with optimal parameters
4. **Deploy** with chosen strategy
5. **Monitor** effectiveness and costs
6. **Iterate** based on results

---

## Support & References

- **LangChain Docs:** https://python.langchain.com/
- **FAISS Docs:** https://faiss.ai/
- **Bedrock Docs:** https://docs.aws.amazon.com/bedrock/

---

**Implementation Date:** November 18, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
