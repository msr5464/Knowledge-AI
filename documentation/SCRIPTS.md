# Deployment Scripts Guide

This directory contains platform-specific installation and execution scripts for InHouse Knowledge AI.

## Available Scripts

### Installation Scripts

- **`install.sh`** - macOS/Linux installation script
- **`install.ps1`** - Windows PowerShell installation script
- **`install.bat`** - Windows Command Prompt installation script

### Execution Scripts

- **`run.sh`** - macOS/Linux run script
- **`run.ps1`** - Windows PowerShell run script
- **`run.bat`** - Windows Command Prompt run script

### Storage Initialization

- **`init_storage.sh`** - macOS/Linux storage initialization
- **`init_storage.ps1`** - Windows PowerShell storage initialization
- **`init_storage.bat`** - Windows Command Prompt storage initialization

### Utility Scripts

- **`check_platform.sh`** - Platform detection utility
- **`fix_port.sh`** - Port conflict resolution utility

## Usage

### Windows

**PowerShell (Recommended):**
```powershell
.\scripts\install.ps1
.\scripts\run.ps1
```

**Command Prompt:**
```cmd
scripts\install.bat
scripts\run.bat
```

### macOS/Linux

```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Run installation
bash scripts/install.sh

# Run application
bash scripts/run.sh
```

## What the Scripts Do

### Installation Scripts

1. **Check Python 3.9+ installation**
2. **Create virtual environment** (`venv/`)
3. **Activate virtual environment**
4. **Upgrade pip** to latest version
5. **Install dependencies** from `requirements.txt`
6. **Fix dependency versions** (sentence-transformers compatibility)
7. **Initialize storage directories**
8. **Check and install Ollama** (if not present)
9. **Start Ollama service** (if not running)
10. **Pull default model** (llama3.2:3b)
11. **Create configuration file** from `config/env.example` → `config/.env`

### Run Scripts

1. **Check if virtual environment exists**
2. **Activate virtual environment**
3. **Check/create configuration file** (if missing)
4. **Start Flask application** with configured port and host

### Storage Initialization

Creates the following directories:
- `storage/documents/` - Uploaded documents
- `storage/chroma_db/` - Vector database
- `storage/embedding_cache/` - Embedding cache
- `logs/` - Application logs

## Troubleshooting

### Scripts Not Executable (macOS/Linux)

```bash
chmod +x scripts/*.sh
```

### PowerShell Execution Policy (Windows)

If scripts are blocked:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Scripts Not Found

Make sure you're running from the project root directory:
```bash
# Check current directory
pwd  # macOS/Linux
cd   # Windows

# Should show: /path/to/my-rag
```

### Virtual Environment Issues

If virtual environment creation fails:
```bash
# Remove old venv and recreate
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Then run install script again
```

## Manual Execution

If scripts fail, you can run commands manually:

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
bash scripts/init_storage.sh
cp config/env.example config/.env
# Edit config/.env
python backend/app.py
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
scripts\init_storage.bat
copy config\env.example config\.env
REM Edit config\.env
python backend\app.py
```

## Script Details

### install.sh / install.ps1 / install.bat

Performs complete system setup:
- Python environment setup
- Dependency installation
- Ollama installation and configuration
- Configuration file creation
- Storage initialization

**Output:** Ready-to-run system

### run.sh / run.ps1 / run.bat

Starts the Flask application:
- Activates virtual environment
- Loads configuration
- Starts server on configured port

**Output:** Running server at http://localhost:PORT

### init_storage.sh / init_storage.ps1 / init_storage.bat

Creates required storage directories:
- Documents directory
- ChromaDB directory
- Embedding cache directory
- Logs directory

**Output:** All storage directories created

## Platform-Specific Notes

### Windows
- PowerShell scripts are recommended over CMD
- May require execution policy changes
- Paths use backslashes in CMD, forward slashes in PowerShell

### macOS
- Python 3.9+ usually pre-installed
- Homebrew can be used for Python/Ollama
- Port 5000 may be used by AirPlay Receiver (default port is 5001)

### Linux
- Requires Python 3.9+ and pip
- May need system packages (python3-venv, etc.)
- Ollama installation via official script

## See Also

- **[README.md](../README.md)** - Main project documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment guide
- **[API.md](API.md)** - REST API documentation

