#!/usr/bin/env python3
"""Upload all android-app files to GitHub root for GitHub Pages"""

import os
import base64
import urllib.request
import json

TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "prahlad168/Alpha-agent-Gaurangga"
BASE_URL = f"https://api.github.com/repos/{REPO}/contents"

def get_sha(path):
    """Get file SHA if exists"""
    req = urllib.request.Request(f"{BASE_URL}/{path}", headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        return data.get("sha")
    except:
        return None

def upload_file(local_path, repo_path):
    """Upload single file"""
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    data = json.dumps({
        "message": f"Add {repo_path}",
        "content": content
    }).encode()
    
    sha = get_sha(repo_path)
    if sha:
        data = json.dumps({
            "message": f"Update {repo_path}",
            "content": content,
            "sha": sha
        }).encode()
    
    req = urllib.request.Request(
        f"{BASE_URL}/{repo_path}",
        data=data,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    )
    
    try:
        resp = urllib.request.urlopen(req)
        print(f"✅ {repo_path}")
        return True
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        print(f"❌ {repo_path}: {body.get('message', str(e))}")
        return False

# Upload all files
app_dir = "android-app"
success = 0
failed = 0

for root, dirs, files in os.walk(app_dir):
    for file in files:
        local_path = os.path.join(root, file)
        repo_path = local_path.replace("android-app/", "")
        
        if upload_file(local_path, repo_path):
            success += 1
        else:
            failed += 1

print(f"\n📊 Total: {success} ✅, {failed} ❌")
print("\n🎉 Jika semua ✅, tunggu 2-5 menit dan buka:")
print("https://prahlad168.github.io/Alpha-agent-Gaurangga/")
