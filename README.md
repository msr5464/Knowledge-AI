# <a href="https://www.linkedin.com/in/mukesh-rajput/"><img align="right" src="https://raw.githubusercontent.com/msr5464/Selenium-Automation-Framework/refs/heads/master/Logo-full.png" alt="Mukesh" height="40"></a> INHOUSE KNOWLEDGE AI

**🤖 AI-Powered Document Intelligence | LLM-Driven Q&A | RAG Technology | Knowledge Hub ~ QnA with Documents**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Demo Video](#demo-video)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**InHouse Knowledge AI** is a cutting-edge, production-ready AI-powered RAG (Retrieval-Augmented Generation) system that transforms your documents into an intelligent knowledge base. Leverage advanced LLM technology to ask questions in natural language and get instant, accurate answers from your document collection. **100% locally hosted, completely private, and secure** - your data never leaves your machine, ensuring maximum privacy and security for sensitive documents (or use OpenAI API for cloud-based AI processing).

### 💡 Some of Real-World Use Cases

**Example 1: Test Documentation Intelligence**
- Upload your test plans, test cases, and requirements documents
- Ask: *"What are the test scenarios for the login functionality?"*
- Get instant AI-powered answers with exact document references
- Quickly find test coverage gaps or missing test cases

**Example 2: Bug Report & Test Result Analysis**
- Upload bug reports, test execution results, and defect logs
- Ask: *"What are the common failure patterns in the last sprint?"*
- AI analyzes patterns and provides insights from your test data
- Identify trends and prioritize testing efforts

**Example 3: API & Technical Documentation Query**
- Upload API specifications, technical docs, and test data sheets
- Ask: *"What are the authentication requirements for the payment API?"*
- Get precise answers from your technical documentation
- Accelerate test case creation and test data preparation

### What It Does

- **🤖 AI-Powered Document Intelligence**: Transform static documents into an interactive knowledge base using advanced AI and LLM technology
- **💬 Natural Language Q&A**: Ask questions in plain English and receive intelligent, context-aware answers powered by Large Language Models
- **📚 Multi-Format Document Support**: Seamlessly process PDF, CSV, Excel, Word (.docx, .doc, .docs), PowerPoint (.pptx, .ppt), and text files (.txt, .text, .md) with AI-driven content extraction
- **🔒 Flexible LLM Options**: Choose between local processing with Ollama (100% private, no data leaves your machine) or cloud-based OpenAI API for enhanced performance
- **🔌 REST API Integration**: Full programmatic access with AI-powered endpoints for seamless integration with other systems

---

## 🎥 Demo Video

Watch a comprehensive demo and explanation of the InHouse Knowledge AI system:

[![Demo Video](https://img.youtube.com/vi/L2yZFrl5NPc/0.jpg)](https://youtu.be/L2yZFrl5NPc)

**[Click here to watch the full demo on YouTube](https://youtu.be/L2yZFrl5NPc)**

---

## ✨ Features

### Core AI & LLM Capabilities

- 🤖 **Flexible LLM Integration**: Choose between Ollama (local, free, private) or OpenAI API (cloud-based, powerful) - supports multiple models including llama3.2, mistral, GPT-4, and more
- 🧠 **AI-Powered Semantic Understanding**: Deep learning embeddings for intelligent document comprehension
- 💬 **Natural Language Processing**: Ask questions naturally - the AI understands context and intent
- 📄 **Multi-Format AI Processing**: Intelligent extraction from PDF, CSV, Excel (.xlsx, .xls), Word (.docx, .doc, .docs), PowerPoint (.pptx, .ppt), and Text files (.txt, .text, .md)
- 🔍 **Vector-Based Semantic Search**: Advanced AI-driven search using ChromaDB for contextually relevant results
- 💾 **Persistent AI Knowledge Base**: Documents and AI embeddings persist across restarts
- ⚡ **AI Performance Optimization**: Smart caching for LLM queries and embeddings for lightning-fast responses
- 🔐 **Enterprise-Grade Security**: Username/password authentication with role-based access control (Admin/Customer)
- 👥 **User Management System**: Complete user administration - create users, manage roles, reset passwords, delete users
- 🔀 **Flexible Answer Modes**: Toggle between RAG mode (uses uploaded documents for context-aware answers) or Direct LLM mode (uses LLM's general knowledge for faster, generic answers)

### Advanced AI Features

- **🔀 Hybrid AI Search**: Combine AI semantic search with keyword search for optimal results
- **🎯 AI Re-ranking**: Intelligent result refinement using CrossEncoder models for better relevance
- **🔍 AI Query Expansion**: Automatically enhance queries with AI-generated related terms
- **💾 Smart Embedding Cache**: AI-powered caching to avoid recomputing document embeddings
- **⚡ Intelligent Query Cache**: Cache LLM responses for instant repeated queries

---

## 📸 Screenshots

### Customer Portal - Home Page:
![Customer Home](documentation/Screenshot%20-%20Customer%20Portal%20-%20Home.png "Customer Portal Home Page")

### Customer Portal - Chat Interface (Internal Docs Mode):
![Customer Chat - RAG Mode](documentation/Screenshot%20-%20Customer%20Portal%20-%20Chat%20-%20Internal%20Docs.png "Customer Portal Chat - Using Internal Documents")

### Customer Portal - Chat Interface (Only LLM Mode):
![Customer Chat - Direct LLM](documentation/Screenshot%20-%20Customer%20Portal%20-%20Chat%20-%20Only%20LLM.png "Customer Portal Chat - Using Direct LLM")

### Admin Portal - Login Page:
![Admin Login](documentation/Screenshot%20-%20Admin%20Portal%20-%20Login.png "Admin Portal Login Page")

### Admin Portal - Dashboard:
![Admin Dashboard](documentation/Screenshot%20-%20Admin%20Portal%20-%20Home.png "Admin Portal Dashboard")

The Admin Portal provides comprehensive document management and system administration:
- **User Management**: Create, manage, and delete user accounts with role-based access control
- **Document Upload**: Drag-and-drop interface for uploading multiple document formats
- **System Statistics**: Real-time metrics on total documents and chunks in the knowledge base
- **ChromaDB Contents**: Browse and inspect all vector embeddings and document chunks
- **Knowledge Base Management**: Reset and manage the entire knowledge base

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** installed
- **Terminal/Command Prompt** access
- **LLM Provider** (choose one):
  - **Ollama** (local AI - will be installed automatically by install script) - Recommended for privacy
  - **OpenAI API Key** (cloud AI - get from https://platform.openai.com) - Alternative option
- **LibreOffice** (optional, but required for `.doc` and `.ppt` files):
  - **macOS**: `brew install --cask libreoffice`
  - **Linux (Debian/Ubuntu)**: `sudo apt-get install libreoffice`
  - **Linux (RHEL/CentOS)**: `sudo yum install libreoffice`
  - **Windows**: Download from [LibreOffice website](https://www.libreoffice.org/download/)
  
  > **Note**: `.docx`, `.pptx`, and other modern formats work without LibreOffice. Only older formats (`.doc`, `.ppt`) require LibreOffice for conversion.

### Installation

**macOS / Linux:**
```bash
chmod +x scripts/*.sh
bash scripts/install.sh
```
**Windows:**
Command Prompt
```cmd
scripts\install.bat
```
**Windows:**
PowerShell
```powershell
.\scripts\install.ps1
```

The installation script will automatically:
- ✅ Create Python virtual environment
- ✅ Install all AI and ML dependencies
- ✅ Install and configure Ollama (LLM engine)
- ✅ Download default AI model (llama3.2:3b) - your local LLM
- ✅ Create `config/.env` configuration file from `config/env.example` template
- ✅ Initialize AI knowledge base storage directories

### Run the Application

**macOS / Linux:**
```bash
bash scripts/run.sh
```
**Windows:**
Command Prompt
```cmd
scripts\run.bat
```
**Windows:**
PowerShell
```powershell
.\scripts\run.ps1
```


### First-Time Configuration

After installation, edit `config/.env` and set:

1. **`SECRET_KEY`** - Flask secret key (change from default!)
   ```bash
   # Generate a secure key:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

**Default Admin Credentials:**
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change the default admin password immediately after first login through the User Management section in the admin panel.

For all configuration options, see [Configuration Guide](documentation/DEPLOYMENT.md#configuration).

### Access Your AI Dashboard

Once running, access your AI-powered interfaces:

- **🤖 AI Q&A Interface**: http://localhost:5001/customer - Ask questions, get AI answers!
- **📊 AI Admin Panel**: http://localhost:5001/admin - Manage your AI knowledge base
- **🔌 AI REST API**: http://localhost:5001/api - Integrate AI capabilities programmatically

---

## ⚙️ Configuration

### Quick AI Configuration

The system uses `config/.env` for all AI and LLM settings. The install script automatically creates this file from `config/env.example`.

**🔐 Essential Settings:**
- `SECRET_KEY` - Flask secret key for session management (change in production!)
- `PORT` - Server port (default: 5001)
- `HOST` - Server host (default: localhost)

**👥 User Authentication:**
- Default admin user is automatically created on first run
- Default credentials: `admin` / `admin123`
- Change password immediately after first login via User Management section
- All authentication uses username/password (no API keys needed)

**🤖 LLM & AI Settings:**
- `LLM_PROVIDER` - Choose "ollama" (local AI, free, private) or "openai" (cloud AI, powerful, requires API key)
- `OLLAMA_MODEL` - AI model name (default: llama3.2:3b) - supports any Ollama model
- `OPENAI_API_KEY` - Your OpenAI API key (required if using OpenAI provider)
- `USE_LOCAL_EMBEDDINGS` - Use local AI embeddings (True) or OpenAI embeddings (False)

**🧠 RAG & AI Intelligence Settings:**
- `CHUNK_SIZE` - AI document processing chunk size (default: 1000)
- `RETRIEVAL_K` - Number of AI-retrieved chunks per query (default: 3)
- `MIN_SIMILARITY_THRESHOLD` - AI confidence threshold percentage (default: 15.0)

📖 **Full Configuration Guide**: See [documentation/DEPLOYMENT.md](documentation/DEPLOYMENT.md#configuration) for all available options.

---

## 📖 Usage

### Admin Interface - Document Intelligence Hub

1. **🔐 Login**:
   - Go to http://localhost:5001/admin
   - Login with username and password
   - Default credentials: `admin` / `admin123` (change after first login!)

2. **👥 User Management** (First Section):
   - Create new users (Admin or Customer roles)
   - Manage user permissions and roles
   - Reset passwords for any user
   - Delete users (with safety checks)
   - View all users and their activity

3. **🤖 AI Document Upload**: 
   - Drag and drop or browse to upload files
   - AI automatically processes: PDF, CSV, Excel, Text files
   - Watch as AI extracts and indexes your content in real-time

4. **📊 AI Knowledge Management**:
   - View all documents in your AI-powered knowledge base
   - Delete documents from the system
   - Explore ChromaDB vector embeddings (AI-generated)
   - Monitor AI system statistics and performance

### Customer Interface - AI Q&A Experience

1. **💬 Ask Your AI Assistant**:
   - Go to http://localhost:5001/customer
   - Enter your question in natural language (just like talking to ChatGPT!)
   - Get instant AI-powered answers with intelligent source citations
   - View AI-matched document chunks with relevance scores

2. **🔀 Answer Source Toggle**:
   - **📚 Internal Docs Mode** (Default): Uses your uploaded documents for context-aware, accurate answers based on your knowledge base
     - Better context and accuracy
     - Slightly slower due to document retrieval
   - **🤖 Only LLM Mode**: Uses LLM's general knowledge directly without document retrieval
     - Faster responses
     - Generic answers from LLM training data
   - Toggle between modes using the radio buttons above the query input

3. **🎯 Advanced AI Options**:
   - Bypass cache for fresh LLM-generated responses
   - View AI similarity scores and confidence levels
   - Explore source documents used by the AI
   - Experience real-time AI reasoning

### REST API

Full API documentation available at [documentation/API.md](documentation/API.md).

**Quick Example:**
```bash
# Query the system
curl -X POST http://localhost:5001/api/customer/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'

# Login first (get session)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username": "admin", "password": "admin123"}'

# Upload a document (requires admin session)
curl -X POST http://localhost:5001/api/admin/upload \
  -b cookies.txt \
  -F "file=@document.pdf"
```

---

## 📁 Project Structure

```
my-rag/
├── backend/              # Backend API server
│   ├── api/             # API routes (admin, customer)
│   ├── services/        # Business logic (RAG service)
│   └── app.py          # Main Flask application
├── core/                 # Core RAG functionality
│   ├── base_rag.py     # Base RAG class
│   ├── multi_format_rag.py  # Multi-format support
│   ├── settings.py     # Configuration management
│   └── ...             # RAG helpers, caching, ChromaDB
├── frontend/             # Frontend interfaces
│   ├── admin/           # Admin UI (document management)
│   └── customer/        # Customer UI (query interface)
├── config/              # Configuration files
│   └── env.example     # Environment template
├── documentation/        # Documentation files
│   ├── API.md          # REST API documentation
│   ├── CONTRIBUTING.md  # Contribution guidelines
│   ├── DEPLOYMENT.md    # Deployment guide
│   └── SCRIPTS.md      # Scripts documentation
├── scripts/             # Deployment scripts
│   ├── install.*       # Installation scripts (all platforms)
│   └── run.*           # Run scripts (all platforms)
└── storage/             # Data storage (created at runtime)
    ├── documents/       # Uploaded documents
    ├── chroma_db/       # Vector database
    └── embedding_cache/ # Embedding cache
```

---

## 📚 Documentation

- **[documentation/DEPLOYMENT.md](documentation/DEPLOYMENT.md)** - Comprehensive deployment guide
- **[documentation/PRODUCTION.md](documentation/PRODUCTION.md)** - Production deployment guide (Gunicorn, systemd, security)
  - Detailed installation for all platforms
  - Complete configuration reference
  - Production deployment options
  - Troubleshooting guide
  
- **[documentation/API.md](documentation/API.md)** - REST API documentation
  - All endpoints with examples
  - Request/response formats
  - Authentication details

- **[documentation/SCRIPTS.md](documentation/SCRIPTS.md)** - Scripts documentation
  - Installation scripts guide
  - Run scripts guide
  - Storage initialization

---

## 🤝 Contributing

Contributions are welcome! This project follows standard open-source practices:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Code Structure

- **Frontend**: HTML/CSS/JavaScript in `frontend/` directory
- **Backend**: Python Flask application in `backend/` directory
- **Core RAG**: RAG implementation in `core/` directory

For detailed contribution guidelines, see [documentation/CONTRIBUTING.md](documentation/CONTRIBUTING.md).

---

## 🔧 Troubleshooting

### Common Issues

**Python not found?**
- Windows: Reinstall Python with "Add to PATH" option
- macOS: `brew install python@3.11`
- Linux: `sudo apt-get install python3 python3-pip python3-venv`

**Scripts not working?**
- Windows PowerShell: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- macOS/Linux: `chmod +x scripts/*.sh`

**Port already in use?**
- Change `PORT` in `config/.env` to a different port (e.g., 5002)

**Ollama not working?**
- The install script should handle this automatically
- Manual: Install from https://ollama.ai and run `ollama pull llama3.2:3b`

**Documents not loading?**
- Check if documents exist in `storage/documents/`
- Verify ChromaDB is initialized in `storage/chroma_db/`
- Check admin API key is correct

📖 **More Help**: See [documentation/DEPLOYMENT.md](documentation/DEPLOYMENT.md#troubleshooting) for detailed troubleshooting.

---

## 📝 License

This project is open source. See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- 🤖 **AI Framework**: Built with [LangChain](https://www.langchain.com/) for advanced RAG and AI orchestration
- 🧠 **Vector AI Database**: Powered by [ChromaDB](https://www.trychroma.com/) for intelligent vector storage and semantic search
- 💬 **LLM Engine**: Driven by [Ollama](https://ollama.ai/) for local, private Large Language Model processing
- 📝 **AI Rendering**: Frontend enhanced with [Marked.js](https://marked.js.org/) for beautiful AI-generated content display

---
---

<div align="center">

**Mukesh Rajput** · [LinkedIn](https://www.linkedin.com/in/mukesh-rajput/) · [Portfolio](https://msr5464.github.io/)

<sub>Made with ❤️ for the Engineering Team</sub>

</div>

---
---
