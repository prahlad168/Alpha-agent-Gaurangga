# 🔒 GitHub Repository Protection Guide

## Status: ⚠️ MANUAL ACTION REQUIRED

The current GitHub token lacks admin permissions to automatically set branch protection.

---

## 🚀 Quick Solution (2 Minutes)

### Step 1: Create Personal Access Token (PAT)

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Fill in:
   - **Name**: `Repo Admin`
   - **Expiration**: 30 days
   - **Scopes**: ✅ Select `repo` (Full control)
4. Click **"Generate token"**
5. **COPY** the token immediately

### Step 2: Run Protection Script

Open terminal and run:

```bash
cd Alpha-agent-Gaurangga
export GITHUB_TOKEN="paste-your-token-here"
bash protect-completely.sh
```

### Step 3: Verify

Check: https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/branches

---

## 🔐 What This Will Protect

| Protection | Status |
|------------|--------|
| Require PR Reviews (1 approval) | ✅ |
| Dismiss Stale Reviews | ✅ |
| Require Code Owner Review | ✅ |
| No Force Pushes | ✅ |
| No Branch Deletion | ✅ |
| Repository Private | ✅ |
| Forking Disabled | ✅ |

---

## 📁 Files Created

```
Alpha-agent-Gaurangga/
├── protect-completely.sh    # One-command protection script
├── protect-repo.sh          # Detailed protection script
└── PROTECTION-README.md     # This file
```

---

## ⚡ Alternative: Manual Setup (3 Minutes)

If you prefer not to use a PAT:

1. Go to: https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/branches
2. Click **"Add rule"**
3. Fill in:
   - Branch name pattern: `main`
   - ☑️ Require pull request reviews before merging
   - Required approving reviews: `1`
   - ☑️ Dismiss stale reviews
   - ☑️ Require a code owner review
   - ☑️ Do not allow force pushes
   - ☑️ Do not allow deletions
4. Click **"Create"**

---

## 🔑 Token Scopes Explained

| Scope | Needed For |
|-------|-----------|
| `repo` | Full control (includes admin) |
| `admin:org` | Organization-level admin |
| `public_repo` | Public repos only |

---

## ⚠️ Why This Requires Manual Action

The current GitHub token (used by the agent) has:
- ❌ No `repo` (admin) scope
- ❌ No `admin:org` scope

Only tokens with **admin permissions** can modify branch protection settings.

---

## ✅ After Setup

Your repository will be protected:
- All changes must go through Pull Requests
- At least 1 approval required to merge
- No force pushes allowed
- Repository is private
- Forking disabled

---

**Questions?** Contact: OpenHands Support
