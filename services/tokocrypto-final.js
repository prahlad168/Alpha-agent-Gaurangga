const https = require('https');
const crypto = require('crypto');

const API_KEY = 'f6082C178d6B518B07D47681Ab63CAa6jkTfZZspuRVNJFREHcXGuA8LvaGC23jA';
const API_SECRET = 'D4300da9820578084Ee4cEc588D7C406NcP7MfqdZR1ozHAvDZKpVBPPVbIv1EoP';
const BTC_WALLET = '1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2';

const BTC_PRICE = 89300000; // Rp 89,300,000 per BTC

function createSignature(queryString) {
    return crypto.createHmac('sha256', API_SECRET).update(queryString).digest('hex');
}

function httpRequest(options, postData = null) {
    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch (e) { resolve({ raw: data }); }
            });
        });
        req.on('error', reject);
        if (postData) req.write(postData);
        req.end();
    });
}

async function tryOrder(format, amount) {
    const timestamp = Date.now();
    
    console.log(`\n${'='.repeat(50)}`);
    console.log(`FORMAT ${format}: Testing...`);
    console.log('='.repeat(50));
    
    let path, queryString, body, signature;
    
    if (format === 1) {
        // Format 1: Query string with sorted params
        path = '/openapi/v1/orders';
        const params = {
            symbol: 'BTC_IDR',
            symbolType: 3,
            side: 'BUY',
            type: 1,
            quoteQty: amount,
            timestamp: timestamp
        };
        queryString = Object.keys(params).sort().map(k => `${k}=${params[k]}`).join('&');
        signature = createSignature(queryString);
        body = JSON.stringify({ ...params, signature });
        
    } else if (format === 2) {
        // Format 2: Just timestamp in signature
        path = '/openapi/v1/orders';
        queryString = `timestamp=${timestamp}`;
        signature = createSignature(queryString);
        body = JSON.stringify({
            symbol: 'BTC_IDR',
            symbolType: 3,
            side: 'BUY',
            type: 1,
            quoteQty: amount,
            timestamp: timestamp,
            signature: signature
        });
        
    } else if (format === 3) {
        // Format 3: Different endpoint - /v1/orders
        path = '/v1/orders';
        queryString = `timestamp=${timestamp}`;
        signature = createSignature(queryString);
        body = JSON.stringify({
            symbol: 'BTC_IDR',
            symbolType: 3,
            side: 'BUY',
            type: 1,
            quoteQty: amount,
            timestamp: timestamp,
            signature: signature
        });
        
    } else if (format === 4) {
        // Format 4: Query in URL
        path = '/openapi/v1/orders';
        queryString = `timestamp=${timestamp}&symbol=BTC_IDR&symbolType=3&side=BUY&type=1&quoteQty=${amount}`;
        signature = createSignature(queryString);
        body = null;
    }
    
    console.log('Path:', path);
    console.log('Query:', queryString);
    console.log('Signature:', signature);
    
    const options = {
        hostname: 'www.tokocrypto.com',
        path: path + (body ? '' : `?${queryString}&signature=${signature}`),
        method: body ? 'POST' : 'GET',
        headers: {
            'X-MBX-APIKEY': API_KEY,
            'Content-Type': 'application/json'
        }
    };
    
    if (body) {
        options.headers['Content-Length'] = Buffer.byteLength(body);
    }
    
    try {
        const result = body 
            ? await httpRequest(options, body)
            : await httpRequest(options);
        
        console.log('Result:', JSON.stringify(result).substring(0, 200));
        
        if (result.success || result.code === 0 || result.status === 'success') {
            console.log('\n✅ SUCCESS!');
            return { success: true, result, format };
        }
    } catch (e) {
        console.log('Error:', e.message);
    }
    
    return { success: false, format };
}

async function main() {
    const amount = parseInt(process.argv[2]) || 20000;
    const btcAmount = (amount / BTC_PRICE).toFixed(8);
    
    console.log('╔══════════════════════════════════════════════╗');
    console.log('║    MAHA LAKSHMI - CEO PAYOUT SYSTEM        ║');
    console.log('╚══════════════════════════════════════════════╝');
    console.log(`Amount: Rp ${amount.toLocaleString()}`);
    console.log(`BTC: ${btcAmount}`);
    console.log(`Wallet: ${BTC_WALLET}`);
    
    // Try different formats
    for (let i = 1; i <= 4; i++) {
        const result = await tryOrder(i, amount);
        if (result.success) {
            console.log('\n🎉 CEO PAYOUT COMPLETE!');
            process.exit(0);
        }
    }
    
    console.log('\n❌ All formats failed');
    console.log('Please check API permissions in Tokocrypto dashboard');
}

main();
