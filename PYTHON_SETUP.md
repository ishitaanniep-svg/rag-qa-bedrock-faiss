# 🐍 Python Installation & Setup Guide

## Problem Detected
Python is not properly installed on your system. The error about Microsoft Store redirects occurs when Python isn't in your system PATH.

## Solution: Install Python Properly

### Option 1: Official Python Installer (Recommended)

1. **Download Python 3.11 or 3.12**
   - Go to: https://www.python.org/downloads/
   - Click "Download Python 3.12" (or latest stable)

2. **Run the Installer**
   - Double-click the .exe file
   - **IMPORTANT: Check the box "Add Python to PATH"** ✓
   - Choose "Install Now"
   - Wait for installation to complete

3. **Verify Installation**
   ```powershell
   python --version
   python -m pip --version
   ```

### Option 2: Windows Package Manager (Fastest)

```powershell
# If you have Windows Package Manager installed:
winget install Python.Python.3.12

# Then verify:
python --version
```

### Option 3: Using Chocolatey

```powershell
# If you have Chocolatey installed:
choco install python

# Then verify:
python --version
```

### Option 4: Using Microsoft Store (Not Recommended)

Open Microsoft Store and search for "Python 3.12" - click Install.
(Note: This version has PATH limitations, which is what caused your issue)

---

## After Python Installation

Once Python is installed, restart PowerShell and verify:

```powershell
# Check Python version
python --version

# Check pip (package manager)
pip --version

# Check Python location
python -c "import sys; print(sys.executable)"
```

Expected output example:
```
Python 3.12.0
pip 23.2.1 from C:\Users\ipaul\AppData\Local\Programs\Python\Python312\lib\site-packages\pip (python 3.12)
C:\Users\ipaul\AppData\Local\Programs\Python\Python312\python.exe
```

---

## Quick Setup After Python Installation

Once Python is installed and working:

```powershell
# Navigate to project folder
cd "C:\Users\ipaul\Desktop\RAG Q&A (Local) with Bedrock + FAISS"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify setup
python setup.py
```

---

## Fixing the Windows App Alias Issue

If you still get the Microsoft Store redirect error after installing Python:

### Step 1: Disable App Execution Aliases
1. Open **Settings**
2. Go to **Apps** → **Advanced app settings**
3. Click **App execution aliases**
4. Find "python.exe" and "python3.exe"
5. Toggle them **OFF** (both should be gray/disabled)
6. Restart PowerShell

### Step 2: Clear PowerShell Cache
```powershell
# Restart PowerShell or run:
Remove-Item -Path "$PROFILE\..\profile.ps1" -ErrorAction SilentlyContinue

# Close and reopen PowerShell
```

---

## Troubleshooting

### If "python: not found" after fresh install:
```powershell
# Restart PowerShell first!
# Close all PowerShell windows and open a NEW one

python --version
```

### If only Works with python3 and not python:
You may have Python 3 installed but not aliased. Use:
```powershell
python3 -m venv venv
python3 -m pip install -r requirements.txt
```

### If PATH is not set:
```powershell
# Manually find Python:
Get-ChildItem -Path "C:\Program Files*" -Filter "python.exe" -Recurse

# Add to PATH manually (replace path with your Python location):
$env:PATH += ";C:\Users\ipaul\AppData\Local\Programs\Python\Python312"
```

---

## Verify Everything Works

After fixing Python, run this test:

```powershell
# Test 1: Python works
python --version

# Test 2: Pip works
pip --version

# Test 3: Can create venv
python -m venv test_venv
Remove-Item test_venv -Recurse

# Test 4: Can install packages
pip install requests
pip uninstall requests -y

# Test 5: Setup verification
cd "C:\Users\ipaul\Desktop\RAG Q&A (Local) with Bedrock + FAISS"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python setup.py
```

If all tests pass, you're ready to launch the app:
```powershell
streamlit run app.py
```

---

## Prevention Tips

✅ Always check "Add Python to PATH" during installation
✅ Install from official python.org (not Microsoft Store)
✅ Close and reopen PowerShell after installation
✅ Use `python -m venv` instead of `virtualenv`
✅ Keep Python updated: `python -m pip install --upgrade pip`

---

**Need help?** Follow these steps in order and let me know which step fails.
