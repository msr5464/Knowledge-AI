#!/bin/bash
# Installation Script for macOS/Linux
# Bash script to set up the RAG system

set -e  # Exit on error

echo "========================================"
echo "RAG System Installation Script"
echo "========================================"
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅ Python found: $PYTHON_VERSION"
echo ""

# Check Python version (3.9+)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Python 3.9+ required. Found: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Fix any version conflicts (sentence-transformers compatibility)
echo "Fixing dependency versions..."
pip install --upgrade sentence-transformers huggingface-hub 2>&1 | grep -E "(Successfully|Requirement|Installing)" | tail -5 || true

# Initialize storage
echo ""
echo "Initializing storage directories..."
bash scripts/init_storage.sh

# Check and install Ollama
echo ""
echo "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing Ollama..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Detected macOS. Installing Ollama..."
        if command -v brew &> /dev/null; then
            echo "Installing via Homebrew..."
            brew install ollama
        else
            echo "⚠️  Homebrew not found. Please install Ollama manually:"
            echo "   Visit: https://ollama.ai/download/mac"
            echo "   Or install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo ""
            read -p "Press Enter after installing Ollama manually, or Ctrl+C to exit..."
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Detected Linux. Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "⚠️  Unsupported OS. Please install Ollama manually from https://ollama.ai"
        read -p "Press Enter after installing Ollama manually, or Ctrl+C to exit..."
    fi
    
    # Verify installation
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama installed successfully"
    else
        echo "❌ Ollama installation failed. Please install manually from https://ollama.ai"
        exit 1
    fi
else
    echo "✅ Ollama found: $(ollama --version 2>&1 | head -1)"
fi

# Start Ollama service if not running
echo ""
echo "Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Ollama service not running. Starting Ollama..."
    # Start Ollama in background
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    echo "✅ Started Ollama service (PID: $OLLAMA_PID)"
    
    # Wait for Ollama to be ready
    echo "Waiting for Ollama to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            echo "✅ Ollama is ready"
            break
        fi
        sleep 1
    done
    
    if [ $i -eq 30 ]; then
        echo "⚠️  Ollama did not start in time. Please start it manually: ollama serve"
    fi
else
    echo "✅ Ollama service is running"
fi

# Pull default model if not available
echo ""
echo "Checking for Ollama model (llama3.2:3b)..."
if ollama list 2>/dev/null | grep -q "llama3.2:3b"; then
    echo "✅ Model llama3.2:3b is available"
else
    echo "⚠️  Model llama3.2:3b not found. Pulling model (this may take a few minutes)..."
    ollama pull llama3.2:3b
    if [ $? -eq 0 ]; then
        echo "✅ Model llama3.2:3b pulled successfully"
    else
        echo "⚠️  Failed to pull model. You can pull it manually later: ollama pull llama3.2:3b"
    fi
fi

# Copy environment file
echo ""
echo "Setting up configuration..."
if [ ! -f "config/.env" ]; then
    cp config/env.example config/.env
    echo "✅ Configuration file created: config/.env"
    echo ""
    echo "📝 Configuration Setup:"
    echo "   The .env file has been created from env.example"
    echo "   This file is hidden (not in git) and contains your personal settings"
    echo ""
    echo "⚠️  IMPORTANT: Before running in production, edit config/.env and set:"
    echo "   1. SECRET_KEY - Generate a secure random key"
    echo ""
    echo "   To generate a secure SECRET_KEY, run:"
    echo "   python -c \"import secrets; print(secrets.token_hex(32))\""
    echo ""
    echo "   For development, the default values will work, but change SECRET_KEY for production!"
    echo ""
    echo "   Default admin credentials: admin / admin123"
    echo "   ⚠️  Change the default admin password after first login!"
else
    echo "⚠️  Configuration file already exists: config/.env"
    echo "   Skipping creation. Edit it manually if needed."
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure your environment (optional for development):"
echo "   - Edit config/.env to customize settings"
echo "   - For production: Change SECRET_KEY"
echo "   - Default admin credentials: admin / admin123 (change after first login!)"
echo ""
echo "2. Start the application:"
echo "   bash scripts/run.sh"
echo ""
echo "3. Access the interfaces:"
echo "   - Admin Panel: http://localhost:5001/admin"
echo "   - Customer Panel: http://localhost:5001/customer"
echo "   - API Base: http://localhost:5001/api"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Quick start guide"
echo "   - DEPLOYMENT.md - Detailed deployment guide"
echo "   - config/env.example - Configuration template with comments"
echo ""

