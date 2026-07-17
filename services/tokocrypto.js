/**
 * ================================================
 * TOKOCRYPTO API INTEGRATION
 * MAHA LAKSHMI HOLDINGS
 * ================================================
 * 
 * Integration for BTC Market Order & Withdrawal
 * API Documentation: https://www.tokocrypto.com/apidocs
 * 
 * VERSION: 1.0.0
 * DATE: 2026-07-17
 * 
 * SECURITY:
 * - API keys stored in environment variables
 * - HMAC SHA256 signature for all signed requests
 * - IP whitelist required (34.10.175.217)
 * ================================================
 */

const https = require('https');
const crypto = require('crypto');

// ================================================
// CONFIGURATION
// ================================================

const CONFIG = {
    baseUrl: 'https://www.tokocrypto.com',
    apiVersion: '/open/v1',
    
    // Load from environment
    apiKey: process.env.TOKOCRYPTO_API_KEY,
    apiSecret: process.env.TOKOCRYPTO_API_SECRET,
    
    // Trading pair
    tradingPair: 'BTC_IDR', // For BTC/IDR trading
    symbolType: 3, // IDR trading pair
    
    // BTC withdrawal address
    btcWallet: process.env.BTC_WALLET_ADDRESS || '1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2',
    
    // Simulation mode
    simulationMode: process.env.SIMULATION_MODE !== 'false'
};

// ================================================
// SIGNATURE GENERATOR (HMAC SHA256)
// ================================================

function createSignature(queryString, secret) {
    // HMAC SHA256 signature - hex lowercase
    return crypto
        .createHmac('sha256', secret)
        .update(queryString)
        .digest('hex');
}

// ================================================
// API REQUEST HANDLER
// ================================================

function apiRequest(method, endpoint, params = {}, signed = false) {
    return new Promise((resolve, reject) => {
        // Build query string with sorted parameters
        const timestamp = Date.now();
        let queryParams = `timestamp=${timestamp}`;
        
        // Sort parameters alphabetically for signature
        if (Object.keys(params).length > 0) {
            const sortedKeys = Object.keys(params).sort();
            for (const key of sortedKeys) {
                queryParams += `&${key}=${params[key]}`;
            }
        }
        
        // Create signature if signed endpoint
        let signature = '';
        if (signed && CONFIG.apiSecret && CONFIG.apiSecret !== 'YOUR_API_SECRET_HERE') {
            signature = createSignature(queryParams, CONFIG.apiSecret);
            queryParams += `&signature=${signature}`;
        }
        
        // Debug: log what we're signing
        console.log(`   🔐 Signing query: ${queryParams.substring(0, 100)}...`);
        
        const path = `${CONFIG.apiVersion}${endpoint}?${queryParams}`;
        
        const options = {
            hostname: 'www.tokocrypto.com',
            path: path,
            method: method,
            headers: {
                'X-MBX-APIKEY': CONFIG.apiKey || '',
                'Content-Type': 'application/json'
            }
        };
        
        console.log(`\n🔗 API Request: ${method} ${endpoint}`);
        
        const req = https.request(options, (res) => {
            let data = '';
            
            res.on('data', chunk => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    resolve(result);
                } catch (error) {
                    resolve(data);
                }
            });
        });
        
        req.on('error', (error) => {
            reject(error);
        });
        
        req.end();
    });
}

// ================================================
// ACCOUNT INFO
// ================================================

async function getAccountInfo() {
    console.log('\n📋 Fetching account info...');
    const result = await apiRequest('GET', '/account/accountInfo', {}, true);
    return result;
}

// ================================================
// GET BTC PRICE
// ================================================

async function getBTCPrice() {
    console.log('\n💰 Fetching BTC price...');
    const result = await apiRequest('GET', '/market/ticker', { 
        symbol: CONFIG.tradingPair 
    });
    
    // Try different response formats
    if (result.data && result.data.length > 0) {
        return {
            price: parseFloat(result.data[0].lastPrice),
            highPrice: parseFloat(result.data[0].highPrice),
            lowPrice: parseFloat(result.data[0].lowPrice),
            volume: parseFloat(result.data[0].volume)
        };
    } else if (result.lastPrice) {
        // Direct format
        return {
            price: parseFloat(result.lastPrice),
            highPrice: parseFloat(result.highPrice),
            lowPrice: parseFloat(result.lowPrice),
            volume: parseFloat(result.volume)
        };
    } else if (result.data && result.data.lastPrice) {
        // Nested data format
        return {
            price: parseFloat(result.data.lastPrice),
            highPrice: parseFloat(result.data.highPrice),
            lowPrice: parseFloat(result.data.lowPrice),
            volume: parseFloat(result.data.volume)
        };
    }
    
    // Return default price for simulation
    console.log('⚠️ Could not fetch live price, using default');
    return {
        price: 89300000, // Default BTC price in IDR
        source: 'DEFAULT'
    };
}

// ================================================
// PLACE MARKET ORDER (BUY BTC)
// ================================================

async function placeMarketOrder(side, quoteQty) {
    console.log(`\n📝 Placing ${side} order for Rp ${quoteQty.toLocaleString('id-ID')}...`);
    
    const params = {
        symbol: CONFIG.tradingPair,
        symbolType: CONFIG.symbolType,
        side: side, // BUY or SELL
        type: 1, // MARKET order
        quoteQty: quoteQty.toString()
    };
    
    const result = await apiRequest('POST', '/orders', params, true);
    
    return {
        success: result.success || result.code === 0,
        orderId: result.data?.orderId,
        clientId: result.data?.clientId,
        executedQty: result.data?.executedQty,
        executedQuoteQty: result.data?.executedQuoteQty,
        status: result.data?.status,
        raw: result
    };
}

// ================================================
// WITHDRAW BTC
// ================================================

async function withdrawBTC(amount, address, network = 'BTC') {
    console.log(`\n🚀 Withdrawing ${amount} BTC to ${address}...`);
    
    const params = {
        amount: amount.toString(),
        coin: 'BTC',
        address: address,
        network: network // BTC, BEP20, TRC20, etc.
    };
    
    const result = await apiRequest('POST', '/asset/withdraw', params, true);
    
    return {
        success: result.success || result.code === 0,
        withdrawId: result.data?.id || result.data?.withdrawId,
        txid: result.data?.txId || result.data?.txid,
        status: result.data?.status,
        raw: result
    };
}

// ================================================
// GET DEPOSIT/WITHDRAW HISTORY
// ================================================

async function getWithdrawHistory(limit = 10) {
    console.log('\n📜 Fetching withdraw history...');
    const result = await apiRequest('GET', '/asset/withdraw/history', { 
        coin: 'BTC',
        limit: limit 
    }, true);
    return result;
}

// ================================================
// BUY BTC & WITHDRAW TO CEO WALLET
// ================================================

async function executeCEOPayout(idrAmount) {
    const startTime = Date.now();
    
    console.log('\n' + '='.repeat(70));
    console.log('🏦 MAHA LAKSHMI - CEO PAYOUT EXECUTION');
    console.log('='.repeat(70));
    console.log(`📅 Timestamp: ${new Date().toISOString()}`);
    console.log(`💰 Amount: Rp ${idrAmount.toLocaleString('id-ID')}`);
    console.log(`🎯 Mode: ${CONFIG.simulationMode ? 'SIMULATION' : 'LIVE'}`);
    console.log(`👛 BTC Wallet: ${CONFIG.btcWallet}`);
    console.log('='.repeat(70));
    
    // Check if API secret is configured
    const hasApiSecret = CONFIG.apiSecret && CONFIG.apiSecret !== 'YOUR_API_SECRET_HERE';
    
    if (CONFIG.simulationMode || !hasApiSecret) {
        console.log('\n⚠️ SIMULATION MODE - No actual transaction will be made');
        console.log(`   Reason: ${CONFIG.simulationMode ? 'Simulation mode enabled' : 'API_SECRET not configured'}`);
        console.log('');
        
        // Get simulated BTC price
        const btcPrice = 89300000; // Simulated price
        const btcAmount = idrAmount / btcPrice;
        
        return {
            success: true,
            mode: 'SIMULATION',
            steps: {
                step1_buy_btc: {
                    action: 'Market Buy BTC',
                    idr_amount: idrAmount,
                    btc_amount: btcAmount.toFixed(8),
                    btc_price: btcPrice,
                    status: 'SIMULATED',
                    txid: 'SIM-TX-' + Date.now()
                },
                step2_withdraw: {
                    action: 'Withdraw BTC',
                    btc_amount: btcAmount.toFixed(8),
                    destination: CONFIG.btcWallet,
                    network: 'BTC',
                    status: 'SIMULATED',
                    txid: 'SIM-WD-' + Date.now()
                }
            },
            total_btc: btcAmount.toFixed(8),
            destination_wallet: CONFIG.btcWallet,
            execution_time_ms: Date.now() - startTime,
            message: '⚠️ SIMULATION MODE - Configure API_SECRET and set SIMULATION_MODE=false for live execution'
        };
    }
    
    try {
        // Step 1: Get current BTC price
        console.log('\n📊 Step 1: Getting BTC price...');
        const priceInfo = await getBTCPrice();
        const btcPrice = priceInfo.price;
        console.log(`💵 Current BTC price: Rp ${btcPrice.toLocaleString('id-ID')}`);
        
        // Step 2: Calculate BTC amount
        const btcAmount = idrAmount / btcPrice;
        console.log(`💰 BTC amount: ${btcAmount.toFixed(8)} BTC`);
        
        // Step 3: Place market buy order
        console.log('\n📊 Step 2: Placing market buy order...');
        const buyResult = await placeMarketOrder('BUY', idrAmount);
        
        if (!buyResult.success) {
            throw new Error(`Buy order failed: ${JSON.stringify(buyResult)}`);
        }
        
        console.log(`✅ Buy order placed! Order ID: ${buyResult.orderId}`);
        
        // Step 4: Withdraw BTC to CEO wallet
        console.log('\n📊 Step 3: Withdrawing BTC to CEO wallet...');
        const withdrawResult = await withdrawBTC(btcAmount, CONFIG.btcWallet);
        
        if (!withdrawResult.success) {
            throw new Error(`Withdrawal failed: ${JSON.stringify(withdrawResult)}`);
        }
        
        console.log(`✅ Withdrawal initiated! TxID: ${withdrawResult.txid}`);
        
        const executionTime = Date.now() - startTime;
        
        console.log('\n' + '='.repeat(70));
        console.log('✅ EXECUTION COMPLETE');
        console.log('='.repeat(70));
        
        return {
            success: true,
            mode: 'LIVE',
            steps: {
                step1_get_price: {
                    action: 'Get BTC Price',
                    price: btcPrice,
                    status: 'COMPLETED'
                },
                step2_buy_btc: {
                    action: 'Market Buy BTC',
                    order_id: buyResult.orderId,
                    client_id: buyResult.clientId,
                    idr_amount: idrAmount,
                    btc_amount: btcAmount.toFixed(8),
                    status: 'COMPLETED'
                },
                step3_withdraw: {
                    action: 'Withdraw BTC',
                    withdraw_id: withdrawResult.withdrawId,
                    txid: withdrawResult.txid,
                    btc_amount: btcAmount.toFixed(8),
                    destination: CONFIG.btcWallet,
                    network: 'BTC',
                    status: 'PENDING_CONFIRMATION'
                }
            },
            total_btc: btcAmount.toFixed(8),
            destination_wallet: CONFIG.btcWallet,
            execution_time_ms: executionTime,
            message: '✅ Live execution completed. Withdrawal pending blockchain confirmation.'
        };
        
    } catch (error) {
        console.error('\n❌ EXECUTION FAILED:', error.message);
        
        return {
            success: false,
            error: error.message,
            execution_time_ms: Date.now() - startTime
        };
    }
}

// ================================================
// EXPORT MODULES
// ================================================

module.exports = {
    CONFIG,
    getAccountInfo,
    getBTCPrice,
    placeMarketOrder,
    withdrawBTC,
    getWithdrawHistory,
    executeCEOPayout
};

// ================================================
// CLI EXECUTION
// ================================================

if (require.main === module) {
    (async () => {
        // Load .env if exists
        const fs = require('fs');
        const path = require('path');
        
        const envPath = path.join(__dirname, '.env.payout');
        if (fs.existsSync(envPath)) {
            const envContent = fs.readFileSync(envPath, 'utf8');
            envContent.split('\n').forEach(line => {
                const [key, ...valueParts] = line.split('=');
                if (key && valueParts.length > 0 && !key.startsWith('#')) {
                    process.env[key.trim()] = valueParts.join('=').trim();
                }
            });
            console.log('✅ Loaded .env.payout configuration');
        }
        
        // Update config with loaded values
        CONFIG.apiKey = process.env.TOKOCRYPTO_API_KEY;
        CONFIG.apiSecret = process.env.TOKOCRYPTO_API_SECRET;
        CONFIG.btcWallet = process.env.BTC_WALLET_ADDRESS || CONFIG.btcWallet;
        CONFIG.simulationMode = process.env.SIMULATION_MODE === 'true';
        
        // Get test amount from command line or use default
        const testAmount = parseInt(process.argv[2]) || 20000; // Default Rp 20,000
        
        console.log(`\n🎯 Test Amount: Rp ${testAmount.toLocaleString('id-ID')}`);
        
        // Execute payout
        const result = await executeCEOPayout(testAmount);
        
        console.log('\n📋 Result:');
        console.log(JSON.stringify(result, null, 2));
        
        process.exit(result.success ? 0 : 1);
    })();
}
