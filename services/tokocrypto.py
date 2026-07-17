#!/usr/bin/env python3
"""
===============================================
TOKOCRYPTO API INTEGRATION - PYTHON VERSION
MAHA LAKSHMI HOLDINGS
===============================================

Python alternative for environments without Node.js

Usage:
    python3 tokocrypto.py 20000

Requirements:
    pip install requests python-dotenv

"""

import os
import sys
import json
import hmac
import hashlib
import time
import requests
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv

# ================================================
# CONFIGURATION
# ================================================

# Load .env file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(SCRIPT_DIR, ".env.payout")

if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE)
    print("✅ Loaded .env.payout configuration")

# Tokocrypto credentials
API_KEY = os.getenv("TOKOCRYPTO_API_KEY", "")
API_SECRET = os.getenv("TOKOCRYPTO_API_SECRET", "")
BTC_WALLET = os.getenv("BTC_WALLET_ADDRESS", "1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() == "true"

# API Configuration
BASE_URL = "https://www.tokocrypto.com"
API_VERSION = "/open/v1"

# ================================================
# HELPER FUNCTIONS
# ================================================

def create_signature(query_string: str) -> str:
    """Generate HMAC SHA256 signature"""
    return hmac.new(
        API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def api_request(method: str, endpoint: str, params: dict = None, signed: bool = False) -> dict:
    """Make API request to Tokocrypto"""
    timestamp = int(time.time() * 1000)
    
    # Build query parameters
    query_params = [f"timestamp={timestamp}"]
    if params:
        for key, value in params.items():
            query_params.append(f"{key}={value}")
    
    query_string = "&".join(query_params)
    
    # Add signature for signed endpoints
    if signed and API_SECRET and API_SECRET != "YOUR_API_SECRET_HERE":
        signature = create_signature(query_string)
        query_params.append(f"signature={signature}")
        query_string = "&".join(query_params)
    
    url = f"{BASE_URL}{API_VERSION}{endpoint}?{query_string}"
    
    headers = {
        "X-MBX-APIKEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"\n🔗 API Request: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_btc_price() -> dict:
    """Get current BTC/IDR price"""
    result = api_request("GET", "/market/ticker", {"symbol": "BTC_IDR"})
    
    if result.get("data") and len(result["data"]) > 0:
        return {
            "price": float(result["data"][0].get("lastPrice", 0)),
            "high": float(result["data"][0].get("highPrice", 0)),
            "low": float(result["data"][0].get("lowPrice", 0))
        }
    
    # Return default if API fails
    return {"price": 89300000, "source": "DEFAULT"}


def place_market_order(side: str, quote_qty: float) -> dict:
    """Place market buy/sell order"""
    params = {
        "symbol": "BTC_IDR",
        "symbolType": 3,
        "side": side.upper(),
        "type": 1,  # MARKET order
        "quoteQty": str(quote_qty)
    }
    
    return api_request("POST", "/orders", params, signed=True)


def withdraw_btc(amount: float, address: str, network: str = "BTC") -> dict:
    """Withdraw BTC to address"""
    params = {
        "amount": str(amount),
        "coin": "BTC",
        "address": address,
        "network": network
    }
    
    return api_request("POST", "/asset/withdraw", params, signed=True)


# ================================================
# MAIN EXECUTION
# ================================================

def execute_payout(idr_amount: int) -> dict:
    """Execute CEO payout - buy BTC and withdraw to wallet"""
    
    print("\n" + "=" * 70)
    print("🏦 MAHA LAKSHMI - CEO PAYOUT EXECUTION (Python)")
    print("=" * 70)
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print(f"💰 Amount: Rp {idr_amount:,}")
    print(f"🎯 Mode: {'SIMULATION' if SIMULATION_MODE else 'LIVE'}")
    print(f"👛 BTC Wallet: {BTC_WALLET}")
    print("=" * 70)
    
    # Check if API secret is configured
    has_api_secret = API_SECRET and API_SECRET != "YOUR_API_SECRET_HERE"
    
    if SIMULATION_MODE or not has_api_secret:
        print("\n⚠️ SIMULATION MODE - No actual transaction will be made")
        print(f"   Reason: {'Simulation mode enabled' if SIMULATION_MODE else 'API_SECRET not configured'}")
        
        btc_price = 89300000
        btc_amount = idr_amount / btc_price
        
        return {
            "success": True,
            "mode": "SIMULATION",
            "steps": {
                "step1_buy_btc": {
                    "action": "Market Buy BTC",
                    "idr_amount": idr_amount,
                    "btc_amount": round(btc_amount, 8),
                    "btc_price": btc_price,
                    "status": "SIMULATED",
                    "txid": f"SIM-TX-{int(time.time()*1000)}"
                },
                "step2_withdraw": {
                    "action": "Withdraw BTC",
                    "btc_amount": round(btc_amount, 8),
                    "destination": BTC_WALLET,
                    "network": "BTC",
                    "status": "SIMULATED",
                    "txid": f"SIM-WD-{int(time.time()*1000)}"
                }
            },
            "total_btc": round(btc_amount, 8),
            "destination_wallet": BTC_WALLET,
            "message": "⚠️ SIMULATION MODE - Configure API_SECRET for live execution"
        }
    
    # LIVE EXECUTION
    try:
        # Step 1: Get BTC price
        print("\n📊 Step 1: Getting BTC price...")
        price_info = get_btc_price()
        btc_price = price_info["price"]
        print(f"💵 Current BTC price: Rp {btc_price:,}")
        
        # Step 2: Calculate BTC amount
        btc_amount = idr_amount / btc_price
        print(f"💰 BTC amount: {btc_amount:.8f} BTC")
        
        # Step 3: Place buy order
        print("\n📊 Step 2: Placing market buy order...")
        buy_result = place_market_order("BUY", idr_amount)
        
        if not buy_result.get("success", False) and buy_result.get("code") != 0:
            raise Exception(f"Buy order failed: {json.dumps(buy_result)}")
        
        order_id = buy_result.get("data", {}).get("orderId")
        print(f"✅ Buy order placed! Order ID: {order_id}")
        
        # Step 4: Withdraw BTC
        print("\n📊 Step 3: Withdrawing BTC to CEO wallet...")
        withdraw_result = withdraw_btc(btc_amount, BTC_WALLET)
        
        if not withdraw_result.get("success", False) and withdraw_result.get("code") != 0:
            raise Exception(f"Withdrawal failed: {json.dumps(withdraw_result)}")
        
        txid = withdraw_result.get("data", {}).get("txId") or withdraw_result.get("data", {}).get("txid")
        print(f"✅ Withdrawal initiated! TxID: {txid}")
        
        return {
            "success": True,
            "mode": "LIVE",
            "steps": {
                "step1_get_price": {
                    "action": "Get BTC Price",
                    "price": btc_price,
                    "status": "COMPLETED"
                },
                "step2_buy_btc": {
                    "action": "Market Buy BTC",
                    "order_id": order_id,
                    "idr_amount": idr_amount,
                    "btc_amount": round(btc_amount, 8),
                    "status": "COMPLETED"
                },
                "step3_withdraw": {
                    "action": "Withdraw BTC",
                    "txid": txid,
                    "btc_amount": round(btc_amount, 8),
                    "destination": BTC_WALLET,
                    "network": "BTC",
                    "status": "PENDING_CONFIRMATION"
                }
            },
            "total_btc": round(btc_amount, 8),
            "destination_wallet": BTC_WALLET,
            "message": "✅ Live execution completed!"
        }
        
    except Exception as e:
        print(f"\n❌ EXECUTION FAILED: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ================================================
# CLI ENTRY POINT
# ================================================

if __name__ == "__main__":
    # Get amount from command line
    if len(sys.argv) > 1:
        try:
            amount = int(sys.argv[1])
        except ValueError:
            print(f"❌ Error: Invalid amount '{sys.argv[1]}'")
            print("Usage: python3 tokocrypto.py <amount_in_IDR>")
            sys.exit(1)
    else:
        amount = 20000  # Default test amount
    
    print(f"\n🎯 Test Amount: Rp {amount:,}")
    
    # Execute payout
    result = execute_payout(amount)
    
    # Print result
    print("\n📋 Result:")
    print(json.dumps(result, indent=2))
    
    # Save to log file
    log_file = os.path.join(SCRIPT_DIR, f"execution-log-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(log_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n📁 Log saved to: {log_file}")
    
    sys.exit(0 if result.get("success") else 1)
