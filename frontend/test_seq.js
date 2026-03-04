const axios = require('axios');

async function testFrontendSequence() {
    try {
        const res = await axios.post('http://localhost:8001/auth/register', {
            username: 'biz_script_102', password: 'Password1!', email: 'bizscript12@example.com',
            full_name: 'Test Business Seq', account_type: 'business'
        });
        const token = res.data.data.token;
        const config = { headers: { Authorization: "Bearer " + token } };
        console.log("Registered.");

        const taxRes = await axios.put('http://localhost:8001/tax', {
            regime: 'new', business_revenue: 1200000, business_expenses: 480000, cogs: 0
        }, config);
        console.log("Tax updated:", taxRes.status);

        const invRes = await axios.post('http://localhost:8001/business/inventory', {
            item_name: 'Total Inventory', quantity: 1, unit_cost: 1000
        }, config);
        console.log("Inventory updated:", invRes.status);

        const recRes = await axios.post('http://localhost:8001/business/receivables', {
            customer_name: 'Total Receivables', invoice_amount: 2000, due_date: '2026-04-01'
        }, config);
        console.log("Receivables updated:", recRes.status);
        
        const payRes = await axios.post('http://localhost:8001/business/payables', {
            vendor_name: 'Total Payables', bill_amount: 3000, due_date: '2026-04-01'
        }, config);
        console.log("Payables updated:", payRes.status);

        const setupRes = await axios.post('http://localhost:8001/auth/complete-setup', {}, config);
        console.log("Setup complete:", setupRes.status);

    } catch (err) {
        if (err.response) {
            console.error(err.response.status, err.response.data);
        } else {
            console.error(err);
        }
    }
}
testFrontendSequence();
