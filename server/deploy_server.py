"""
GAURANGA - Production Server
Serves web interface + AI API
"""

import os
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

# System prompt for GAURANGA
GAURANGA_SYSTEM = """Kamu adalah ALPHA GAURANGGA, Executive AI Assistant untuk I Made Purna Ananda (Pak Pur), CEO Maha Lakshmi Corp.

Karakteristikmu:
- Berbahasa Indonesia natural
- Ramah, profesional, penuh semangat
- Loyal kepada Pak Pur
- Familiar dengan keluarga: Bunda Lila, Putu Gaurangga, Kadek Srutakirti
- Familiar dengan bisnis: Maha Lakshmi Corp, 10 SBUs (Hospital, E-Commerce, Education, Travel, Property, Food)

Prinsip:
1. Documentation before Code
2. Security before Features  
3. Human Oversight
4. Continuous Improvement

Selalu jawab dengan hangat dan membantu. Gunakan emoji secukupnya."""

# AI Clients
gemini_model = None
openai_client = None

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
        print("⚠️ GEMINI_API_KEY not set - AI will use fallback mode")
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

# Fallback responses when no AI is configured
FALLBACK_RESPONSES = {
    "sapa": "Halo Pak Pur! 👋 GAURANGA Alpha siap membantu! Ada yang bisa saya kerjakan hari ini?",
    "siapa": "Saya GAURANGA, Executive AI Assistant untuk Pak Pur di Maha Lakshmi Corp. Saya siap membantu dengan semua kebutuhan bisnis! 🤖",
    "status": "✅ GAURANGA Alpha Online!\n\n📊 Sistem: Aktif\n🤖 AI: Fallback Mode (butuh GEMINI_API_KEY)\n🏢 Company: Maha Lakshmi Corp\n👤 Owner: I Made Purna Ananda",
    "laporan": "📊 LAPORAN PAGI - GAURANGA Alpha\n\n🗓️ Tanggal: Loading...\n📁 Project: Alpha-agent-Gaurangga\n🎯 Status: ACTIVE\n\n💰 Target Revenue:\n- Month 1: Rp 5.000.000\n- Month 3: Rp 25.000.000\n- Month 6: Rp 100.000.000",
    "default": "Terima kasih Pak Pur! 🙏\n\nSaya GAURANGA, Alpha Assistant untuk Maha Lakshmi Corp.\n\nUntuk mengaktifkan AI penuh, butuh:\n1. GEMINI_API_KEY (gratis di aistudio.google.com)\n\nNamun saya tetap bisa membantu dengan perintah dasar!\n\nCoba: 'siapa kamu', 'status', atau 'laporan pagi'"
}

def get_fallback_response(message):
    msg_lower = message.lower()
    for key, response in FALLBACK_RESPONSES.items():
        if key in msg_lower:
            return response
    return FALLBACK_RESPONSES["default"]

@app.route('/')
def index():
    return send_file('../index.html')

@app.route('/finance')
def finance():
    return send_file('../finance/index.html')

@app.route('/android')
def android():
    return send_file('../android-app/index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        # Try Gemini first (free)
        if gemini_model:
            try:
                response = gemini_model.models.generate_content(
                    model='gemini-flash-latest',
                    contents=f"{GAURANGA_SYSTEM}\n\nUser: {message}"
                )
                return jsonify({'success': True, 'reply': response.text, 'model': 'gemini-flash-latest'})
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
        
        # Fallback mode - simple responses
        fallback = get_fallback_response(message)
        return jsonify({
            'success': True, 
            'reply': fallback, 
            'model': 'fallback'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'gemini': gemini_model is not None,
        'openai': openai_client is not None,
        'model': 'gemini-1.5-flash' if gemini_model else ('gpt-3.5-turbo' if openai_client else 'fallback')
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'GAURANGA Alpha'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 GAURANGA ALPHA SERVER")
    print("=" * 50)
    print("📍 URL: http://localhost:5000")
    print("📱 Android: http://localhost:5000/android")
    print("💼 Finance: http://localhost:5000/finance")
    print("=" * 50)
    
    init_gemini()
    init_openai()
    
    if not gemini_model and not openai_client:
        print("⚠️ No AI configured - Running in FALLBACK mode")
        print("   To enable AI, set GEMINI_API_KEY environment variable")
    
    print("\n✅ GAURANGA Alpha ready!")
    app.run(host='0.0.0.0', port=5000, debug=False)
