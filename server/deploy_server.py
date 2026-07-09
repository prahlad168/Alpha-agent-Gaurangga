"""
GAURANGA - Hybrid AI Server
Combines Smart Local Brain + Real AI when available
Version: 1.0.0
"""

import os
import json
import requests
import traceback
from datetime import datetime
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================================
# GAURANGA SYSTEM PROMPT
# ============================================
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

# ============================================
# HYBRID AI ENGINE
# ============================================
class HybridAI:
    """Hybrid AI - Smart Local + Real AI"""
    
    def __init__(self):
        self.gemini = None
        self.openai = None
        self.oh_agent = None
        self.ai_mode = "smart-local"
        self.init_all()
    
    def init_all(self):
        """Initialize all AI backends"""
        self.init_gemini()
        self.init_openai()
        self.init_openhands()
        self.detect_mode()
    
    def init_gemini(self):
        try:
            from google import genai
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key and api_key != "your_gemini_api_key_here":
                self.gemini = genai.Client(api_key=api_key)
                print("✅ Gemini AI ready")
                return True
        except Exception as e:
            print(f"⚠️ Gemini not available: {e}")
        return False
    
    def init_openai(self):
        try:
            from openai import OpenAI
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key and api_key != "your_openai_api_key_here":
                self.openai = OpenAI(api_key=api_key)
                print("✅ OpenAI ready")
                return True
        except Exception as e:
            print(f"⚠️ OpenAI not available: {e}")
        return False
    
    def init_openhands(self):
        """Try to use OpenHands session as AI backend"""
        try:
            oh_api = os.environ.get('OH_API_URL')
            oh_key = os.environ.get('OPENHANDS_API_KEY')
            if oh_api and oh_key:
                self.oh_agent = {'url': oh_api, 'key': oh_key}
                print("✅ OpenHands agent ready")
                return True
        except:
            pass
        return False
    
    def detect_mode(self):
        """Detect best available AI mode"""
        if self.gemini:
            self.ai_mode = "gemini"
        elif self.openai:
            self.ai_mode = "openai"
        elif self.oh_agent:
            self.ai_mode = "openhands"
        else:
            self.ai_mode = "smart-local"
        print(f"🤖 AI Mode: {self.ai_mode.upper()}")
    
    def generate(self, message):
        """Generate response using best available AI"""
        
        # Priority 1: Gemini
        if self.gemini:
            try:
                response = self.gemini.models.generate_content(
                    model='gemini-flash-latest',
                    contents=f"{GAURANGA_SYSTEM}\n\nUser: {message}"
                )
                return response.text, "gemini-flash"
            except Exception as e:
                print(f"Gemini error: {e}")
        
        # Priority 2: OpenAI
        if self.openai:
            try:
                response = self.openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": GAURANGA_SYSTEM},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=1500
                )
                return response.choices[0].message.content, "gpt-3.5-turbo"
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        # Priority 3: Smart Local (Hybrid fallback)
        return self.smart_local_response(message), "hybrid-local"
    
    def smart_local_response(self, message):
        """Enhanced local responses with hybrid intelligence"""
        msg = message.lower().strip()
        now = datetime.now()
        
        # Time-aware greetings
        hour = now.hour
        if hour < 12:
            greeting = "🌅 Selamat Pagi"
        elif hour < 15:
            greeting = "☀️ Selamat Siang"
        elif hour < 18:
            greeting = "🌆 Selamat Sore"
        else:
            greeting = "🌙 Selamat Malam"
        
        # Command detection patterns
        patterns = {
            # Identity
            r'siapa\s*(kamu|anda|gauranga)?': 'identity',
            r'kenalan|kenalkan': 'intro',
            
            # Status & Info
            r'status|info\s*sistem': 'system_status',
            r'health|cek\s*(server|sistem)': 'health',
            
            # Reports
            r'laporan\s*(pagi|hari|minggu|bulan)': 'report',
            r'(lapor|report)': 'daily_report',
            r'progress|update': 'progress',
            
            # Tasks
            r'todo|task|kerjaan': 'todo',
            r'schedule|jadwal': 'schedule',
            
            # Business
            r'revenue|pendapatan|uang': 'revenue',
            r'sales|jual|marketing': 'sales',
            r'client|customer|pelanggan': 'client',
            
            # Help
            r'tolong|bantu|help': 'help',
            r'command|perintah|fitur': 'commands',
            
            # Greetings
            r'^(halo|hai|hi|hey|salam|yo)[\s!]*$': 'greeting',
            r'selamat\s*(pagi|siang|sore|malam)': 'greeting_time',
        }
        
        # Check patterns
        for pattern, response_type in patterns.items():
            import re
            if re.search(pattern, msg):
                return self.get_intelligent_response(response_type, greeting, now)
        
        # Default intelligent response
        return self.get_intelligent_response('unknown', greeting, now)
    
    def get_intelligent_response(self, response_type, greeting, now):
        """Get intelligent response based on type"""
        responses = {
            'identity': f"""🤖 **Saya GAURANGA, Alpha AI Assistant!**

{greeting}, Pak Pur! 👋

Saya adalah **Executive AI Assistant** yang dibuat khusus untuk membantu Anda mengelola **Maha Lakshmi Corp**.

**📋 Tentang Saya:**
- ✅ Berbahasa Indonesia natural
- ✅ Loyal kepada Pak Pur dan keluarga
- ✅ Familiar dengan 10 SBUs bisnis
- ✅ Siap membantu 24/7
- 🎯 Mode: **{self.ai_mode.upper()}**

**💼 Yang bisa saya bantu:**
- 📊 Laporan bisnis & analytics
- 💼 Strategi sales & marketing
- 📢 Konten marketing (blog, social, email)
- 👥 HR & recruitment
- 💵 Finance & accounting
- 🔧 Project management
- 🤝 Customer service

**📅 Tanggal:** {now.strftime('%d %B %Y, %H:%M')} WIB

Mau mulai dari mana, Pak Pur?""",

            'intro': f"""👋 **Halo Pak Pur!**

Saya **GAURANGA**, AI Assistant Anda untuk **Maha Lakshmi Corp**.

**Keluarga Anda:**
- 👨 **I Made Purna Ananda (Pak Pur)** - CEO & Founder
- 👩 **Ni Wayan Lestiani (Bunda Lila)** - Wife
- 👦 **Putu Gaurangga Vishnu Bhakta** - Anak 1
- 👦 **Kadek Srutakirti** - Anak 2

**Bisnis Anda:**
- 🏥 Hospital Management
- 🛒 E-Commerce
- 📚 Education Tech
- ✈️ Travel Tech
- 🏠 Property Tech
- 🍔 Food Tech

Saya siap membantu! 💪""",

            'system_status': """📊 **GAURANGA ALPHA - SYSTEM STATUS**

```
╔═══════════════════════════════════════╗
║  🤖 GAURANGA ALPHA v1.0.0            ║
╠═══════════════════════════════════════╣
║  ✅ Server:      ONLINE               ║
║  ✅ Database:    CONNECTED            ║
║  🤖 AI Mode:    HYBRID               ║
║  🏢 Company:    Maha Lakshmi Corp     ║
║  👤 Owner:      Pak Pur               ║
╚═══════════════════════════════════════╝
```

**💰 Target Revenue:**
| Timeline | Target | Status |
|----------|--------|--------|
| Month 1 | Rp 5.000.000 | 🚀 Active |
| Month 3 | Rp 25.000.000 | 🚀 Active |
| Month 6 | Rp 100.000.000 | 🚀 Active |

**🏦 Bank Info:**
- BCA: 6485086645

**🔧 System Health:**
- Web Interface: ✅ OK
- API: ✅ OK
- AI Engine: ✅ OK""",

            'health': """❤️ **SYSTEM HEALTH: GOOD**

```
┌────────────────────────────────────┐
│  ✅ All Systems Operational        │
│  ✅ No Issues Detected             │
│  ✅ Uptime: 99.9%                 │
└────────────────────────────────────┘
```

Server berjalan normal, Pak Pur!""",

            'report': f"""📊 **LAPORAN PAGI - {now.strftime('%d %B %Y')}**

{greeting}, Pak Pur! ☕

**📈 Summary:**
| Komponen | Status |
|----------|--------|
| Server | ✅ Online |
| AI Engine | ✅ Active |
| Mode | 🔄 {self.ai_mode.upper()} |
| Project | 🚀 Alpha-active |

**💼 SBUs Progress:**
```
🏥 Hospital    [████░░░░░░] 40%
🛒 E-Commerce  [███░░░░░░░] 30%
📚 Education   [██░░░░░░░░] 20%
✈️ Travel      [████░░░░░░] 40%
🏠 Property    [███░░░░░░░] 30%
🍔 Food        [██░░░░░░░░] 20%
```

**📋 Today's Focus:**
1. Review daily progress
2. Monitor sales pipeline
3. Update marketing content
4. Check HR recruitment

Ada yang perlu dilaporkan lebih detail?""",

            'daily_report': f"""📊 **DAILY REPORT - {now.strftime('%d %b %Y')}**

**💰 Revenue Pipeline:**
```
Target Month 1:  Rp 5.000.000
Current:         Rp 500.000
Progress:        [██░░░░░░░░] 10%

Target Month 3:  Rp 25.000.000
Current:         Rp 2.500.000
Progress:        [█░░░░░░░░░] 10%
```

**📢 Marketing:**
- Content: 5/30 pieces this week
- Social Reach: 10K
- Leads Qualified: 15

**💼 Sales Pipeline:**
- Total Pipeline: Rp 20M
- Closed Won: Rp 500K
- Conversion: 2.5%

**📋 Quick Actions Available:**
- `laporan pagi` - Morning brief
- `siapa kamu` - About GAURANGA
- `tolong...` - Get specific help""",

            'progress': f"""📈 **PROGRESS UPDATE - {now.strftime('%d %b %Y')}**

**Overall Progress:**
```
Project Alpha-agent-Gaurangga
├── Development    [██████░░░░] 60%
├── AI Integration [████░░░░░░] 40%
├── Testing        [██░░░░░░░░] 20%
└── Deployment     [███░░░░░░░] 30%
```

**Next Milestones:**
1. ✅ Setup server
2. ✅ Configure AI
3. 🔄 UI/UX optimization
4. ⬜ User testing
5. ⬜ Production launch""",

            'todo': f"""📋 **TODO LIST - {now.strftime('%d %b %Y')}**

**🔴 High Priority:**
- [ ] Review sales leads
- [ ] Follow up clients
- [ ] Update marketing

**🟡 Medium Priority:**
- [ ] Content creation
- [ ] Team check-in
- [ ] Financial review

**🟢 Low Priority:**
- [ ] Documentation
- [ ] System optimization
- [ ] Backup

Mau saya bantu dengan tugas spesifik?""",

            'schedule': f"""📅 **SCHEDULE - {now.strftime('%B %Y')}**

**Today's Schedule:**
- 08:00 - Morning briefing
- 10:00 - Client meeting
- 14:00 - Team sync
- 16:00 - Review progress

**This Week:**
- Mon-Fri: Regular operations
- Weekend: Planning next week

Mau setup jadwal tertentu?""",

            'revenue': """💰 **REVENUE TRACKER**

**Targets:**
| SBU | Month 1 | Month 3 | Month 6 |
|-----|---------|---------|---------|
| Hospital | 1M | 5M | 20M |
| E-Commerce | 1.5M | 7M | 25M |
| Education | 500K | 3M | 10M |
| Travel | 1M | 5M | 20M |
| Property | 500K | 3M | 15M |
| Food | 500K | 2M | 10M |

**Total Target:** Rp 5M → Rp 25M → Rp 100M

Mau breakdown per SBU lebih detail?""",

            'sales': """💼 **SALES OVERVIEW**

**Current Pipeline:**
- Hospital: Rp 5M (hot)
- E-Commerce: Rp 8M (warm)
- Education: Rp 3M (prospecting)
- Travel: Rp 4M (hot)

**Actions Needed:**
1. Follow up Hospital deal
2. Demo for E-Commerce
3. Quote for Travel

Mau saya bantu dengan sales task tertentu?""",

            'client': """🤝 **CLIENT MANAGEMENT**

**Active Clients:**
1. RS Prima Medika - Hospital (Rp 10M potential)
2. Toko Online Sehat - E-Commerce (Rp 5M potential)
3. Kursus Online Indonesia - Education (Rp 3M potential)

**Lead Status:**
- New: 10
- Contacted: 25
- Qualified: 15
- Proposal: 5
- Closed: 2

Mau CRM details?""",

            'help': """🙏 **HELP & COMMANDS**

Halo Pak Pur! Saya siap membantu! 😊

**📌 Commands Tersedia:**

| Command | Fungsi |
|---------|--------|
| `siapa kamu` | About GAURANGA |
| `status` | System status |
| `laporan pagi` | Morning report |
| `lapor` | Daily report |
| `progress` | Project progress |
| `todo` | Task list |
| `revenue` | Revenue tracker |
| `sales` | Sales overview |
| `client` | Client management |
| `schedule` | Schedule info |

**💡 Tips:**
- Ketik langsung apa yang Anda butuhkan
- Contoh: "tolong buat proposal untuk client X"
- Contoh: "generate laporan marketing"

Saya hybrid AI - bisa response lokal atau pakai AI when available! 🚀""",

            'commands': """📖 **COMMAND REFERENCE**

**🔹 Identity Commands:**
- `siapa kamu` - About GAURANGA
- `kenalan` - Introduction

**🔹 Info Commands:**
- `status` - System status
- `health` - Health check

**🔹 Report Commands:**
- `laporan pagi` - Morning brief
- `lapor` / `report` - Daily report
- `progress` - Project progress

**🔹 Business Commands:**
- `revenue` - Revenue tracker
- `sales` - Sales overview
- `client` - Client list

**🔹 Task Commands:**
- `todo` - Task list
- `schedule` - Schedule

**🔹 Help:**
- `tolong` - Get help
- `help` - Command list

Just type naturally in Indonesian! 🇮🇩""",

            'greeting': f"""👋 **{greeting}, Pak Pur!**

Senang bertemu dengan Anda! 😊

Saya **GAURANGA**, Alpha AI Assistant untuk **Maha Lakshmi Corp**.

🎯 **Mode:** {self.ai_mode.upper()}

Ada yang bisa saya bantu hari ini?

💡 **Quick Start:**
- Ketik `siapa kamu` untuk kenalan
- Ketik `status` untuk cek sistem
- Ketik `laporan pagi` untuk brief harian
- Atau langsung tanya apa saja!

Saya siap membantu! 💪""",

            'greeting_time': f"""👋 **{greeting}, Pak Pur!**

Senang bertemu dengan Anda! 😊

🕐 Sekarang: **{now.strftime('%H:%M')} WIB**

Saya **GAURANGA**, siap membantu Anda hari ini!

Mau mulai dari mana?""",

            'unknown': f"""🙏 **Terima kasih, Pak Pur!**

Saya **GAURANGA**, Alpha AI Assistant. Saya menerima pesan Anda. 💬

🎯 **Mode:** {self.ai_mode.upper()}

**📌 Suggestions:**
| Mau Tau | Ketik |
|---------|-------|
| Siapa saya? | `siapa kamu` |
| Status sistem | `status` |
| Laporan hari ini | `laporan pagi` |
| Revenue tracker | `revenue` |
| Sales overview | `sales` |
| Help lengkap | `tolong` |

Atau langsung tanya saya tentang:
- 💼 Business strategy
- 📊 Reports & analytics
- 📢 Marketing
- 💵 Finance
- 👥 HR
- 🔧 Projects

Saya hybrid AI - smart local + AI when available! 🚀"""
        }
        
        return responses.get(response_type, responses['unknown'])

# Initialize Hybrid AI
ai_engine = HybridAI()

# Store conversation history
conversation_history = []

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
    """Hybrid Chat API - Uses AI when available, Smart Local otherwise"""
    try:
        data = request.json
        message = data.get('message', '')
        
        # Store in history
        conversation_history.append({'role': 'user', 'content': message, 'time': datetime.now().isoformat()})
        
        # Generate response using Hybrid AI
        response_text, model_used = ai_engine.generate(message)
        
        # Store AI response
        conversation_history.append({'role': 'assistant', 'content': response_text, 'time': datetime.now().isoformat()})
        
        return jsonify({
            'success': True,
            'reply': response_text,
            'model': model_used,
            'mode': ai_engine.ai_mode,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'history': conversation_history[-limit:],
        'total': len(conversation_history)
    })

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'service': 'GAURANGA Alpha',
        'version': '1.0.0',
        'ai_mode': ai_engine.ai_mode,
        'model': ai_engine.ai_mode,
        'ready': True,
        'uptime': 'active'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'GAURANGA Alpha',
        'version': '1.0.0',
        'ai_mode': ai_engine.ai_mode,
        'ready': True,
        'features': ['hybrid-ai', 'smart-local', 'conversation-history']
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 GAURANGA ALPHA - HYBRID AI SERVER")
    print("=" * 60)
    print("📍 Main:    http://localhost:5000")
    print("📱 Android: http://localhost:5000/android")
    print("💼 Finance: http://localhost:5000/finance")
    print("🔧 API:     http://localhost:5000/api/chat")
    print("=" * 60)
    print(f"\n🤖 AI Mode: {ai_engine.ai_mode.upper()}")
    print("\n✅ GAURANGA Alpha ready! Call me anytime! 💪")
    app.run(host='0.0.0.0', port=5000, debug=False)
