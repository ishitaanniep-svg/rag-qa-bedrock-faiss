# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Prerequisites Check
```powershell
# Verify Python 3.8+
python --version

# Verify AWS CLI installed
aws --version

# Configure AWS (if not done)
aws configure
```

### Step 2: Environment Setup
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Setup
```powershell
# Run setup verification
python setup.py
```

Expected output:
```
✅ Python version detected
✅ AWS credentials found
✅ Bedrock API accessible
```

### Step 4: Launch Application
```powershell
streamlit run app.py
```

Browser will open at `http://localhost:8501`

## Using the App

### First Time (Create Vector Store)
1. **Upload PDFs**: Use sidebar to upload 1+ PDF files
2. **Create Store**: Click "🔄 Create Vector Store"
3. **Wait**: Processing takes 1-5 minutes depending on PDF size
4. **Ask Questions**: Start typing questions

### Subsequent Uses (Load Vector Store)
1. **Load Store**: Click "💾 Load Saved Store"
2. **Ask Questions**: Immediately start asking (much faster!)

## Example Workflow

```
1. Upload: "research_paper.pdf", "manual.pdf"
   ↓
2. Click "Create Vector Store"
   ↓
3. See: "✅ Vector store created successfully!"
   ↓
4. Ask: "What are the main findings?"
   ↓
5. Get: AI answer with source citations
```

## Common Commands

```powershell
# Activate environment (each session)
.\venv\Scripts\Activate.ps1

# Install new packages
pip install <package_name>

# Update dependencies
pip install -r requirements.txt --upgrade

# Check environment
pip list

# Deactivate environment
deactivate

# Delete vector store and start fresh
Remove-Item faiss_store -Recurse
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Credentials Error** | Run `aws configure` |
| **Bedrock Model Error** | Enable models in AWS Console |
| **Import Error** | Reinstall: `pip install -r requirements.txt` |
| **Slow Processing** | Normal first time; cached on reuse |
| **Bad Answers** | Adjust k=4-5, check PDF quality |

## Environment Variables (Optional)

Create `.env` file:
```
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=default
```

## Next Steps

- Read full [README.md](README.md)
- Explore advanced settings in sidebar
- Try different PDF types
- Adjust temperature for different response styles
- Save vector stores for frequently used documents

## Need Help?

1. Check [README.md](README.md) Troubleshooting section
2. Review AWS Bedrock documentation
3. Verify AWS credentials: `aws sts get-caller-identity`
4. Check internet connection for AWS API calls

---

**Ready to go! 🎉**
