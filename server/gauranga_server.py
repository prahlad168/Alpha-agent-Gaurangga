"""
GAURANGA - AI Integration Server
Supports Gemini (FREE) and OpenAI (paid)
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

# AI Clients
gemini_model = None
openai_client = None

# System prompt for GAURANGA
GAURANGA_SYSTEM = """Kamu adalah ALPHA GAURANGGA, Executive AI Assistant untuk I Made Purna Ananda (Pak Pur), CEO Maha Lakshmi Corp.

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

def init_gemini():
    global gemini_model
    try:
        from google import genai
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            client = genai.Client(api_key=api_key)
            gemini_model = client
            print("✅ Gemini initialized (FREE tier)")
            return True
        print("⚠️ GEMINI_API_KEY not set")
        return False
    except Exception as e:
        print(f"❌ Gemini init failed: {e}")
        return False

def init_openai():
    global openai_client
    try:
        from openai import OpenAI
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            openai_client = OpenAI(api_key=api_key)
            print("✅ OpenAI initialized")
            return True
        return False
    except Exception as e:
        print(f"❌ OpenAI init failed: {e}")
        return False

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        # Try Gemini first (free)
        if gemini_model:
            try:
                response = gemini_model.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=f"{GAURANGA_SYSTEM}\n\nUser: {message}"
                )
                return jsonify({'success': True, 'reply': response.text, 'model': 'gemini-2.0-flash'})
            except Exception as e:
                print(f"Gemini error: {e}")
        
        # Fallback to OpenAI
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": GAURANGA_SYSTEM},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=1000
                )
                return jsonify({
                    'success': True,
                    'reply': response.choices[0].message.content,
                    'model': 'gpt-3.5-turbo'
                })
            except Exception as e:
                return jsonify({'error': f'OpenAI error: {str(e)}'}), 500
        
        return jsonify({'error': 'No AI service configured'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'gemini': gemini_model is not None,
        'openai': openai_client is not None,
        'model': 'gemini-1.5-flash' if gemini_model else 'gpt-3.5-turbo'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("🚀 GAURANGA Server starting...")
    init_gemini()
    init_openai()
    if not gemini_model and not openai_client:
        print("⚠️ No AI service available!")
    print("🚀 Server running on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
