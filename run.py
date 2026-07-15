#!/usr/bin/env python3
"""
MAHALAKSMI AIOS v1.0 - Startup Script
Automated system initialization and diagnostics
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_diagnostics():
    """Run system diagnostics across all 5 volumes."""
    print("\n" + "="*60)
    print("🔍 MAHALAKSMI AIOS v1.0 - System Diagnostics")
    print("="*60 + "\n")
    
    # Import components
    from app.core.engine import get_engine, initialize_system
    from app.core.security import get_security_manager
    from app.intelligence.gateway import get_gateway
    from app.development.openhands_connector import get_connector
    from app.business.revenue import get_revenue_manager
    from app.business.finance import get_finance_ledger
    from app.enterprise.hub import get_enterprise_hub
    
    components = [
        ("Volume I: Core Engine", lambda: get_engine()),
        ("Volume I: Security Manager", lambda: get_security_manager()),
        ("Volume II: Intelligence Gateway", lambda: get_gateway()),
        ("Volume III: OpenHands Connector", lambda: get_connector()),
        ("Volume IV: Revenue Manager", lambda: get_revenue_manager()),
        ("Volume IV: Finance Ledger", lambda: get_finance_ledger()),
        ("Volume V: Enterprise Hub", lambda: get_enterprise_hub()),
    ]
    
    all_healthy = True
    
    for name, get_component in components:
        try:
            component = get_component()
            if component:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: FAILED (null)")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            all_healthy = False
    
    print("\n" + "-"*60)
    
    # Initialize system
    print("\n🚀 Initializing system...")
    if await initialize_system():
        print("✅ System initialization: SUCCESS")
    else:
        print("❌ System initialization: FAILED")
        all_healthy = False
    
    print("\n" + "="*60)
    if all_healthy:
        print("✅ ALL DIAGNOSTICS PASSED - System Ready!")
    else:
        print("⚠️ SOME DIAGNOSTICS FAILED - Check logs")
    print("="*60 + "\n")
    
    return all_healthy


def main():
    """Main entry point."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🤖 MAHA LAKSHMI AIOS v1.0 ENTERPRISE EDITION       ║
    ║                                                           ║
    ║     Multi-Volume AI Operating System                     ║
    ║     Volume I:   Core Framework                           ║
    ║     Volume II:  Intelligence Gateway                     ║
    ║     Volume III: OpenHands Connector                     ║
    ║     Volume IV:  Revenue & Finance                       ║
    ║     Volume V:   Enterprise Integration                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run diagnostics
    try:
        success = asyncio.run(run_diagnostics())
        
        if success:
            print("\n🌐 Starting Uvicorn server...")
            print("📚 API Documentation: http://127.0.0.1:8000/docs")
            print("🏥 Health Check: http://127.0.0.1:8000/health")
            print()
            
            # Import and run uvicorn
            import uvicorn
            uvicorn.run(
                "app.main:app",
                host="0.0.0.0",
                port=8000,
                reload=False,
                log_level="info"
            )
        else:
            print("\n❌ System not ready. Please check configuration.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Shutdown requested. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
