const https = require('https');
const crypto = require('crypto');

const API_KEY = 'f6082C178d6B518B07D47681Ab63CAa6jkTfZZspuRVNJFREHcXGuA8LvaGC23jA';
const API_SECRET = 'D4300da9820578084Ee4cEc588D7C406NcP7MfqdZR1ozHAvDZKpVBPPVbIv1EoP';
const BTC_WALLET = '1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2';

function createSignature(queryString) {
    return crypto.createHmac('sha256', API_SECRET).update(queryString).digest('hex');
}

// Test GET endpoint first
function testGET() {
    return new Promise((resolve) => {
        const timestamp = Date.now();
        const query = `timestamp=${timestamp}`;
        const signature = createSignature(query);
        
        console.log('\n--- TESTING GET /account/accountInfo ---');
        console.log('Query: ' + query);
        console.log('Signature: ' + signature);
        
        const options = {
            hostname: 'www.tokocrypto.com',
            path: `/open/v1/account/accountInfo?${query}&signature=${signature}`,
            method: 'GET',
            headers: { 'X-MBX-APIKEY': API_KEY }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                console.log('Status:', res.statusCode);
                console.log('Response:', data.substring(0, 300));
                resolve({ status: res.statusCode, data });
            });
        });
        req.on('error', e => resolve({ error: e.message }));
        req.end();
    });
}

// POST order with JSON body
function postOrder(amount) {
    return new Promise((resolve) => {
        const timestamp = Date.now();
        
        // Build params object
        const params = {
            symbol: 'BTC_IDR',
            symbolType: '3',
            side: 'BUY',
            type: '1',
            quoteQty: amount.toString(),
            timestamp: timestamp.toString()
        };
        
        // Create query string for signature (sorted keys)
        const queryParts = [];
        Object.keys(params).sort().forEach(key => {
            queryParts.push(`${key}=${params[key]}`);
        });
        const queryString = queryParts.join('&');
        const signature = createSignature(queryString);
        
        console.log('\n--- POST /orders ---');
        console.log('Query string: ' + queryString);
        console.log('Signature: ' + signature);
        
        // Send as JSON body
        const body = JSON.stringify({
            symbol: 'BTC_IDR',
            symbolType: 3,
            side: 'BUY',
            type: 1,
            quoteQty: amount.toString(),
            timestamp: timestamp,
            signature: signature
        });
        
        const options = {
            hostname: 'www.tokocrypto.com',
            path: '/open/v1/orders',
            method: 'POST',
            headers: { 
                'X-MBX-APIKEY': API_KEY,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body)
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
        req.write(body);
        req.end();
    });
}

async function main() {
    console.log('==========================================');
    console.log('   MAHA LAKSHMI - CEO PAYOUT');
    console.log('==========================================');
    console.log('Amount: Rp ' + (parseInt(process.argv[2]) || 20000).toLocaleString());
    console.log('Wallet: ' + BTC_WALLET);
    
    try {
        // First test GET to verify signature
        const getResult = await testGET();
        
        // Then try POST
        const amount = parseInt(process.argv[2]) || 20000;
        const postResult = await postOrder(amount);
        
        console.log('\n==========================================');
        if (postResult.success || postResult.code === 0) {
            console.log('   CEO PAYOUT SUCCESS!');
            console.log('   Order ID: ' + postResult.data?.orderId);
        } else {
            console.log('   CEO PAYOUT FAILED');
            console.log('   Error: ' + JSON.stringify(postResult));
        }
        console.log('==========================================');
    } catch (e) {
        console.log('ERROR:', e.message);
    }
}

main();
