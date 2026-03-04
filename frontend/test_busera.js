const axios = require('axios');

async function reproduceBug() {
    try {
        const res = await axios.post('http://localhost:8000/auth/register', {
            username: 'busera_test1', password: 'Password1!', email: 'busera_test1@example.com',
            full_name: 'Busera Test', account_type: 'business'
        });
        const token = res.data.data.token;
        const config = { headers: { Authorization: "Bearer " + token } };
        
        console.log("Registered:", res.status);

        const taxRes = await axios.put('http://localhost:8000/tax', {
            regime: 'new', business_revenue: 1200000, business_expenses: 480000, cogs: 0
        }, config);
        console.log("Tax updated:", taxRes.status);
        
        const bankRes = await axios.post('http://localhost:8000/accounts', {
            bank_name: 'Test Bank', account_type: 'savings', balance: 200000, mode: 'business'
        }, config);
        console.log("Bank updated:", bankRes.status);

        const ccRes = await axios.post('http://localhost:8000/loans/credit-cards', {
            card_name: 'Test CC', credit_limit: 50000, credit_used: 10000, emi: 0
        }, config);
        console.log("CC updated:", ccRes.status);

        const loanRes = await axios.post('http://localhost:8000/loans', {
            loan_name: 'Test Loan', loan_type: 'business', outstanding: 500000, emi: 15000, interest_rate: 10, mode: 'business'
        }, config);
        console.log("Loan updated:", loanRes.status);

        const invRes = await axios.post('http://localhost:8000/investments', {
            type: 'fd', value: 100000, interest_rate: 6, mode: 'business'
        }, config);
        console.log("Investments updated:", invRes.status);
        
        const payRes = await axios.post('http://localhost:8000/business/payables', {
            vendor_name: 'Total Payables', bill_amount: 3000, due_date: '2026-04-01'
        }, config);
        console.log("Payables updated:", payRes.status);

    } catch (err) {
        if (err.response) {
            console.error("ERROR from API:", err.response.status, err.response.data);
        } else {
            console.error("UNKNOWN ERROR:", err.message);
        }
    }
}
reproduceBug();
