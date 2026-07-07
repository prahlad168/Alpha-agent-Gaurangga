"""
GAURANGA - ChatGPT Integration Server
Handles API calls to OpenAI with secure key storage
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import traceback

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client with API key from environment
client = None

def init_openai():
    global client
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
    else:
        print("⚠️ OPENAI_API_KEY not set")

@app.route('/api/chat', methods=['POST'])
def chat():
    """Proxy endpoint for ChatGPT queries"""
    try:
        data = request.json
        message = data.get('message', '')
        system_context = data.get('context', '')
        
        if not client:
            return jsonify({
                'error': 'OpenAI not configured',
                'message': 'API key not set'
            }), 500
        
        # Build messages
        messages = []
        
        # System prompt with GAURANGA context
        if system_context:
            messages.append({
                "role": "system", 
                "content": system_context
            })
        else:
            messages.append({
                "role": "system", 
                "content": """Kamu adalah ALPHA GAURANGGA, Executive AI Assistant untuk I Made Purna Ananda (Pak Pur), CEO Maha Lakshmi Corp.

Karakteristikmu:
- Berbahasa Indonesia natural
- Ramah, profesional, penuh semangat
- Loyal kepada Pak Pur
- Familiar dengan keluarga: Bunda Lila, Putu Gaurangga, Kadek Srutakirti
- Familiar dengan bisnis: Maha Lakshmi Corp, 10 SBUs

Prinsip:
1. Documentation before Code
2. Security before Features  
3. Human Oversight
4. Continuous Improvement

Selalu jawab dengan hangat dan membantu. Gunakan emoji secukupnya."""
            })
        
        messages.append({"role": "user", "content": message})
        
        # Call ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and affordable
            messages=messages,
            max_tokens=1000,
            temperature=0.8
        )
        
        reply = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'reply': reply,
            'model': 'gpt-4o-mini'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Check if OpenAI is configured"""
    return jsonify({
        'status': 'online',
        'openai_configured': client is not None,
        'model': 'gpt-4o-mini'
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    init_openai()
    print("🚀 GAURANGA Server starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
