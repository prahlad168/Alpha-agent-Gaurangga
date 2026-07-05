#!/bin/bash
# Upload android-app files to GitHub root

REPO="prahlad168/Alpha-agent-Gaurangga"
TOKEN="$GITHUB_TOKEN"

echo "🚀 Uploading GAURANGA app to GitHub..."

# Upload index.html
echo "📄 index.html..."
CONTENT=$(base64 -w0 android-app/index.html)
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/contents/index.html" \
  -d "{\"message\":\"Add index.html for GitHub Pages\",\"content\":\"$CONTENT\"}" | grep -o '"commit".*' || echo "Done"

# Upload CSS
echo "🎨 css/style.css..."
mkdir -p android-app/css android-app/js android-app/assets android-app/icons
CONTENT=$(base64 -w0 android-app/css/style.css)
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/contents/css/style.css" \
  -d "{\"message\":\"Add CSS\",\"content\":\"$CONTENT\"}" | grep -o '"commit".*' || echo "Done"

# Upload JS
echo "⚡ js/gauranga-agent.js..."
CONTENT=$(base64 -w0 android-app/js/gauranga-agent.js)
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/contents/js/gauranga-agent.js" \
  -d "{\"message\":\"Add JavaScript\",\"content\":\"$CONTENT\"}" | grep -o '"commit".*' || echo "Done"

echo ""
echo "✅ SELESAI!"
echo ""
echo "📌 IMPORTANT: Repo harus PUBLIC dulu!"
echo ""
echo "Buka link berikut dan enable GitHub Pages:"
echo "https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/pages"
echo ""
echo "Atau tunggu saya coba enable sekarang..."
