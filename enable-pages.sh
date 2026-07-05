#!/bin/bash
# Script untuk Enable GitHub Pages - Jalankan di terminal HP Pak Pur

echo "=========================================="
echo "🚀 GAURANGA - Enable GitHub Pages"
echo "=========================================="
echo ""

# Step 1: Make Public
echo "1️⃣ Membuat repo PUBLIC..."
gh repo edit prahlad168/Alpha-agent-Gaurangga \
  --visibility public \
  --accept-visibility-change-consequences

# Step 2: Enable Pages
echo ""
echo "2️⃣ Enable GitHub Pages..."
curl -s -X POST \
  -H "Authorization: Bearer $(gh auth token)" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/prahlad168/Alpha-agent-Gaurangga/pages" \
  -d '{"source":{"branch":"main","path":"/android-app"}}'

echo ""
echo ""
echo "=========================================="
echo "✅ SELESAI!"
echo "=========================================="
echo ""
echo "Buka dalam 2-5 menit:"
echo "https://prahlad168.github.io/Alpha-agent-Gaurangga/android-app/"
echo ""
