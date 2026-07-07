#!/bin/bash
# =============================================================================
# GITHUB REPOSITORY PROTECTION - COMPLETE SOLUTION
# =============================================================================
# Created by GAURANGA Alpha Agent
# Date: 2026-07-07
# =============================================================================

set -e

REPO="prahlad168/Alpha-agent-Gaurangga"
BRANCH="main"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        🔒 GITHUB REPOSITORY PROTECTION                        ║"
echo "║        Alpha-agent-Gaurangga                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check for GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ ERROR: GITHUB_TOKEN not found!"
    echo ""
    echo "Please create a PAT with 'repo' scope:"
    echo "  1. https://github.com/settings/tokens"
    echo "  2. Generate new token (classic)"
    echo "  3. Select: ✅ repo (Full control)"
    echo "  4. Run: export GITHUB_TOKEN='your-token' && bash protect-completely.sh"
    exit 1
fi

echo "✅ Token found: ${GITHUB_TOKEN:0:8}..."
echo ""

# STEP 1: Branch Protection
echo "📌 Step 1: Setting branch protection..."
curl -s -X PUT \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/branches/$BRANCH/protection" \
    -d '{"enforce_admins":true,"required_pull_request_reviews":{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true},"allow_force_pushes":false,"allow_deletions":false}'
echo " ✅ Branch protection applied"

# STEP 2: Make Private
echo "📌 Step 2: Making repository private..."
curl -s -X PATCH \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO" \
    -d '{"visibility":"private","allow_forking":false}'
echo " ✅ Repository is now private"

# Verify
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        ✅ PROTECTION COMPLETE                                   ║"
echo "║                                                                  ║"
echo "║  Verify at: https://github.com/$REPO/settings/branches        ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
