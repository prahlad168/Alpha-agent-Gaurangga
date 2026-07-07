<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💬 Alpha Gaurangga AI Chat</title>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --success: #10b981;
            --dark: #0a0a0a;
            --card: #141414;
            --border: #262626;
            --text: #ffffff;
            --text-muted: #737373;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', system-ui, sans-serif;
        }

        body {
            background: var(--dark);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Header */
        .chat-header {
            background: var(--card);
            padding: 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .gauranga-avatar {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 18px;
            position: relative;
        }

        .gauranga-avatar::after {
            content: '';
            position: absolute;
            bottom: 2px;
            right: 2px;
            width: 12px;
            height: 12px;
            background: var(--success);
            border-radius: 50%;
            border: 2px solid var(--card);
        }

        .chat-info h1 {
            font-size: 18px;
            font-weight: 600;
        }

        .chat-info p {
            font-size: 12px;
            color: var(--text-muted);
        }

        .status-badge {
            margin-left: auto;
            background: rgba(16, 185, 129, 0.2);
            color: var(--success);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .status-badge.offline {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        /* Messages */
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            max-width: 85%;
            padding: 16px 20px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.6;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            background: var(--primary);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 6px;
        }

        .message.ai {
            background: var(--card);
            border: 1px solid var(--border);
            align-self: flex-start;
            border-bottom-left-radius: 6px;
        }

        .message.ai .sender {
            font-size: 12px;
            color: var(--primary);
            font-weight: 600;
            margin-bottom: 8px;
        }

        .message.typing {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dots span {
            width: 8px;
            height: 8px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }

        /* Quick Actions */
        .quick-actions {
            padding: 10px 20px;
            display: flex;
            gap: 8px;
            overflow-x: auto;
            scrollbar-width: none;
        }

        .quick-actions::-webkit-scrollbar {
            display: none;
        }

        .quick-btn {
            background: var(--card);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 13px;
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.2s;
        }

        .quick-btn:hover {
            background: var(--primary);
            border-color: var(--primary);
        }

        /* Input Area */
        .input-area {
            background: var(--card);
            padding: 20px;
            border-top: 1px solid var(--border);
        }

        .input-container {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .input-wrapper {
            flex: 1;
            position: relative;
        }

        #messageInput {
            width: 100%;
            background: var(--dark);
            border: 1px solid var(--border);
            border-radius: 25px;
            padding: 14px 20px;
            padding-right: 50px;
            color: var(--text);
            font-size: 14px;
            resize: none;
            outline: none;
            transition: border-color 0.2s;
        }

        #messageInput:focus {
            border-color: var(--primary);
        }

        #messageInput::placeholder {
            color: var(--text-muted);
        }

        .voice-btn {
            position: absolute;
            right: 8px;
            bottom: 8px;
            width: 36px;
            height: 36px;
            background: var(--primary);
            border: none;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .voice-btn:hover {
            transform: scale(1.1);
        }

        .voice-btn.recording {
            background: #ef4444;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .send-btn {
            width: 50px;
            height: 50px;
            background: var(--primary);
            border: none;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            transition: all 0.2s;
        }

        .send-btn:hover {
            background: #5558e3;
            transform: scale(1.05);
        }

        .send-btn:disabled {
            background: var(--border);
            cursor: not-allowed;
        }

        /* Settings */
        .settings-bar {
            padding: 10px 20px;
            background: var(--card);
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-muted);
        }

        .model-select {
            background: var(--dark);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
        }

        /* Toast */
        .toast {
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--card);
            border: 1px solid var(--border);
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 14px;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
        }

        .toast.show {
            opacity: 1;
        }

        .toast.error {
            border-color: #ef4444;
            color: #ef4444;
        }

        .toast.success {
            border-color: var(--success);
            color: var(--success);
        }
    </style>
</head>
<body>
    <header class="chat-header">
        <div class="gauranga-avatar">GA</div>
        <div class="chat-info">
            <h1>Alpha Gaurangga</h1>
            <p>Executive AI Assistant - Maha Lakshmi Corp</p>
        </div>
        <div class="status-badge" id="statusBadge">🔴 Offline</div>
    </header>

    <div class="messages-container" id="messagesContainer">
        <!-- Welcome message -->
        <div class="message ai">
            <div class="sender">🙏 Alpha Gaurangga</div>
            Swastyastu, Pak Pur! <em>🙏✨</em><br><br>
            Saya adalah <strong>Alpha Gaurangga</strong>, Executive AI Assistant pribadi Bapak.<br><br>
            Saya siap membantu Bapak dengan:<br>
            • 💼 Strategi bisnis Maha Lakshmi Corp<br>
            • 📊 Analisis 10 SBUs<br>
            • 💰 Keuangan & target revenue<br>
            • 👨‍👩‍👧‍👦 Keseimbangan keluarga<br><br>
            Ada yang bisa saya bantu hari ini?
        </div>
    </div>

    <div class="quick-actions">
        <button class="quick-btn" onclick="sendQuickMessage('laporan pagi')">📋 Laporan Pagi</button>
        <button class="quick-btn" onclick="sendQuickMessage('target revenue bulan ini')">💰 Target Revenue</button>
        <button class="quick-btn" onclick="sendQuickMessage('status 10 SBUs')">🏢 Status SBUs</button>
        <button class="quick-btn" onclick="sendQuickMessage('rencana hari ini')">📅 Rencana Harian</button>
        <button class="quick-btn" onclick="sendQuickMessage('tips produktivitas')">💡 Tips Produktif</button>
    </div>

    <div class="input-area">
        <div class="input-container">
            <div class="input-wrapper">
                <textarea 
                    id="messageInput" 
                    placeholder="Ketik pesan untuk Alpha Gaurangga..."
                    rows="1"
                    onkeydown="handleKeyDown(event)"
                    oninput="autoResize(this)"
                ></textarea>
                <button class="voice-btn" id="voiceBtn" onclick="toggleVoice()">
                    <i class="fas fa-microphone"></i>
                </button>
            </div>
            <button class="send-btn" id="sendBtn" onclick="sendMessage()">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
    </div>

    <div class="settings-bar">
        <span>Model: <span id="modelName">gemini-flash</span></span>
        <span id="connectionStatus">Connecting...</span>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        // ============================================
        // ALPHA GAURANGGA AI CHAT
        // ============================================
        
        const API_URL = 'http://localhost:5000/api/chat';
        let conversationHistory = [];
        let isRecording = false;
        let recognition = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            checkConnection();
            setupVoiceRecognition();
            document.getElementById('messageInput').focus();
        });

        // Check AI connection
        async function checkConnection() {
            try {
                const response = await fetch('http://localhost:5000/api/status');
                const data = await response.json();
                
                const badge = document.getElementById('statusBadge');
                const connStatus = document.getElementById('connectionStatus');
                
                if (data.gemini || data.openai) {
                    badge.textContent = '🟢 Online';
                    badge.classList.remove('offline');
                    connStatus.textContent = 'Connected: ' + data.model;
                    document.getElementById('modelName').textContent = data.model;
                } else {
                    badge.textContent = '🔴 Offline';
                    badge.classList.add('offline');
                    connStatus.textContent = 'Disconnected';
                    showToast('AI server not running. Start server first!', 'error');
                }
            } catch (e) {
                document.getElementById('statusBadge').textContent = '🔴 Offline';
                document.getElementById('statusBadge').classList.add('offline');
                document.getElementById('connectionStatus').textContent = 'Server not found';
            }
        }

        // Send message
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            input.style.height = 'auto';
            
            // Show typing indicator
            showTyping();
            
            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                hideTyping();
                
                if (data.success) {
                    addMessage(data.reply, 'ai');
                    conversationHistory.push({ role: 'user', content: message });
                    conversationHistory.push({ role: 'assistant', content: data.reply });
                } else {
                    addMessage('Maaf, terjadi kesalahan: ' + (data.error || 'Unknown error'), 'ai');
                    showToast('Error: ' + (data.error || 'Unknown'), 'error');
                }
            } catch (e) {
                hideTyping();
                addMessage('Tidak dapat terhubung ke AI server. Pastikan server sedang berjalan di port 5000.', 'ai');
                showToast('Connection failed', 'error');
            }
        }

        // Quick message
        function sendQuickMessage(message) {
            document.getElementById('messageInput').value = message;
            sendMessage();
        }

        // Add message to chat
        function addMessage(content, type) {
            const container = document.getElementById('messagesContainer');
            const msg = document.createElement('div');
            msg.className = `message ${type}`;
            
            if (type === 'ai') {
                msg.innerHTML = `<div class="sender">🙏 Alpha Gaurangga</div>${formatMessage(content)}`;
            } else {
                msg.textContent = content;
            }
            
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
        }

        // Format message (basic markdown)
        function formatMessage(text) {
            return text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');
        }

        // Typing indicator
        function showTyping() {
            const container = document.getElementById('messagesContainer');
            const typing = document.createElement('div');
            typing.className = 'message ai typing';
            typing.id = 'typingIndicator';
            typing.innerHTML = `
                <div class="sender">🙏 Alpha Gaurangga</div>
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            `;
            container.appendChild(typing);
            container.scrollTop = container.scrollHeight;
        }

        function hideTyping() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }

        // Voice Recognition
        function setupVoiceRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.lang = 'id-ID';
                recognition.continuous = false;
                recognition.interimResults = true;

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('messageInput').value = transcript;
                };

                recognition.onend = () => {
                    document.getElementById('voiceBtn').classList.remove('recording');
                    isRecording = false;
                };

                recognition.onerror = (event) => {
                    console.log('Speech error:', event.error);
                    document.getElementById('voiceBtn').classList.remove('recording');
                    isRecording = false;
                };
            }
        }

        function toggleVoice() {
            if (!recognition) {
                showToast('Voice recognition not supported', 'error');
                return;
            }

            if (isRecording) {
                recognition.stop();
                isRecording = false;
                document.getElementById('voiceBtn').classList.remove('recording');
            } else {
                recognition.start();
                isRecording = true;
                document.getElementById('voiceBtn').classList.add('recording');
                showToast('Listening...', 'success');
            }
        }

        // Text-to-Speech
        function speak(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'id-ID';
                utterance.rate = 1;
                utterance.pitch = 1;
                speechSynthesis.speak(utterance);
            }
        }

        // Auto-resize textarea
        function autoResize(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
        }

        // Handle Enter key
        function handleKeyDown(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        // Toast notification
        function showToast(message, type = '') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show ' + type;
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        // Refresh connection
        setInterval(checkConnection, 30000);
    </script>
</body>
</html>
