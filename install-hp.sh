#!/bin/bash
# Alpha Gaurangga - Quick Install for Android (Termux)
# Copy semua baris ini ke Termux dan paste

echo "🤖 ALPHA GAURANGA INSTALLER"
echo "============================"
echo ""

# Check if Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo "⚠️ Please run this in Termux on Android!"
    echo "Download: https://f-droid.org"
    exit 1
fi

echo "📦 Updating packages..."
pkg update && pkg upgrade -y

echo "📦 Installing dependencies..."
pkg install python git nodejs espeak-ng ffmpeg sox -y

echo "📥 Cloning project..."
cd ~/storage/shared
rm -rf Alpha-agent-Gaurangga 2>/dev/null
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga/system-agent

echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ INSTALLATION COMPLETE!"
echo "============================"
echo ""
echo "🚀 To start Alpha Gaurangga:"
echo "   cd ~/storage/shared/Alpha-agent-Gaurangga/system-agent"
echo "   python3 gauranga_agent.py --always-on"
echo ""
echo "🎤 To test voice:"
echo "   python3 -c \"from engine.tts import TTSEngine; t=TTSEngine({'voice':{'tts':'system'}}); t.speak('Halo Pak Pur, Alpha Gaurangga aktif!')\""
