# Quick Start: Evaluation & Logging

**5-Minute Guide to Using the Evaluation System**

---

## Step 1: Install Dependencies (if needed)

```bash
cd "c:\Users\ipaul\Desktop\RAG Q&A (Local) with Bedrock + FAISS"
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 2: Configure Environment

Copy `.env.example` to `.env` and set:

```env
# Enable Evaluation Features
ENABLE_RAGAS_EVALUATION=true
ENABLE_RESPONSIBLE_AI=true

# Set Thresholds
RAGAS_FAITHFULNESS_THRESHOLD=0.80
RAGAS_CONTEXT_RECALL_THRESHOLD=0.70

# Configure Filtering
CONTENT_FILTER_KEYWORDS=inappropriate,offensive,harmful,violent
```

---

## Step 3: Run the Application

```bash
streamlit run app.py
```

---

## Step 4: Enable Features in UI

1. **Launch app** - Browser opens automatically
2. **Go to sidebar** → Scroll to "Evaluation & Logging"
3. **Check boxes:**
   - ☑ Enable RAGAS Evaluation
   - ☑ Enable Responsible AI Filtering

---

## Step 5: Ask a Question

1. Upload PDF documents (if not already done)
2. Create vector store
3. Ask a question in the main text box
4. Press Enter

---

## Step 6: View Results

### Performance Metrics (Always Shown)

```
┌─────────────────┬─────────────┬──────────────┐
│ Retrieval Time  │  LLM Time   │  Total Time  │
├─────────────────┼─────────────┼──────────────┤
│     125ms       │   2,350ms   │   2,500ms    │
└─────────────────┴─────────────┴──────────────┘
```

### RAGAS Metrics (If Enabled)

Expand "📊 RAGAS Quality Metrics":

```
Faithfulness:      0.85 ✅ (≥0.80)
Context Recall:    0.75 ✅ (≥0.70)
Context Precision: 0.67
Answer Relevancy:  0.90
```

### Source Documents

Expand "📚 Source Documents" to see retrieved content

---

## Step 7: Review Logs

### CSV Logs (Excel)

```bash
# Open in Excel
start logs\query_log_20251118.csv
```

**Columns:**
- timestamp
- query
- response
- retrieval_strategy
- total_latency_ms
- faithfulness
- context_recall
- response_filtered

### JSON Logs (Programmatic)

```python
import json

with open('logs/query_log_20251118.json', 'r') as f:
    logs = json.load(f)

# Print summary
for log in logs:
    print(f"Query: {log['query']}")
    print(f"Latency: {log['performance_metrics']['total_latency_ms']}ms")
    print(f"Faithfulness: {log['ragas_metrics']['faithfulness']}")
    print()
```

---

## Quick Tips

### 🚀 Fast Mode (Development)

Disable RAGAS for faster responses:

```env
ENABLE_RAGAS_EVALUATION=false  # ✅ Fast
ENABLE_RESPONSIBLE_AI=true     # ✅ Keep safety
```

### 📊 Quality Mode (Production)

Enable everything for quality assurance:

```env
ENABLE_RAGAS_EVALUATION=true   # ✅ Quality checks
ENABLE_RESPONSIBLE_AI=true     # ✅ Content filtering
LOG_RETENTION_DAYS=90          # ✅ Long retention
```

### 💰 Cost Mode (Budget-Conscious)

Minimize LLM calls:

```env
ENABLE_RAGAS_EVALUATION=false  # ❌ Save money
ENABLE_RESPONSIBLE_AI=true     # ✅ Keyword filtering only
```

---

## What to Expect

### Without RAGAS (Fast)
- Response time: 1-3 seconds
- Metrics: Performance only
- Cost: Normal query cost

### With RAGAS (Quality)
- Response time: 3-8 seconds
- Metrics: Performance + RAGAS scores
- Cost: +$0.01-0.03 per query

---

## Troubleshooting

### "Import Error"
```bash
pip install -r requirements.txt
```

### "No logs created"
```bash
mkdir logs
```

### "RAGAS too slow"
```env
ENABLE_RAGAS_EVALUATION=false
```

### "All responses filtered"
```env
# Check your keyword list
CONTENT_FILTER_KEYWORDS=inappropriate,offensive,harmful
```

---

## Example Analysis

### View Average Quality

```python
import pandas as pd

df = pd.read_csv('logs/query_log_20251118.csv')

print(f"Average Faithfulness: {df['faithfulness'].mean():.2f}")
print(f"Average Context Recall: {df['context_recall'].mean():.2f}")
print(f"Queries Meeting Threshold: {df['meets_threshold'].sum()}/{len(df)}")
```

### View Performance by Strategy

```python
import pandas as pd

df = pd.read_csv('logs/query_log_20251118.csv')

print(df.groupby('retrieval_strategy')['total_latency_ms'].mean())
```

---

## Next Steps

1. ✅ Test with your documents
2. ✅ Review quality metrics
3. ✅ Analyze logs
4. ✅ Optimize configuration
5. ✅ Deploy to production

---

## Full Documentation

- **Complete Guide:** `EVALUATION_LOGGING_GUIDE.md`
- **Implementation:** `PHASE4_IMPLEMENTATION.md`
- **Completion Report:** `PHASE4_COMPLETE.md`

---

**Ready to use in 5 minutes!** 🚀
