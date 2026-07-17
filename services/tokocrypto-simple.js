const https = require('https');
const crypto = require('crypto');

const API_KEY = 'f6082C178d6B518B07D47681Ab63CAa6jkTfZZspuRVNJFREHcXGuA8LvaGC23jA';
const API_SECRET = 'D4300da9820578084Ee4cEc588D7C406NcP7MfqdZR1ozHAvDZKpVBPPVbIv1EoP';
const BTC_WALLET = '1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2';

function createSignature(queryString) {
    return crypto.createHmac('sha256', API_SECRET).update(queryString).digest('hex');
}

function apiRequest(method, endpoint, params) {
    return new Promise((resolve, reject) => {
        const timestamp = Date.now();
        let query = `timestamp=${timestamp}`;
        if (params) {
            Object.keys(params).sort().forEach(key => {
                query += `&${key}=${params[key]}`;
            });
        }
        const signature = createSignature(query);
        query += `&signature=${signature}`;
        
        const options = {
            hostname: 'www.tokocrypto.com',
            path: `/open/v1${endpoint}?${query}`,
            method: method,
            headers: { 'X-MBX-APIKEY': API_KEY }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch (e) { resolve(data); }
            });
        });
        req.on('error', reject);
        req.end();
    });
}

async function main() {
    const amount = parseInt(process.argv[2]) || 20000;
    console.log('==========================================');
    console.log('   MAHA LAKSHMI - CEO PAYOUT');
    console.log('==========================================');
    console.log('Amount: Rp ' + amount.toLocaleString());
    console.log('Wallet: ' + BTC_WALLET);
    console.log('----------------------------------------');
    
    try {
        console.log('[1/2] Placing BUY order...');
        const order = await apiRequest('POST', '/orders', {
            symbol: 'BTC_IDR',
            symbolType: 3,
            side: 'BUY',
            type: 1,
            quoteQty: amount.toString()
        });
        
        if (order.success || order.code === 0) {
            console.log('SUCCESS! Order ID: ' + order.data.orderId);
            console.log('----------------------------------------');
            console.log('[2/2] Withdrawing BTC to wallet...');
            
            const btcAmount = (amount / 89300000).toFixed(8);
            const withdraw = await apiRequest('POST', '/asset/withdraw', {
                coin: 'BTC',
                amount: btcAmount,
                address: BTC_WALLET,
                network: 'BTC'
            });
            
            if (withdraw.success || withdraw.code === 0) {
                console.log('SUCCESS! Withdrawal TxID: ' + (withdraw.data.txId || withdraw.data.id));
                console.log('==========================================');
                console.log('   CEO PAYOUT COMPLETE!');
                console.log('   BTC: ' + btcAmount);
                console.log('   Wallet: ' + BTC_WALLET);
                console.log('==========================================');
            } else {
                console.log('WITHDRAW FAILED: ' + JSON.stringify(withdraw));
            }
        } else {
            console.log('ORDER FAILED: ' + JSON.stringify(order));
        }
    } catch (e) {
        console.log('ERROR: ' + e.message);
    }
}

main();
