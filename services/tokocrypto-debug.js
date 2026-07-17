const https = require('https');
const crypto = require('crypto');

const API_KEY = 'f6082C178d6B518B07D47681Ab63CAa6jkTfZZspuRVNJFREHcXGuA8LvaGC23jA';
const API_SECRET = 'D4300da9820578084Ee4cEc588D7C406NcP7MfqdZR1ozHAvDZKpVBPPVbIv1EoP';
const BTC_WALLET = '1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2';

console.log('==========================================');
console.log('   MAHA LAKSHMI - CEO PAYOUT DEBUG');
console.log('==========================================');
console.log('API Key length:', API_KEY.length);
console.log('API Secret length:', API_SECRET.length);
console.log('');

// Test 1: GET account info
function testGET(path) {
    return new Promise((resolve) => {
        const timestamp = Date.now();
        const queryString = `timestamp=${timestamp}`;
        const signature = crypto.createHmac('sha256', API_SECRET).update(queryString).digest('hex');
        
        console.log(`\n--- GET ${path} ---`);
        console.log('Query string:', queryString);
        console.log('Signature:', signature);
        
        const options = {
            hostname: 'www.tokocrypto.com',
            path: `/openapi/v1${path}?${queryString}&signature=${signature}`,
            method: 'GET',
            headers: { 'X-MBX-APIKEY': API_KEY }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                console.log('Status:', res.statusCode);
                console.log('Response:', data.substring(0, 300));
                resolve(JSON.parse(data));
            });
        });
        req.on('error', e => resolve({ error: e.message }));
        req.end();
    });
}

// Test 2: POST order with different formats
async function testPOST(amount) {
    const timestamp = Date.now();
    
    // Format 1: Signature based on sorted params
    const params = {
        timestamp: timestamp,
        symbol: 'BTC_IDR',
        symbolType: '3', 
        side: 'BUY',
        type: '1',
        quoteQty: amount.toString()
    };
    
    // Sort keys and build query string
    const sortedKeys = Object.keys(params).sort();
    let queryParts = [];
    for (let key of sortedKeys) {
        queryParts.push(`${key}=${params[key]}`);
    }
    const queryString1 = queryParts.join('&');
    const signature1 = crypto.createHmac('sha256', API_SECRET).update(queryString1).digest('hex');
    
    console.log('\n--- POST /orders (Format 1 - sorted) ---');
    console.log('Query string:', queryString1);
    console.log('Signature:', signature1);
    
    // Try with query in URL
    return new Promise((resolve) => {
        const postData = JSON.stringify({
            symbol: 'BTC_IDR',
            symbolType: 3,
            side: 'BUY',
            type: 1,
            quoteQty: amount.toString(),
            timestamp: timestamp,
            signature: signature1
        });
        
        const options = {
            hostname: 'www.tokocrypto.com',
            path: '/openapi/v1/orders',
            method: 'POST',
            headers: { 
                'X-MBX-APIKEY': API_KEY,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                console.log('Status:', res.statusCode);
                console.log('Response:', data.substring(0, 500));
                try { resolve(JSON.parse(data)); }
                catch (e) { resolve({ raw: data }); }
            });
        });
        req.on('error', e => resolve({ error: e.message }));
        req.write(postData);
        req.end();
    });
}

async function main() {
    // First test GET to see if API key works
    const accountResult = await testGET('/account/accountInfo');
    
    if (accountResult.error || (accountResult.code && accountResult.code !== 0)) {
        console.log('\n❌ GET request failed - check API key');
        console.log('Result:', JSON.stringify(accountResult));
        return;
    }
    
    console.log('\n✅ GET request successful!');
    
    // Then test POST
    const orderResult = await testPOST(20000);
    
    console.log('\n==========================================');
    console.log('   RESULT');
    console.log('==========================================');
    if (orderResult.success || orderResult.code === 0) {
        console.log('   ORDER SUCCESS!');
        console.log('   Order ID:', orderResult.data?.orderId);
    } else {
        console.log('   ORDER FAILED');
        console.log('   Error:', JSON.stringify(orderResult));
    }
}

main();
