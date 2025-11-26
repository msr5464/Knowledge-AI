"""
Customer API Routes
==================
Endpoints for customer operations (querying RAG system).
"""

from flask import Blueprint, request, jsonify, current_app

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/query', methods=['POST'])
def query():
    """Query the RAG system."""
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({
            'success': False,
            'error': 'Question is required'
        }), 400
    
    question = data['question']
    session_id = data.get('session_id')
    bypass_cache = data.get('bypass_cache', False)  # Default to False if not provided
    use_rag = data.get('use_rag', True)  # Default to True (use RAG with documents)
    
    if not question or not question.strip():
        return jsonify({
            'success': False,
            'error': 'Question cannot be empty'
        }), 400
    
    # Get RAG service
    rag_service = current_app.config['RAG_SERVICE']
    
    # Process query
    result = rag_service.query(question, session_id, bypass_cache=bypass_cache, use_rag=use_rag)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@customer_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'rag-customer-api'
    }), 200

