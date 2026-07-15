"""
MAHALAKSMI AIOS v1.0 - Revenue Flow E2E Test Suite
Automated testing for digital asset monetization, CEO share routing, and ledger sync.

Test Coverage:
1. Revenue recording from digital products
2. 60% CEO Share routing to BCA 6485086645
3. 40% Operational allocation
4. Finance Ledger synchronization
5. Disbursement flow
"""
import asyncio
import sys
import os
from datetime import datetime
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from app.business.revenue import get_revenue_manager, RevenueStatus
from app.business.finance import get_finance_ledger, TransactionType, Category


class TestResults:
    """Test result tracker."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record(self, name: str, passed: bool, message: str = ""):
        if passed:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {message}")
            print(f"  ❌ {name} - {message}")
    
    def summary(self):
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nErrors:")
            for e in self.errors:
                print(f"  - {e}")
        print("="*60)
        return self.failed == 0


async def test_revenue_60_40_split(results: TestResults):
    """Test 1: Verify 60/40 revenue split."""
    print("\n📊 TEST 1: Revenue 60/40 Split Verification")
    print("-" * 40)
    
    revenue = get_revenue_manager()
    
    # Record test revenue
    test_amount = 1000000  # 1 juta
    transaction = await revenue.record_digital_revenue(
        source="test_digital_products",
        amount=test_amount,
        payment_method="qris"
    )
    
    expected_ceo = test_amount * 0.60
    expected_ops = test_amount * 0.40
    
    # Verify CEO share
    ceo_match = abs(transaction.ceo_share - expected_ceo) < 1
    results.record(
        "CEO Share (60%)",
        ceo_match,
        f"Expected {expected_ceo}, got {transaction.ceo_share}"
    )
    
    # Verify Operational share
    ops_match = abs(transaction.operational_share - expected_ops) < 1
    results.record(
        "Operational Share (40%)",
        ops_match,
        f"Expected {expected_ops}, got {transaction.operational_share}"
    )
    
    # Verify total
    total_match = abs((transaction.ceo_share + transaction.operational_share) - test_amount) < 1
    results.record(
        "Total Allocation",
        total_match,
        f"Sum mismatch: {transaction.ceo_share + transaction.operational_share} != {test_amount}"
    )
    
    # Verify CEO account
    ceo_account = revenue.ceo_bank["account_number"]
    results.record(
        "CEO Account BCA 6485086645",
        ceo_account == "6485086645",
        f"Wrong account: {ceo_account}"
    )
    
    return transaction


async def test_ledger_sync(results: TestResults):
    """Test 2: Verify Finance Ledger synchronization."""
    print("\n📒 TEST 2: Finance Ledger Synchronization")
    print("-" * 40)
    
    finance = get_finance_ledger()
    
    # Record revenue to ledger directly
    test_amount = 2500000
    ledger_entry = finance.add_entry(
        TransactionType.REVENUE,
        Category.DIGITAL_PRODUCTS,
        test_amount,
        "Test revenue for ledger sync",
        {"transaction_id": "TEST-LEDGER-001"}
    )
    
    # Verify entry recorded
    results.record(
        "Ledger Entry Created",
        ledger_entry.entry_id is not None,
        "No entry ID returned"
    )
    
    # Verify balance updated
    balance = finance.get_balance()
    balance_match = balance >= test_amount
    results.record(
        "Balance Updated",
        balance_match,
        f"Balance: {balance}, Test amount: {test_amount}"
    )
    
    # Verify transaction type
    type_match = ledger_entry.transaction_type == TransactionType.REVENUE
    results.record(
        "Transaction Type",
        type_match,
        f"Wrong type: {ledger_entry.transaction_type}"
    )
    
    # Verify category
    cat_match = ledger_entry.category == Category.DIGITAL_PRODUCTS
    results.record(
        "Category Assignment",
        cat_match,
        f"Wrong category: {ledger_entry.category}"
    )
    
    return ledger_entry


async def test_ceo_disbursement(results: TestResults):
    """Test 3: Test CEO disbursement flow."""
    print("\n💸 TEST 3: CEO Disbursement Flow")
    print("-" * 40)
    
    revenue = get_revenue_manager()
    
    # Record revenue first
    test_amount = 5000000  # 5 juta
    transaction = await revenue.record_digital_revenue(
        source="test_services",
        amount=test_amount,
        payment_method="bank_transfer"
    )
    
    # Request CEO disbursement
    ceo_share = transaction.ceo_share
    disbursement = await revenue.request_ceo_disbursement(
        amount=ceo_share,
        method="bank_transfer"
    )
    
    # Verify disbursement created
    results.record(
        "Disbursement Created",
        disbursement.request_id is not None,
        "No request ID returned"
    )
    
    # Verify amount
    amount_match = disbursement.amount == ceo_share
    results.record(
        "Disbursement Amount",
        amount_match,
        f"Expected {ceo_share}, got {disbursement.amount}"
    )
    
    # Verify status
    status_match = disbursement.status == "completed"
    results.record(
        "Disbursement Status",
        status_match,
        f"Wrong status: {disbursement.status}"
    )
    
    # Verify transaction ID generated
    results.record(
        "Transaction ID Generated",
        disbursement.transaction_id is not None,
        "No transaction ID"
    )
    
    # Verify CEO account
    account_match = disbursement.recipient_account == "6485086645"
    results.record(
        "CEO Account Match",
        account_match,
        f"Wrong account: {disbursement.recipient_account}"
    )
    
    return disbursement


async def test_multiple_revenue_streams(results: TestResults):
    """Test 4: Test multiple revenue streams."""
    print("\n📈 TEST 4: Multiple Revenue Streams")
    print("-" * 40)
    
    revenue = get_revenue_manager()
    finance = get_finance_ledger()
    
    # Get initial state
    initial_summary = revenue.get_summary()
    initial_count = initial_summary["total_transactions"]
    
    # Test different sources
    streams = [
        {"source": "test_digital", "amount": 10000000, "method": "qris"},
        {"source": "test_services", "amount": 5000000, "method": "bank_transfer"},
        {"source": "test_consulting", "amount": 2500000, "method": "ewallet"},
    ]
    
    total_expected = sum(s["amount"] for s in streams)
    
    # Record all streams
    for stream in streams:
        txn = await revenue.record_digital_revenue(
            source=stream["source"],
            amount=stream["amount"],
            payment_method=stream["method"]
        )
    
    # Verify transactions added
    summary = revenue.get_summary()
    new_count = summary["total_transactions"] - initial_count
    count_match = new_count == len(streams)
    results.record(
        "Transactions Added",
        count_match,
        f"Expected {len(streams)}, got {new_count}"
    )
    
    # Verify revenue increased by expected amount
    expected_total = initial_summary["total_revenue"] + total_expected
    total_match = abs(summary["total_revenue"] - expected_total) < 1
    results.record(
        "Revenue Increased Correctly",
        total_match,
        f"Expected {expected_total}, got {summary['total_revenue']}"
    )
    
    # Verify CEO share is 60% of total
    ceo_percentage = summary["allocation"]["ceo_percentage"]
    results.record(
        "CEO Percentage (60%)",
        abs(ceo_percentage - 60.0) < 0.1,
        f"Wrong percentage: {ceo_percentage}%"
    )
    
    return summary


async def test_clearing_house(results: TestResults):
    """Test 5: Test clearing house settlement."""
    print("\n🏦 TEST 5: Clearing House Settlement")
    print("-" * 40)
    
    revenue = get_revenue_manager()
    
    # Record revenue
    test_amount = 10000000  # 10 juta
    transaction = await revenue.record_digital_revenue(
        source="test_clearing",
        amount=test_amount,
        payment_method="qris"
    )
    
    # Verify transaction completed
    status_match = transaction.status == RevenueStatus.COMPLETED
    results.record(
        "Transaction Completed",
        status_match,
        f"Wrong status: {transaction.status}"
    )
    
    # Verify clearing reference
    clearing_match = transaction.clearing_reference is not None
    results.record(
        "Clearing Reference Generated",
        clearing_match,
        "No clearing reference"
    )
    
    # Verify cleared timestamp
    cleared_match = transaction.cleared_at is not None
    results.record(
        "Clearing Timestamp Set",
        cleared_match,
        "No cleared timestamp"
    )
    
    # Verify settlement report
    report = revenue.clearing_house.get_settlement_report()
    settled_match = report["total_settled"] > 0
    results.record(
        "Settlement Report",
        settled_match,
        f"No settlements: {report}"
    )
    
    return transaction


async def test_finance_summary(results: TestResults):
    """Test 6: Test finance summary report."""
    print("\n📋 TEST 6: Finance Summary Report")
    print("-" * 40)
    
    finance = get_finance_ledger()
    
    # Add test entries
    finance.add_entry(
        TransactionType.REVENUE,
        Category.DIGITAL_PRODUCTS,
        50000000,
        "Test revenue 1"
    )
    finance.add_entry(
        TransactionType.EXPENSE,
        Category.OPERATIONS,
        10000000,
        "Test expense 1"
    )
    
    # Get summary
    summary = finance.get_summary()
    
    # Verify income recorded
    income_match = summary["income"]["total"] >= 50000000
    results.record(
        "Income Recorded",
        income_match,
        f"Income: {summary['income']['total']}"
    )
    
    # Verify expense recorded
    expense_match = summary["expenses"]["total"] >= 10000000
    results.record(
        "Expense Recorded",
        expense_match,
        f"Expense: {summary['expenses']['total']}"
    )
    
    # Verify profit calculated
    profit_match = summary["profit"] >= 40000000
    results.record(
        "Profit Calculated",
        profit_match,
        f"Profit: {summary['profit']}"
    )
    
    # Verify profit margin
    margin_match = summary["profit_margin"] > 0
    results.record(
        "Profit Margin Calculated",
        margin_match,
        f"Margin: {summary['profit_margin']}%"
    )
    
    return summary


async def run_all_tests():
    """Run all revenue flow tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.0 - Revenue Flow E2E Tests")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    results = TestResults()
    
    # Run all tests
    try:
        await test_revenue_60_40_split(results)
        await test_ledger_sync(results)
        await test_ceo_disbursement(results)
        await test_multiple_revenue_streams(results)
        await test_clearing_house(results)
        await test_finance_summary(results)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        results.failed += 1
        results.errors.append(str(e))
    
    # Print summary
    success = results.summary()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED - Revenue Flow Operational!")
    else:
        print("⚠️ SOME TESTS FAILED - Review above")
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
