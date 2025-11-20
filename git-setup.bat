@echo off
REM Git Setup Script for RAG Q&A Project

echo ========================================
echo Git Setup for RAG Q&A with Bedrock
echo ========================================
echo.

REM Configure Git user
git config --global user.name "ishitaanniep-svg"
git config --global user.email "ishitaanniep@gmail.com"
echo ✅ Git user configured

REM Initialize repository
git init
echo ✅ Git repository initialized

REM Add all files
git add .
echo ✅ Files staged

REM Create initial commit
git commit -m "Initial commit: RAG Q&A chatbot with AWS Bedrock, FAISS, and advanced retrieval strategies"
echo ✅ Initial commit created

echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Go to: https://github.com/new
echo 2. Create a new repository named: rag-qa-bedrock-faiss
echo 3. Don't initialize with README
echo 4. Copy the repository URL
echo 5. Run this command (replace YOUR_USERNAME):
echo.
echo    git remote add origin https://github.com/ishitaanniep-svg/rag-qa-bedrock-faiss.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo ========================================

pause
