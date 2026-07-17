const https = require('https');
const crypto = require('crypto');

const API_KEY = 'f6082C178d6B518B07D47681Ab63CAa6jkTfZZspuRVNJFREHcXGuA8LvaGC23jA';
const API_SECRET = 'D4300da9820578084Ee4cEc588D7C406NcP7MfqdZR1ozHAvDZKpVBPPVbIv1EoP';
const BTC_WALLET = '1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2';

function createSignature(queryString) {
    return crypto.createHmac('sha256', API_SECRET).update(queryString).digest('hex');
}

async function makeRequest(method, path, params = {}) {
    const timestamp = Date.now();
    
    // Build query string
    const queryParams = { ...params, timestamp };
    const queryString = Object.keys(queryParams).sort()
        .map(k => `${k}=${queryParams[k]}`)
        .join('&');
    
    const signature = createSignature(queryString);
    const fullPath = `${path}?${queryString}&signature=${signature}`;
    
    console.log(`\n--- Request ---`);
    console.log(`Method: ${method}`);
    console.log(`Path: ${fullPath}`);
    
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'www.tokocrypto.com',
            path: fullPath,
            method: method,
            headers: {
                'X-MBX-APIKEY': API_KEY,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                console.log(`Status: ${res.statusCode}`);
                if (data.startsWith('<!') || data.startsWith('<html')) {
                    console.log('Response: HTML (CloudFront blocked)');
                    resolve({ html: true, status: res.statusCode });
                } else {
                    console.log(`Response: ${data.substring(0, 300)}`);
                    try { resolve(JSON.parse(data)); }
                    catch (e) { resolve({ raw: data }); }
                }
            });
        });
        
        req.on('error', e => resolve({ error: e.message }));
        req.end();
    });
}

async function main() {
    const amount = parseInt(process.argv[2]) || 20000;
    
    console.log('╔════════════════════════════════════════╗');
    console.log('║   MAHA LAKSHMI - CEO PAYOUT          ║');
    console.log('╚════════════════════════════════════════╝');
    console.log(`Amount: Rp ${amount.toLocaleString()}`);
    
    // Test GET first
    console.log('\n[1] Testing GET /openapi/account/quote');
    const getResult = await makeRequest('GET', '/openapi/account/quote');
    
    if (getResult.html || getResult.error) {
        console.log('❌ GET blocked - trying alternative...');
        
        // Try without /openapi prefix
        console.log('\n[2] Testing GET /v1/account/quote');
        const altResult = await makeRequest('GET', '/v1/account/quote');
        
        if (altResult.code === -1022 || altResult.code === -2014) {
            console.log('❌ Signature required but auth failed');
        }
    }
    
    // Try POST with order
    console.log('\n[3] Testing POST /v1/orders');
    const orderResult = await makeRequest('POST', '/v1/orders', {
        symbol: 'BTC_IDR',
        side: 'BUY',
        type: 'LIMIT',
        price: '89300000',
        quantity: '0.00022396'
    });
    
    console.log('\n[4] Testing POST /openapi/v1/orders (browser UA)');
    const orderResult2 = await makeRequest('POST', '/openapi/v1/orders', {
        symbol: 'BTC_IDR',
        side: 'BUY',
        type: 1,
        symbolType: 3,
        quoteQty: amount.toString()
    });
    
    console.log('\n========================================');
    console.log('RESULT SUMMARY');
    console.log('========================================');
    console.log('API requires browser-like requests.');
    console.log('Manual execution via Tokocrypto website recommended.');
}

main();
