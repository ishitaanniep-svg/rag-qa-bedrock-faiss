# 📁 Project Structure & Files Overview

## Complete File Manifest

```
RAG Q&A (Local) with Bedrock + FAISS/
│
├── 📄 app.py                    ⭐ MAIN APPLICATION
│   └─ Streamlit web interface for RAG chatbot
│   └─ Document upload and processing
│   └─ Q&A interaction with source citations
│
├── 🛠️ utils.py                   ⭐ UTILITIES & HELPERS
│   └─ DocumentProcessor: Load and split PDFs
│   └─ VectorStoreManager: Manage FAISS indexes
│   └─ RAGConfig: Configuration management
│
├── 📦 requirements.txt          ⭐ DEPENDENCIES
│   └─ All Python packages needed
│   └─ Pinned versions for stability
│
├── ⚙️ setup.py                   ⭐ VERIFICATION SCRIPT
│   └─ Check Python version
│   └─ Verify AWS credentials
│   └─ Test Bedrock access
│   └─ Install dependencies
│
├── 📖 README.md                 ⭐ FULL DOCUMENTATION
│   └─ Complete setup guide
│   └─ Usage instructions
│   └─ Configuration details
│   └─ Troubleshooting guide
│   └─ Advanced usage tips
│
├── 🚀 QUICKSTART.md             ⭐ FAST SETUP GUIDE
│   └─ 5-minute setup steps
│   └─ Quick commands reference
│   └─ Common issues & solutions
│
├── .env.example                 ⭐ CONFIGURATION TEMPLATE
│   └─ AWS region settings
│   └─ Model IDs
│   └─ Processing parameters
│
├── .gitignore                   ⭐ VERSION CONTROL
│   └─ Ignore sensitive files
│   └─ Ignore vector stores
│   └─ Ignore environment files
│
└── 📁 faiss_store/ (created after first run)
    ├─ index.faiss              Vector index
    ├─ index.pkl                Index metadata
    ├─ docstore.pkl             Document storage
    └─ metadata.json            Processing metadata
```

## 🎯 Core Components

### 1. **app.py** - Main Application
```python
Features:
  ✅ Streamlit UI with sidebar
  ✅ Multi-PDF upload support
  ✅ FAISS vector store creation
  ✅ Amazon Bedrock integration
  ✅ Q&A with source citations
  ✅ Chat history tracking
  ✅ Session state management
  ✅ Error handling & logging
```

**Key Functions:**
- `initialize_bedrock_clients()`: Setup AWS Bedrock
- `load_and_process_pdfs()`: Extract text from PDFs
- `create_vector_store()`: Build FAISS index
- `create_qa_chain()`: Setup RAG pipeline
- `main()`: Streamlit app entry point

### 2. **utils.py** - Helper Utilities
```python
Classes:
  • DocumentProcessor: PDF loading and chunking
  • VectorStoreManager: Save/load FAISS indexes
  • RAGConfig: Configuration defaults

Functions:
  • save_config(): Persist config to JSON
  • load_config(): Load config from JSON
  • Logging utilities
```

### 3. **requirements.txt** - Dependencies
```
Core Libraries:
  • streamlit: Web UI framework
  • boto3: AWS SDK
  • langchain: LLM orchestration
  • langchain-aws: Bedrock integration
  • langchain-community: Vector stores & loaders
  • faiss-cpu: Vector similarity search
  • pypdf: PDF processing
  • python-dotenv: Environment variables
```

### 4. **setup.py** - Verification Script
```
Checks:
  ✓ Python version (3.8+)
  ✓ AWS credentials configured
  ✓ Bedrock model access
  ✓ Dependency installation

Usage:
  python setup.py
```

## 📚 Documentation Files

### README.md
- Complete project overview
- Installation instructions
- Configuration guide
- Usage walkthrough
- Troubleshooting tips
- Advanced usage examples
- Security considerations

### QUICKSTART.md
- 5-minute setup
- Step-by-step guide
- Common commands
- Quick troubleshooting
- Example workflow

## 🔄 Data Flow Architecture

```
PDF Upload
    ↓
DocumentProcessor.load_pdf()
    ↓
RecursiveCharacterTextSplitter
    ↓
Documents + Embeddings
    ↓
FAISS.from_documents()
    ↓
VectorStoreManager.save_store()
    ↓
faiss_store/ (persisted locally)
    ↓
User Question
    ↓
Embeddings Query
    ↓
FAISS Similarity Search (top-k retrieval)
    ↓
Context + Question
    ↓
Claude 3 (Bedrock LLM)
    ↓
Answer with Sources
```

## 🔧 Configuration Options

### In Code (app.py)
```python
# Document processing
chunk_size = 1000
chunk_overlap = 200

# Retrieval
search_kwargs = {"k": 3}

# Models
EMBEDDING_MODEL = "amazon.titan-embed-text-v1"
LLM_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
```

### Via Sidebar (UI)
```
Adjustable Settings:
  • Number of documents to retrieve (1-5)
  • Model temperature (0.0-1.0)
  • Custom prompts (advanced)
```

### Via .env File (Optional)
```
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=default
CHUNK_SIZE=1000
RETRIEVAL_K=3
```

## 🚀 Getting Started

### 1. Initial Setup
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify setup
python setup.py
```

### 2. Configure AWS
```powershell
aws configure
# Enter: Access Key ID, Secret Key, Region (us-east-1)
```

### 3. Run Application
```powershell
streamlit run app.py
```

### 4. Use Application
- Upload PDFs
- Create vector store
- Ask questions
- Review answers with sources

## 📊 File Dependencies

```
app.py
├── requires: streamlit, boto3, langchain libraries
├── uses: utils.py (optional, not required)
└── outputs: faiss_store/, chat_history.json

utils.py
├── requires: langchain libraries
├── provides: DocumentProcessor, VectorStoreManager, RAGConfig
└── used by: app.py (optional)

setup.py
├── requires: boto3, subprocess
├── standalone: runs independently
└── verifies: Python, AWS, Bedrock

requirements.txt
├── Lists all dependencies
└── Used by: pip install -r requirements.txt
```

## 🔐 Sensitive Files

Files to keep private (covered by .gitignore):
```
❌ .env                          AWS credentials
❌ faiss_store/                  Document embeddings
❌ chat_history.json             Chat records
❌ .aws/                         AWS config/credentials
```

Files safe to share:
```
✅ app.py                        Application code
✅ utils.py                      Utility code
✅ requirements.txt              Dependencies
✅ README.md, QUICKSTART.md      Documentation
✅ .env.example                  Configuration template
✅ .gitignore                    Git ignore rules
```

## 📈 Project Stats

```
Total Files: 8
Core Code: 2 files (app.py, utils.py)
Documentation: 4 files (README, QUICKSTART, .env.example, this file)
Configuration: 2 files (requirements.txt, .gitignore, setup.py)

Lines of Code:
  • app.py: ~350 lines
  • utils.py: ~250 lines
  • setup.py: ~150 lines
  • Total: ~750 lines

Dependencies: 13 packages
```

## 🎓 Learning Path

1. **Beginner**: Run QUICKSTART.md
2. **Intermediate**: Read README.md
3. **Advanced**: Study app.py code
4. **Expert**: Modify utils.py and prompts

## 🤝 Extending the Application

### Add Custom Features
1. Edit `app.py` main() function
2. Add new sidebar sections
3. Implement new retrieval strategies
4. Add persistence features

### Modify Models
1. Update model IDs in `utils.py` RAGConfig
2. Adjust chunk sizes for your documents
3. Change temperature for different response styles

### Improve Answers
1. Fine-tune prompts in `create_qa_chain()`
2. Increase retrieval_k for more context
3. Adjust chunk_size/overlap for better chunks

## 📞 Support Resources

- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [LangChain Docs](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

**You're all set! Happy building! 🚀**
