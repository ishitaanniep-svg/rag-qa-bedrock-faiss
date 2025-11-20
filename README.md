# Local RAG Q&A Chatbot with Amazon Bedrock & FAISS

A Streamlit-based question-answering application that uses Retrieval-Augmented Generation (RAG) to answer questions about PDF documents. The application leverages Amazon Bedrock for AI generation and embeddings, combined with FAISS for local vector storage.

## 🎯 Features

- **📄 Multi-PDF Support**: Upload and process multiple PDF documents
- **🔍 Semantic Search**: FAISS-based vector similarity search
- **🤖 AI-Powered Answers**: Amazon Bedrock Claude 3 for intelligent responses
- **💾 Local Vector Store**: Persistent FAISS indexes for efficient reuse
- **📚 Source Attribution**: View source documents for each answer
- **💬 Chat History**: Keep track of conversations
- **⚙️ Configurable Settings**: Adjust retrieval depth and model temperature

## 📋 Prerequisites

- **Python 3.8+** (recommended 3.10+)
- **AWS Account** with Bedrock access
- **AWS CLI** configured with appropriate credentials
- **Virtual Environment** (recommended)

## 🚀 Quick Start

### 1. Clone or Setup the Project

```bash
cd "RAG Q&A (Local) with Bedrock + FAISS"
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials

**Option A: Using AWS CLI (Recommended)**
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (us-east-1)
```

**Option B: Using Environment Variables**
```powershell
# PowerShell
$env:AWS_ACCESS_KEY_ID = "your_access_key"
$env:AWS_SECRET_ACCESS_KEY = "your_secret_key"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

**Option C: Using .env File**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# (Not recommended for production)
```

### 5. Ensure Bedrock Model Access

Make sure your AWS account has access to the required Bedrock models:
- **amazon.titan-embed-text-v1** (for embeddings)
- **anthropic.claude-3-sonnet-20240229-v1:0** (for generation)

To enable access:
1. Go to AWS Console → Bedrock → Model Access
2. Request access to the models (usually instant approval)

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Upload Documents
1. Click "📤 Upload Documents" in the sidebar
2. Select one or more PDF files
3. Click "Open" to upload

### Step 2: Create Vector Store
1. Click "🔄 Create Vector Store" button
2. The app will:
   - Extract text from PDFs
   - Split into chunks (1000 chars with 200 char overlap)
   - Generate embeddings using Bedrock
   - Create a FAISS index
   - Save locally for future use

### Step 3: Ask Questions
1. Enter your question in the text field
2. The app will:
   - Search for relevant document chunks
   - Send context + question to Claude
   - Generate an answer
   - Display source documents

### Step 4: Review Results
- View the AI-generated answer
- Expand "📚 Source Documents" to see references
- Check chat history for previous questions

## 🔄 Reusing Vector Stores

After creating a vector store, it's saved locally in the `faiss_store/` directory.

**To reuse:**
1. Click "💾 Load Saved Store" in the sidebar
2. The app will load the existing index
3. Start asking questions immediately (no re-processing needed)

## ⚙️ Configuration Options

### Sidebar Settings

| Setting | Range | Default | Purpose |
|---------|-------|---------|---------|
| **Number of Documents** | 1-5 | 3 | How many similar docs to retrieve |
| **Temperature** | 0.0-1.0 | 0.7 | Model creativity (higher = more creative) |

### Code Configuration

In `app.py`, you can modify:

```python
# Chunk size for document splitting
chunk_size=1000

# Overlap between chunks
chunk_overlap=200

# Number of documents for retrieval
search_kwargs={"k": 3}
```

## 🏗️ Project Structure

```
RAG Q&A (Local) with Bedrock + FAISS/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── README.md             # This file
└── faiss_store/          # Local vector store (created after first run)
    ├── index.faiss
    ├── index.pkl
    └── docstore.pkl
```

## 🔧 Troubleshooting

### Issue: "No credentials found"
**Solution:** Configure AWS credentials using `aws configure` or set environment variables

### Issue: "Model not found" or "Access Denied"
**Solution:** Ensure your AWS account has access to Bedrock models:
- Go to AWS Console → Bedrock → Model Access
- Request access to the required models

### Issue: "FAISS is not installed properly"
**Solution:** Reinstall with CPU support
```bash
pip install --upgrade faiss-cpu
```

### Issue: "PDF processing is slow"
**Solution:** This is normal for first-time processing. The vector store is cached locally for faster reuse.

### Issue: "Poor answer quality"
**Solution:** Try these improvements:
1. Increase retrieval documents (k=4 or 5)
2. Check that your PDFs have clear, readable text
3. Ask more specific questions
4. Adjust temperature slider to 0.5-0.7 for better focus

## 📊 How RAG Works

```
User Question
     ↓
[Query Vector] ← Embedding Model (Bedrock)
     ↓
[FAISS Search] → Retrieve Top-K Similar Chunks
     ↓
[Context Assembly] → Combine question + retrieved chunks
     ↓
[LLM Generation] ← Claude 3 (Bedrock)
     ↓
Answer with Source Citations
```

## 🔐 Security Considerations

1. **AWS Credentials**: Never commit credentials to version control
2. **Vector Store**: The `faiss_store/` contains document embeddings (not raw text)
3. **Environment Variables**: Use `.env` file locally, never share credentials
4. **PDF Data**: Ensure PDFs don't contain sensitive information

## 💡 Tips for Best Results

1. **Quality PDFs**: Use text-based PDFs (not scanned images)
2. **Relevant Questions**: Be specific and clear in your questions
3. **Document Size**: 5-50 MB per session is optimal
4. **Chunk Size**: Default 1000 chars works well for most documents
5. **Retrieval Count**: Start with 3, increase if answers seem incomplete

## 🚀 Advanced Usage

### Custom Prompt Template

Modify the prompt template in `create_qa_chain()`:

```python
prompt_template = """Your custom prompt here
Context: {context}
Question: {question}
Answer:"""
```

### Different Models

Change the model IDs in `initialize_bedrock_clients()`:

```python
# For different embedding models
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2-v1")

# For different generation models
llm = BedrockLLM(model_id="anthropic.claude-3-opus-20240229-v1:0")
```

### Persistent Chat

Modify `chat_history` handling to save to JSON:

```python
import json

def save_chat_history():
    with open("chat_history.json", "w") as f:
        json.dump(st.session_state.chat_history, f)
```

## 📚 Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [RAG Pattern](https://docs.anthropic.com/claude/reference/models-overview)

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review AWS Bedrock model access
3. Verify Python version and dependencies
4. Check AWS credential configuration

## 🎓 Learning Resources

This application demonstrates:
- **RAG Pattern**: Combining retrieval with generation
- **Vector Embeddings**: Semantic search using Bedrock
- **FAISS**: Efficient similarity search
- **LangChain**: LLM orchestration
- **Streamlit**: Rapid ML app development

---

**Happy Q&A-ing! 🚀**
