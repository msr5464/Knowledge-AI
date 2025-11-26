"""
Admin API Routes
===============
Endpoints for admin operations (document upload, management).
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import tempfile
from backend.api.auth.routes import require_auth

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/upload', methods=['POST'])
@require_auth(admin_only=True)
def upload_document():
    """Upload and process a document."""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    # Save uploaded file temporarily using system temp directory
    filename = secure_filename(file.filename)
    
    # Use Python's tempfile for better cross-platform temp handling
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
        temp_path = Path(temp_file.name)
        try:
            file.save(str(temp_path))
            
            # Get RAG service
            rag_service = current_app.config['RAG_SERVICE']
            
            # Process document
            result = rag_service.upload_document(temp_path, filename)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

@admin_bp.route('/documents', methods=['GET'])
@require_auth(admin_only=True)
def list_documents():
    """List all uploaded documents."""
    rag_service = current_app.config['RAG_SERVICE']
    documents = rag_service.list_documents()
    
    return jsonify({
        'success': True,
        'documents': documents,
        'count': len(documents)
    }), 200

@admin_bp.route('/documents/<doc_id>', methods=['DELETE'])
@require_auth(admin_only=True)
def delete_document(doc_id):
    """Delete a document."""
    rag_service = current_app.config['RAG_SERVICE']
    result = rag_service.delete_document(doc_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404

@admin_bp.route('/documents/<doc_id>/download', methods=['GET'])
@require_auth(admin_only=True)
def download_document(doc_id):
    """Download a document file."""
    from flask import send_file
    rag_service = current_app.config['RAG_SERVICE']
    
    # Find document by ID
    if doc_id not in rag_service.documents:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404
    
    doc_info = rag_service.documents[doc_id]
    file_path = Path(doc_info['path'])
    
    if not file_path.exists():
        return jsonify({
            'success': False,
            'error': 'File not found on disk'
        }), 404
    
    try:
        return send_file(
            str(file_path.absolute()),
            as_attachment=True,
            download_name=doc_info['name']
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/stats', methods=['GET'])
@require_auth(admin_only=True)
def get_stats():
    """Get system statistics."""
    rag_service = current_app.config['RAG_SERVICE']
    stats = rag_service.get_stats()
    
    if stats['success']:
        return jsonify(stats), 200
    else:
        return jsonify(stats), 500

@admin_bp.route('/chromadb', methods=['GET'])
@require_auth(admin_only=True)
def get_chromadb_contents():
    """Get ChromaDB collection contents."""
    rag_service = current_app.config['RAG_SERVICE']
    result = rag_service.get_chromadb_contents()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@admin_bp.route('/chromadb/reset', methods=['POST'])
@require_auth(admin_only=True)
def reset_chromadb():
    """Reset ChromaDB by deleting all collections."""
    rag_service = current_app.config['RAG_SERVICE']
    
    # Get delete_all parameter from request
    data = request.get_json() or {}
    delete_all = data.get('delete_all', True)
    
    result = rag_service.reset_chromadb(delete_all=delete_all)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

