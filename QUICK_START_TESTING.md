# Quick Start: Testing Advanced Retrieval Strategies

## Setup (5 minutes)

### 1. Update Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure .env
Copy `.env.example` to `.env` and update:
```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1

# Default strategy (start with semantic)
RETRIEVAL_STRATEGY=semantic

# Hybrid settings (for testing hybrid strategy)
HYBRID_SEMANTIC_WEIGHT=0.6
```

### 3. Start Application
```powershell
python -m streamlit run app.py
```

---

## Testing Each Strategy (2-3 minutes each)

### Strategy 1: Semantic (Baseline)
**Configuration:**
```env
RETRIEVAL_STRATEGY=semantic
```

**Test:**
1. Upload a PDF document
2. Ask: "What is the main topic?"
3. Observe: Fast response, basic relevance
4. Note response time ⏱️

---

### Strategy 2: Hybrid Search
**Configuration:**
```env
RETRIEVAL_STRATEGY=hybrid
HYBRID_SEMANTIC_WEIGHT=0.6
```

**Test:**
1. Keep same documents
2. Ask: "Python machine learning library"
3. Compare to semantic results
4. Notice: Keyword matches included
5. Try different weights: 0.3, 0.5, 0.8

**Observation Points:**
- Semantic weight 0.8 = more conceptual matches
- Semantic weight 0.2 = more keyword matches
- Find your optimal weight

---

### Strategy 3: Semantic Query Expansion
**Configuration:**
```env
RETRIEVAL_STRATEGY=query_expansion
QUERY_EXPANSION_COUNT=3
```

**Test:**
1. Ask an ambiguous question
2. Example: "How does it work?"
3. Observe: Multiple query variants generated
4. Results: More comprehensive

**When it shines:**
- Vague questions
- Multiple ways to phrase same idea
- Technical concepts with synonyms

---

### Strategy 4: Context Re-ranking
**Configuration:**
```env
RETRIEVAL_STRATEGY=reranking
RERANK_TOP_K=5
```

**Test:**
1. Ask: "Key features and benefits"
2. Wait longer (LLM re-scores each doc)
3. Results should be highly relevant
4. Compare with semantic - usually better quality

**Trade-off:**
- ✅ Higher accuracy
- ⏱️ Slower (LLM calls per document)
- 💰 More expensive (more API calls)

---

### Strategy 5: Self-Query Retriever
**Configuration:**
```env
RETRIEVAL_STRATEGY=self_query
SELF_QUERY_METADATA_FIELDS=source,page,type,date
```

**Requires:** Documents with metadata

**Test:**
1. Ask: "Find 2024 research papers"
2. Query parser extracts: {"year": "2024", "type": "research"}
3. Results filtered by metadata
4. Should return only matching documents

**Note:** Only works if your documents have metadata set

---

### Strategy 6: Multi-Hop Retrieval
**Configuration:**
```env
RETRIEVAL_STRATEGY=multihop
MULTIHOP_MAX_HOPS=3
```

**Test:**
1. Ask complex question: "How do neural networks improve machine learning performance through optimization?"
2. Observes: Question decomposed into sub-questions
3. Results synthesized from multiple searches
4. Better for complex, multi-part queries

**Performance:**
- ⏱️ Slower (multiple retrievals)
- 🎯 Better for complex questions
- ✅ Finds multi-faceted answers

---

## Comparison Test (5 minutes)

### Run Sequential Tests
```
Strategy       | Response Time | Result Quality | Costs
Semantic       | <1s          | ⭐⭐          | $
Hybrid         | ~1s          | ⭐⭐⭐        | $
Expansion      | ~2-3s        | ⭐⭐⭐        | $$
Re-ranking     | ~3-5s        | ⭐⭐⭐⭐      | $$
Self-Query     | ~1s          | ⭐⭐⭐        | $
Multi-Hop      | ~3-5s        | ⭐⭐⭐⭐      | $$$
```

### Questions to Test Each Strategy

**Test Set 1: Simple Questions**
- ✅ Good: Semantic
- ✅ Good: Hybrid

**Test Set 2: Ambiguous Questions**
- ✅ Good: Query Expansion
- ✅ Good: Multi-Hop

**Test Set 3: High Precision Needed**
- ✅ Best: Re-ranking

**Test Set 4: Filtered Results**
- ✅ Best: Self-Query

---

## UI Features Testing

### In Streamlit Sidebar:

1. **Retrieval Strategy Dropdown**
   - Switch between strategies in real-time
   - Strategy info shown below
   - Settings apply immediately

2. **Strategy Details Expander**
   - Shows current configuration
   - Verify weights, counts, settings

3. **Number of Documents Slider**
   - Adjust from 1-5
   - Compare quality vs quantity

4. **Temperature Slider**
   - Affects LLM generation
   - Lower = more focused
   - Higher = more creative

---

## Performance Metrics to Track

### For Each Strategy, Measure:

```python
import time

query = "Your test question"
strategy = "semantic"

# Time
start = time.time()
results = retriever_manager.retrieve(query, k=3)
elapsed = time.time() - start
print(f"Time: {elapsed:.2f}s")

# Quality (manual assessment 1-5)
quality = 4  # How relevant were results?

# Cost (API calls)
# Semantic: 0 LLM calls
# Hybrid: 0 LLM calls (just BM25 index)
# Expansion: N paraphrases
# Re-ranking: k documents scored
# Self-Query: 1 extraction call
# Multi-Hop: N sub-questions + k scores
```

---

## Troubleshooting Tests

### If Strategy Not Appearing:
```
1. Check .env file exists and has RETRIEVAL_STRATEGY set
2. Restart Streamlit: Ctrl+C, then re-run
3. Check logs for initialization errors
```

### If Results Seem Wrong:
```
1. Ensure documents loaded (check status indicator)
2. Try "Load Saved Store" if available
3. Reload documents if needed
```

### If LLM Strategies Fail:
```
1. Verify AWS credentials are valid
2. Check Bedrock region (us-east-1)
3. Ensure models are enabled in Bedrock
4. Check CloudWatch logs
```

---

## Recommended Configuration by Use Case

### E-Commerce Support
```env
RETRIEVAL_STRATEGY=hybrid
HYBRID_SEMANTIC_WEIGHT=0.4  # More keyword-based
```

### Research/Academic
```env
RETRIEVAL_STRATEGY=query_expansion
QUERY_EXPANSION_COUNT=5
```

### Legal/Compliance
```env
RETRIEVAL_STRATEGY=reranking
RERANK_TOP_K=10  # High precision
```

### Customer Service
```env
RETRIEVAL_STRATEGY=semantic
# Fast, simple, cost-effective
```

### Technical Documentation
```env
RETRIEVAL_STRATEGY=multihop
MULTIHOP_MAX_HOPS=3
```

---

## Next: Production Deployment

After successful testing:

1. **Choose optimal strategy** for your use case
2. **Set fixed RETRIEVAL_STRATEGY** in production .env
3. **Monitor costs** (especially re-ranking, multi-hop)
4. **A/B test** with real users if possible
5. **Adjust parameters** based on feedback

---

## Testing Checklist

- [ ] Semantic strategy works
- [ ] Hybrid strategy works
- [ ] Query expansion works
- [ ] Re-ranking works
- [ ] Self-query works (with metadata)
- [ ] Multi-hop works
- [ ] UI strategy selector works
- [ ] Strategy switching is instant
- [ ] Different k values work
- [ ] Performance metrics acceptable
- [ ] Costs within budget
- [ ] No errors in logs

---

**Ready to test? Start with: `RETRIEVAL_STRATEGY=semantic`**

Then progress through other strategies as you gain confidence.

Good luck! 🚀
