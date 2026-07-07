#!/usr/bin/env python3
"""
GitHub Repository Auto-Protection Script
Uses Selenium/Playwright to automate browser actions
"""

import asyncio
import os
import sys

async def auto_protect():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🔒 GITHUB REPOSITORY PROTECTION                          ║
║        Auto-Protection Script                                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    try:
        from pyppeteer import launch
    except ImportError:
        print("📦 Installing pyppeteer...")
        os.system("pip install pyppeteer")
        from pyppeteer import launch
    
    print("🚀 Launching browser...")
    
    browser = await launch(
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
    )
    
    page = await browser.newPage()
    
    try:
        # Go to branch protection settings
        print("📱 Opening GitHub branch protection settings...")
        await page.goto(
            'https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/branches',
            {'waitUntil': 'networkidle2', 'timeout': 60000}
        )
        
        print("✅ Page loaded!")
        print()
        print("=" * 70)
        print("  AUTOMATION READY - Please login if needed")
        print("=" * 70)
        print()
        print("The browser will stay open. Follow the steps below:")
        print()
        print("1. If not logged in → Login with your GitHub credentials")
        print("2. Click the 'Add rule' button")
        print("3. Fill in the protection settings")
        print("4. Click 'Create'")
        print()
        print("📍 URL: https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/branches")
        print()
        print("⏸️  Waiting for you to complete setup...")
        print("   (Close browser manually when done)")
        print()
        
        # Wait indefinitely
        await asyncio.Event().wait()
        
    except asyncio.CancelledError:
        print("👋 Browser closed by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(auto_protect())
    except KeyboardInterrupt:
        print("\n👋 Script stopped")
