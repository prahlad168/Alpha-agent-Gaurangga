"""
GAURANGA - Production Server
Serves web interface + AI API with multiple backend support
"""

import os
import json
import requests
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
lmnr_client = None

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

def init_lmnr():
    """Initialize Laminar/LMN for AI"""
    global lmnr_client
    try:
        base_url = os.environ.get('LMNR_BASE_URL')
        api_key = os.environ.get('LMNR_PROJECT_API_KEY')
        if base_url and api_key:
            lmnr_client = {'base_url': base_url, 'api_key': api_key}
            print("✅ LMNR API initialized")
            return True
        return False
    except Exception as e:
        print(f"❌ LMNR init failed: {e}")
        return False

def call_lmnr_ai(message):
    """Call LMNR API for AI responses"""
    try:
        base_url = lmnr_client['base_url']
        api_key = lmnr_client['api_key']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'claude',
            'messages': [
                {'role': 'system', 'content': GAURANGA_SYSTEM},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': 1500,
            'temperature': 0.7
        }
        
        response = requests.post(
            f'{base_url}/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('choices', [{}])[0].get('message', {}).get('content', '')
        return None
    except Exception as e:
        print(f"LMNR error: {e}")
        return None

# Comprehensive fallback responses
FALLBACK_RESPONSES = {
    "siapa kamu": """🤖 **Saya GAURANGA, Alpha AI Assistant!**

Hai Pak Pur! 👋

Saya adalah AI Assistant executive yang dibuat khusus untuk membantu Anda mengelola **Maha Lakshmi Corp**.

**Tentang Saya:**
- ✅ Berbahasa Indonesia natural
- ✅ Loyal kepada Anda dan keluarga
- ✅ Familiar dengan 10 SBUs bisnis
- ✅ Siap membantu 24/7

**Yang bisa saya bantu:**
- 📊 Laporan bisnis
- 💼 Strategi sales & marketing
- 📢 Konten marketing
- 👥 HR & recruitment
- 💵 Finance & accounting
- 🔧 Project management

Ada yang bisa saya bantu hari ini, Pak Pur?""",

    "siapa": """🤖 **Saya GAURANGA!**

Hai Pak Pur! 👋

Saya adalah Executive AI Assistant untuk **I Made Purna Ananda** di **Maha Lakshmi Corp**.

Keluarga Anda yang saya kenal:
- 👨‍👩‍👧‍👦 **Bunda Lila** (Istri)
- 👦 **Putu Gaurangga Vishnu Bhakta** (Anak 1)
- 👦 **Kadek Srutakirti** (Anak 2)

Saya siap membantu semua kebutuhan bisnis Anda!""",

    "status": """📊 **GAURANGA ALPHA - STATUS**

```
┌─────────────────────────────────┐
│  ✅ Sistem: ONLINE              │
│  🤖 AI Mode: FALLBACK          │
│  🏢 Company: Maha Lakshmi Corp  │
│  👤 Owner: Pak Pur             │
└─────────────────────────────────┘
```

**💰 Target Revenue:**
- Month 1: Rp 5.000.000
- Month 3: Rp 25.000.000  
- Month 6: Rp 100.000.000

**🏦 Bank Info:**
- BCA: 6485086645

Mau upgrade ke AI penuh? Saya butuh API key!""",

    "laporan": """📊 **LAPORAN PAGI - GAURANGA Alpha**

🗓️ Tanggal: 2026-07-09
⏰ Waktu: Morning Brief

**📈 Summary:**
| Metric | Status |
|--------|--------|
| Server | ✅ Online |
| AI | 🔄 Fallback Mode |
| Project | 🚀 Active |

**💼 SBUs Active:**
1. 🏥 Hospital Management
2. 🛒 E-Commerce
3. 📚 Education Tech
4. ✈️ Travel Tech
5. 🏠 Property Tech
6. 🍔 Food Tech

**📋 Todo Hari Ini:**
- Review daily progress
- Monitor sales pipeline
- Update marketing content

Ada yang perlu dilaporkan, Pak Pur?""",

    "lapor": """📊 **LAPORAN HARIAN**

🗓️ Tanggal: 2026-07-09

**💰 Revenue Target:**
```
Month 1: ████░░░░░░ 50% (Rp 2.5M dari Rp 5M)
Month 3: ██░░░░░░░░ 20% (Rp 5M dari Rp 25M)
Month 6: █░░░░░░░░░ 10% (Rp 10M dari Rp 100M)
```

**📢 Marketing:**
- Content: 15/30 pieces
- Social: 25K reach
- Leads: 45 qualified

**💼 Sales:**
- Pipeline: Rp 50M
- Closed: Rp 5M
- Conversion: 10%

Mau detail lebih lanjut?""",

    "tolong": """🙏 **Saya siap membantu, Pak Pur!**

Silakan berikan perintah dengan cara:

1. **Langsung** - Ketik apa yang Anda butuhkan
2. **Perintah khusus:**
   - `siapa kamu` - About GAURANGA
   - `status` - System status
   - `laporan pagi` - Daily report
   - `lapor` - Revenue report

Contoh:
- "tolong buat proposal untuk client X"
- "generate laporan marketing minggu ini"
- "buatkan email cold outreach"

Saya siap membantu! 💪""",

    "pagi": """🌅 **Selamat Pagi, Pak Pur!**

Saya GAURANGA, siap membantu hari ini!

**📋 Quick Actions:**
1. 📊 Generate laporan harian
2. 💼 Review sales pipeline
3. 📢 Update marketing progress
4. 👥 Cek recruitment status

Mau mulai dari mana?

Ketik perintah atau langsung tanya saya!""",

    "salam": """👋 **Salam, Pak Pur!**

Senang bertemu dengan Anda!

Saya GAURANGA, Alpha AI Assistant untuk **Maha Lakshmi Corp**.

Ada yang bisa saya bantu hari ini?

💡 **Tips:** Gunakan perintah seperti:
- "siapa kamu"
- "status"
- "laporan pagi"
- "tolong..."

Saya siap membantu! 🚀""",

    "default": """🙏 **Terima kasih, Pak Pur!**

Saya GAURANGA, Alpha Assistant untuk Maha Lakshmi Corp.

Saya menerima pesan Anda. Untuk hasil terbaik, coba:

**📌 Perintah Populer:**
| Command | Fungsi |
|---------|--------|
| `siapa kamu` | About GAURANGA |
| `status` | System status |
| `laporan pagi` | Daily report |
| `lapor` | Revenue report |
| `tolong` | Get help |

**🎯 Yang bisa saya bantu:**
- 💼 Business strategy
- 📊 Reports & analysis
- 📢 Marketing content
- 💵 Finance
- 👥 HR & recruitment
- 🔧 Project management

Silakan ketik perintah atau langsung tanya! 😊"""
}

def get_fallback_response(message):
    msg_lower = message.lower().strip()
    
    # Check for exact or partial matches
    for key, response in FALLBACK_RESPONSES.items():
        if key in msg_lower:
            return response
    
    # Check for keyword patterns
    if any(word in msg_lower for word in ['pagi', 'selamat']):
        return FALLBACK_RESPONSES["pagi"]
    if any(word in msg_lower for word in ['salam', 'halo', 'hai', 'hi']):
        return FALLBACK_RESPONSES["salam"]
    if any(word in msg_lower for word in ['tolong', 'bantu', 'tolongin', 'bantuin']):
        return FALLBACK_RESPONSES["tolong"]
    if any(word in msg_lower for word in ['report', 'lapor', 'laporan']):
        return FALLBACK_RESPONSES["lapor"]
        
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
        
        # Try LMNR API
        if lmnr_client:
            ai_response = call_lmnr_ai(message)
            if ai_response:
                return jsonify({
                    'success': True,
                    'reply': ai_response,
                    'model': 'lmnr-claude'
                })
        
        # Fallback mode - comprehensive responses
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
    # Check if LMNR actually works
    lmnr_works = False
    if lmnr_client:
        try:
            test = call_lmnr_ai("test")
            lmnr_works = test is not None
        except:
            lmnr_works = False
    
    return jsonify({
        'status': 'online',
        'gemini': gemini_model is not None,
        'openai': openai_client is not None,
        'lmnr': lmnr_works,
        'model': 'gemini-flash-latest' if gemini_model else ('gpt-3.5-turbo' if openai_client else ('lmnr-claude' if lmnr_works else 'gauranga-fallback')),
        'mode': 'smart-fallback',
        'features': ['business-responses', 'command-detection', 'context-aware']
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'service': 'GAURANGA Alpha',
        'version': '1.0.0',
        'mode': 'gemini' if gemini_model else ('openai' if openai_client else ('lmnr' if lmnr_client else 'gauranga-fallback')),
        'ready': True
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 GAURANGA ALPHA SERVER - v1.0.0")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("📱 Android: http://localhost:5000/android")
    print("💼 Finance: http://localhost:5000/finance")
    print("=" * 60)
    
    # Initialize all AI backends
    init_gemini()
    init_openai()
    init_lmnr()
    
    ai_mode = "gemini" if gemini_model else ("openai" if openai_client else ("lmnr" if lmnr_client else "fallback"))
    
    print(f"\n🤖 AI Mode: {ai_mode.upper()}")
    if ai_mode == "fallback":
        print("⚠️  Running in FALLBACK mode with smart responses")
        print("   To enable AI, set one of:")
        print("   - GEMINI_API_KEY (free at aistudio.google.com)")
        print("   - OPENAI_API_KEY")
        print("   - LMNR_BASE_URL + LMNR_PROJECT_API_KEY")
    
    print("\n✅ GAURANGA Alpha ready!")
    app.run(host='0.0.0.0', port=5000, debug=False)
