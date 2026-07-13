"""
GAURANGA - Revenue API Server
Flask API untuk tracking pendapatan real-time
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import RevenueDatabase, db
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)

# Initialize database
db = RevenueDatabase()

# ============ SBU ENDPOINTS ============

@app.route('/api/sbu', methods=['GET'])
def get_sbus():
    """Get all SBUs with revenue"""
    try:
        sbus = db.get_all_sbus()
        return jsonify({'success': True, 'data': sbus})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sbu/<name>', methods=['GET'])
def get_sbu(name):
    """Get SBU by name"""
    try:
        sbu = db.get_sbu_by_name(name)
        if sbu:
            return jsonify({'success': True, 'data': sbu})
        return jsonify({'success': False, 'error': 'SBU not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ CLIENT ENDPOINTS ============

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients"""
    try:
        clients = db.get_all_clients()
        return jsonify({'success': True, 'data': clients})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clients', methods=['POST'])
def add_client():
    """Add new client"""
    try:
        data = request.json
        client_id = db.add_client(
            name=data.get('name'),
            company=data.get('company'),
            phone=data.get('phone'),
            email=data.get('email'),
            sbu_id=data.get('sbu_id')
        )
        return jsonify({'success': True, 'client_id': client_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clients/<int:client_id>/status', methods=['PUT'])
def update_client_status(client_id):
    """Update client status"""
    try:
        data = request.json
        db.update_client_status(client_id, data.get('status'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ PROJECT ENDPOINTS ============

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = db.get_all_projects()
        return jsonify({'success': True, 'data': projects})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def add_project():
    """Add new project"""
    try:
        data = request.json
        project_id = db.add_project(
            name=data.get('name'),
            client_id=data.get('client_id'),
            sbu_id=data.get('sbu_id'),
            value=data.get('value', 0),
            status=data.get('status', 'prospect'),
            description=data.get('description')
        )
        return jsonify({'success': True, 'project_id': project_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>/status', methods=['PUT'])
def update_project_status(project_id):
    """Update project status"""
    try:
        data = request.json
        db.update_project_status(project_id, data.get('status'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ TRANSACTION ENDPOINTS ============

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get transactions"""
    try:
        limit = request.args.get('limit', 50, type=int)
        sbu_id = request.args.get('sbu_id', type=int)
        transactions = db.get_transactions(limit=limit, sbu_id=sbu_id)
        return jsonify({'success': True, 'data': transactions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """Add new transaction"""
    try:
        data = request.json
        tx_id = db.add_transaction(
            sbu_id=data.get('sbu_id'),
            type=data.get('type'),
            amount=data.get('amount'),
            description=data.get('description'),
            category=data.get('category'),
            payment_method=data.get('payment_method'),
            date=data.get('date'),
            project_id=data.get('project_id')
        )
        return jsonify({'success': True, 'transaction_id': tx_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ REVENUE SUMMARY ENDPOINTS ============

@app.route('/api/revenue/summary', methods=['GET'])
def get_revenue_summary():
    """Get revenue summary"""
    try:
        summary = db.get_revenue_summary()
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/revenue/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data"""
    try:
        summary = db.get_revenue_summary()
        sbus = db.get_all_sbus()
        recent_transactions = db.get_transactions(limit=10)
        pending_invoices = db.get_invoices(status='pending')
        
        return jsonify({
            'success': True,
            'data': {
                'summary': summary,
                'sbus': sbus,
                'recent_transactions': recent_transactions,
                'pending_invoices': pending_invoices
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ INVOICE ENDPOINTS ============

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    """Get invoices"""
    try:
        status = request.args.get('status')
        invoices = db.get_invoices(status=status)
        return jsonify({'success': True, 'data': invoices})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/invoices', methods=['POST'])
def create_invoice():
    """Create invoice"""
    try:
        data = request.json
        invoice_id = db.create_invoice(
            client_id=data.get('client_id'),
            amount=data.get('amount'),
            sbu_id=data.get('sbu_id'),
            project_id=data.get('project_id'),
            due_days=data.get('due_days', 14)
        )
        return jsonify({'success': True, 'invoice_id': invoice_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/invoices/<int:invoice_id>/pay', methods=['POST'])
def mark_invoice_paid(invoice_id):
    """Mark invoice as paid"""
    try:
        data = request.json
        db.mark_invoice_paid(invoice_id, data.get('payment_method'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ CEO TRANSFER ENDPOINTS ============

@app.route('/api/ceo/transfers', methods=['GET'])
def get_ceo_transfers():
    """Get CEO transfer history"""
    try:
        transfers = db.get_ceo_transfers()
        return jsonify({'success': True, 'data': transfers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ceo/transfer', methods=['POST'])
def add_ceo_transfer():
    """Add CEO Bitcoin transfer"""
    try:
        data = request.json
        result = db.add_ceo_transfer(
            amount_idr=data.get('amount_idr'),
            btc_rate=data.get('btc_rate', 1500000000),
            sbu_source=data.get('sbu_source', 'general'),
            note=data.get('note')
        )
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ QUICK DATA ENDPOINTS ============

@app.route('/api/quick/income', methods=['POST'])
def quick_add_income():
    """Quick add income transaction"""
    try:
        data = request.json
        sbu_name = data.get('sbu', 'general')
        sbu = db.get_sbu_by_name(sbu_name)
        if not sbu:
            sbu = db.get_sbu_by_name('general')
        
        tx_id = db.add_transaction(
            sbu_id=sbu['id'],
            type='income',
            amount=data.get('amount'),
            description=data.get('description', f"Income from {sbu_name}"),
            category=data.get('category', 'project'),
            payment_method=data.get('payment_method', 'BCA')
        )
        return jsonify({'success': True, 'transaction_id': tx_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/quick/expense', methods=['POST'])
def quick_add_expense():
    """Quick add expense transaction"""
    try:
        data = request.json
        sbu_name = data.get('sbu', 'general')
        sbu = db.get_sbu_by_name(sbu_name)
        if not sbu:
            sbu = db.get_sbu_by_name('general')
        
        tx_id = db.add_transaction(
            sbu_id=sbu['id'],
            type='expense',
            amount=data.get('amount'),
            description=data.get('description', f"Expense for {sbu_name}"),
            category=data.get('category', 'operational')
        )
        return jsonify({'success': True, 'transaction_id': tx_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ HEALTH CHECK ============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'GAURANGA Revenue API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def status():
    """Status check"""
    try:
        summary = db.get_revenue_summary()
        return jsonify({
            'status': 'online',
            'service': 'GAURANGA Revenue API',
            'version': '1.0.0',
            'revenue': {
                'total': summary['total_income'],
                'monthly': summary['monthly_income']
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# ============ MAIN ============

if __name__ == '__main__':
    print("🚀 GAURANGA Revenue API Server starting...")
    print("📊 Endpoints available:")
    print("   GET  /api/sbu              - List all SBUs")
    print("   GET  /api/clients          - List all clients")
    print("   GET  /api/projects          - List all projects")
    print("   GET  /api/transactions      - List transactions")
    print("   GET  /api/revenue/summary   - Revenue summary")
    print("   GET  /api/revenue/dashboard - Dashboard data")
    print("   GET  /api/invoices          - List invoices")
    print("   GET  /api/ceo/transfers     - CEO transfer history")
    print("   POST /api/quick/income      - Quick add income")
    print("   POST /api/quick/expense     - Quick add expense")
    print("\n🌐 Server running on http://0.0.0.0:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
