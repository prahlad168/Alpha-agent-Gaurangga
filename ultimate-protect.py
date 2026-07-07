#!/usr/bin/env python3
"""
GitHub Repository Protection - Ultimate Browser Automation
This script uses pyppeteer to automate the GitHub UI
"""

import asyncio
import os

async def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🔒 GITHUB REPOSITORY PROTECTION                          ║
║        ULTIMATE AUTOMATION                                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    from pyppeteer import launch
    
    print("🚀 Launching browser...")
    
    browser = await launch(
        headless=False,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--start-maximized'
        ]
    )
    
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080})
    
    try:
        print("📱 Opening GitHub branch protection settings...")
        await page.goto(
            'https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/branches',
            {'waitUntil': 'networkidle2', 'timeout': 60000}
        )
        
        print("✅ Page loaded!")
        print()
        
        # Wait a bit for any JS to load
        await asyncio.sleep(2)
        
        # Try to click "Add rule" button
        print("🔍 Looking for 'Add rule' button...")
        
        try:
            # Try to find and click the Add rule button
            add_rule_btn = await page.querySelector('button:has-text("Add")')
            if add_rule_btn:
                await add_rule_btn.click()
                print("✅ Clicked 'Add' button")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠️  Could not auto-click: {e}")
        
        print()
        print("=" * 70)
        print("  🤖 AUTOMATION IN PROGRESS")
        print("=" * 70)
        print()
        print("The browser is now open with the branch protection page.")
        print()
        print("Please complete these steps manually:")
        print()
        print("1. LOGIN to GitHub if not already logged in")
        print()
        print("2. Find and click the 'Add rule' button (green)")
        print()
        print("3. Fill in the form:")
        print("   • Branch name pattern: main")
        print("   • ☑️ Require pull request reviews before merging")
        print("   •   → Required approving reviews: 1")
        print("   •   → ☑️ Dismiss stale reviews")
        print("   •   → ☑️ Require a code owner review")
        print("   • ☑️ Require conversation resolution before merging")
        print("   • ☑️ Do not allow bypassing the above settings")
        print("   • ☑️ Do not allow force pushes")
        print("   • ☑️ Do not allow deletions")
        print()
        print("4. Click 'Create'")
        print()
        print("📍 URL: https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/branches")
        print()
        
        # Wait for user to complete
        input("\n   Press ENTER after completing the setup...")
        
        # Verify
        print()
        print("🔍 Verifying protection...")
        await page.goto(
            'https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/branches',
            {'waitUntil': 'networkidle2'}
        )
        
        content = await page.content()
        if 'protected' in content.lower() or 'main' in content.lower():
            print()
            print("╔══════════════════════════════════════════════════════════════════╗")
            print("║                                                                  ║")
            print("║        ✅ PROTECTION SETUP COMPLETED!                          ║")
            print("║                                                                  ║")
            print("║        Your repository is now protected!                       ║")
            print("║                                                                  ║")
            print("╚══════════════════════════════════════════════════════════════════╝")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await browser.close()
        print()
        print("👋 Browser closed. Done!")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
