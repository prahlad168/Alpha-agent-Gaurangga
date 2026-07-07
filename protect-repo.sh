#!/bin/bash

# =============================================================================
# PROTECT REPOSITORY SCRIPT
# =============================================================================
# 
# Script ini akan melindungi repository Alpha-agent-Gaurangga di GitHub
# 
# CARA PAKAI:
# 1. Buka terminal
# 2. Copy script ini ke file, contoh: protect-repo.sh
# 3. Buat Personal Access Token (PAT) baru dengan scope "repo" di:
#    https://github.com/settings/tokens
# 4. Run script dengan: GITHUB_TOKEN=<your-token> bash protect-repo.sh
#
# =============================================================================

REPO="prahlad168/Alpha-agent-Gaurangga"
BRANCH="main"

echo "=============================================="
echo "  PROTECTING REPOSITORY"
echo "  $REPO"
echo "=============================================="
echo ""

# Check if token exists
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ ERROR: GITHUB_TOKEN not set!"
    echo ""
    echo "Cara setup:"
    echo "1. Buka: https://github.com/settings/tokens"
    echo "2. Klik 'Generate new token (classic)'"
    echo "3. Pilih scope: repo (full control)"
    echo "4. Copy token-nya"
    echo "5. Run: GITHUB_TOKEN=<token> bash protect-repo.sh"
    exit 1
fi

echo "🔐 Step 1: Setting Branch Protection..."
curl -X PUT \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/branches/$BRANCH/protection" \
  -d '{
    "required_status_checks": null,
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true,
      "required_approving_review_count": 1
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "required_linear_history": false,
    "require_conversation_resolution": true
  }'

echo ""
echo "✅ Branch protection enabled!"
echo ""

echo "🔒 Step 2: Making Repository Private..."
curl -X PATCH \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO" \
  -d '{"visibility": "private", "allow_forking": false}'

echo ""
echo "🔐 Repository is now private!"
echo ""

echo "=============================================="
echo "  ✅ PROTECTION COMPLETE!"
echo "=============================================="
echo ""
echo "Settings yang aktif:"
echo "  ✅ Require PR Reviews (1 approval)"
echo "  ✅ Dismiss Stale Reviews"
echo "  ✅ Require Code Owner Review"
echo "  ✅ Require Conversation Resolution"
echo "  ✅ Do Not Allow Force Pushes"
echo "  ✅ Do Not Allow Branch Deletion"
echo "  ✅ Block Admin Bypass"
echo "  ✅ Repository is Private"
echo "  ✅ Forking Disabled"
echo ""
echo "Repository: https://github.com/$REPO"
echo "Settings:   https://github.com/$REPO/settings/branches"
echo ""
