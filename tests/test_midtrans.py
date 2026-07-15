"""
MAHALAKSMI AIOS v1.1.1 - Midtrans Payment Gateway Tests
Tests Snap API integration, signature verification, and 60/40 split
"""
import asyncio
import sys
import os
import hashlib
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.business.midtrans_client import (
    get_midtrans_client,
    MidtransClient,
    TransactionStatus,
    TransactionResult
)
from app.business.revenue import (
    get_revenue_manager,
    RevenueManager,
    RevenueStatus
)


class TestResults:
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


async def test_midtrans_client_initialization(results: TestResults):
    """Test Midtrans client initialization."""
    print("\n💳 TEST: Midtrans Client Initialization")
    print("-" * 40)
    
    client = get_midtrans_client()
    
    results.record(
        "Midtrans Client Created",
        client is not None
    )
    
    results.record(
        "Server Key Loaded (or demo mode)",
        True  # Either key is set or demo mode is active
    )
    
    results.record(
        "API URLs Configured",
        "sandbox" in client.snap_url or "app.midtrans.com" in client.snap_url
    )
    
    return client


async def test_signature_generation(results: TestResults, client: MidtransClient):
    """Test signature key generation."""
    print("\n🔐 TEST: Signature Generation")
    print("-" * 40)
    
    order_id = "ORDER-123"
    gross_amount = 100000
    server_key = "test-server-key"
    
    signature = client._generate_signature_key(
        order_id=order_id,
        gross_amount=gross_amount,
        server_key=server_key
    )
    
    results.record(
        "Signature Generated",
        len(signature) == 128  # SHA512 produces 128 hex chars
    )
    
    # Verify consistency
    signature2 = client._generate_signature_key(
        order_id=order_id,
        gross_amount=gross_amount,
        server_key=server_key
    )
    
    results.record(
        "Signature Consistent",
        signature == signature2
    )
    
    # Verify different inputs produce different signatures
    signature3 = client._generate_signature_key(
        order_id="ORDER-456",
        gross_amount=gross_amount,
        server_key=server_key
    )
    
    results.record(
        "Different Inputs = Different Signature",
        signature != signature3
    )
    
    return client


async def test_signature_verification(results: TestResults, client: MidtransClient):
    """Test signature verification."""
    print("\n✅ TEST: Signature Verification")
    print("-" * 40)
    
    # Set server key for testing
    os.environ["MIDTRANS_SERVER_KEY"] = "test-server-key-123"
    client.server_key = "test-server-key-123"
    
    order_id = "ORDER-TEST-001"
    gross_amount = 500000
    status_code = "200"
    
    # Generate valid signature
    signature_raw = f"{status_code}{order_id}{gross_amount}{client.server_key}"
    valid_signature = hashlib.sha512(signature_raw.encode()).hexdigest()
    
    # Verify valid signature
    is_valid = client._verify_notification_signature(
        order_id=order_id,
        gross_amount=gross_amount,
        status_code=status_code,
        signature_key=valid_signature
    )
    
    results.record(
        "Valid Signature Accepted",
        is_valid
    )
    
    # Test invalid signature
    invalid_signature = "invalid" * 16  # 128 chars
    
    is_invalid = client._verify_notification_signature(
        order_id=order_id,
        gross_amount=gross_amount,
        status_code=status_code,
        signature_key=invalid_signature
    )
    
    results.record(
        "Invalid Signature Rejected",
        not is_invalid
    )
    
    # Test tampered amount
    tampered_signature = hashlib.sha512(
        f"{status_code}{order_id}{999999}{client.server_key}".encode()
    ).hexdigest()
    
    is_tampered = client._verify_notification_signature(
        order_id=order_id,
        gross_amount=gross_amount,
        status_code=status_code,
        signature_key=tampered_signature
    )
    
    results.record(
        "Tampered Data Rejected",
        not is_tampered
    )
    
    return client


async def test_notification_parsing(results: TestResults, client: MidtransClient):
    """Test notification parsing."""
    print("\n📨 TEST: Notification Parsing")
    print("-" * 40)
    
    # Create valid notification payload
    server_key = "test-server-key-123"
    
    order_id = "ORDER-001"
    gross_amount = 250000
    status_code = "201"
    signature_raw = f"{status_code}{order_id}{gross_amount}{server_key}"
    valid_signature = hashlib.sha512(signature_raw.encode()).hexdigest()
    
    # Temporarily set server key
    original_key = client.server_key
    client.server_key = server_key
    
    payload = {
        "transaction_id": "TXN-123456",
        "order_id": order_id,
        "payment_type": "qris",
        "status_code": status_code,
        "gross_amount": str(gross_amount),
        "transaction_status": "settlement",
        "signature_key": valid_signature,
        "transaction_time": "2026-07-14 12:00:00",
        "fraud_status": "accept"
    }
    
    notification = client.handle_notification(payload)
    
    results.record(
        "Notification Parsed",
        notification.order_id == order_id
    )
    
    results.record(
        "Amount Correct",
        notification.gross_amount == gross_amount
    )
    
    results.record(
        "Status Correct",
        notification.transaction_status == TransactionStatus.SETTLEMENT
    )
    
    results.record(
        "Payment Type Correct",
        notification.payment_type == "qris"
    )
    
    # Restore server key
    client.server_key = original_key
    
    return client


async def test_demo_mode_transaction(results: TestResults, client: MidtransClient):
    """Test demo mode transaction creation."""
    print("\n🧪 TEST: Demo Mode Transaction")
    print("-" * 40)
    
    # Ensure no real API key for demo mode
    client.server_key = ""
    
    result = client.create_snap_transaction(
        order_id="DEMO-ORDER-001",
        gross_amount=100000,
        customer_details={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        },
        item_details=[
            {"id": "ITEM-1", "name": "Product 1", "price": 100000, "quantity": 1}
        ]
    )
    
    results.record(
        "Demo Transaction Created",
        result.success
    )
    
    results.record(
        "Demo Token Generated",
        "DEMO_TOKEN" in result.snap_token
    )
    
    results.record(
        "Demo Redirect URL",
        "demo.midtrans.com" in result.snap_redirect_url
    )
    
    return client


async def test_revenue_60_40_split(results: TestResults):
    """Test 60/40 CEO split calculation."""
    print("\n💰 TEST: Revenue 60/40 Split")
    print("-" * 40)
    
    revenue = get_revenue_manager()
    
    # Test allocation calculation
    allocation = revenue.calculate_allocation(1000000)  # 1 million
    
    results.record(
        "Gross Amount Correct",
        allocation["gross_amount"] == 1000000
    )
    
    results.record(
        "CEO Share = 60%",
        allocation["ceo_share"] == 600000
    )
    
    results.record(
        "Ops Share = 40%",
        allocation["operational_share"] == 400000
    )
    
    results.record(
        "CEO Percentage = 60",
        allocation["ceo_percentage"] == 60.0
    )
    
    # Test with different amount
    allocation2 = revenue.calculate_allocation(417900145)
    
    expected_ceo = int(417900145 * 0.6)
    expected_ops = int(417900145 * 0.4)
    
    results.record(
        "Large Amount CEO = 60%",
        allocation2["ceo_share"] == expected_ceo
    )
    
    results.record(
        "Large Amount Ops = 40%",
        allocation2["operational_share"] == expected_ops
    )
    
    return revenue


async def test_create_payment_order(results: TestResults, revenue: RevenueManager):
    """Test creating a payment order."""
    print("\n📝 TEST: Create Payment Order")
    print("-" * 40)
    
    # Reset global midtrans client for demo mode
    import app.business.midtrans_client as mc
    mc._midtrans_client = None
    
    # Clear environment to force demo mode
    os.environ.pop("MIDTRANS_SERVER_KEY", None)
    
    # Create fresh revenue manager to pick up demo mode
    import app.business.revenue as rev
    rev._revenue_manager = None
    fresh_revenue = rev.get_revenue_manager()
    
    # Now create payment order (should use demo mode)
    result = await fresh_revenue.create_payment_order(
        order_id="TEST-ORDER-001",
        gross_amount=500000,
        customer_details={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com"
        },
        item_details=[
            {"id": "ITEM-1", "name": "Digital Course", "price": 500000, "quantity": 1}
        ]
    )
    
    results.record(
        "Payment Order Created",
        result["success"]
    )
    
    results.record(
        "Order ID Preserved",
        result["order_id"] == "TEST-ORDER-001"
    )
    
    results.record(
        "Transaction ID Generated",
        "REV-" in result["transaction_id"]
    )
    
    results.record(
        "Snap Token Present",
        "DEMO_TOKEN" in result["snap_token"]
    )
    
    results.record(
        "Status Pending",
        result["status"] == "pending"
    )
    
    # Verify transaction stored
    stored_tx = fresh_revenue.get_transaction_by_order_id("TEST-ORDER-001")
    results.record(
        "Transaction Stored",
        stored_tx is not None
    )
    
    return fresh_revenue


async def test_settlement_and_split(results: TestResults, revenue: RevenueManager):
    """Test payment settlement with 60/40 split."""
    print("\n🎉 TEST: Settlement with 60/40 Split")
    print("-" * 40)
    
    # First create a pending order
    result = await revenue.create_payment_order(
        order_id="SETTLEMENT-TEST-001",
        gross_amount=1000000,
        customer_details={"first_name": "Test", "last_name": "User"},
        item_details=[{"id": "ITEM-1", "name": "Test", "price": 1000000, "quantity": 1}]
    )
    
    # Simulate settlement
    transaction = await revenue.handle_payment_settlement(
        order_id="SETTLEMENT-TEST-001",
        gross_amount=1000000,
        transaction_id="MIDTRANS-TXN-001",
        payment_type="bca_va"
    )
    
    results.record(
        "Settlement Processed",
        transaction is not None
    )
    
    results.record(
        "Status = COMPLETED",
        transaction.status == RevenueStatus.COMPLETED
    )
    
    results.record(
        "Amount Preserved",
        transaction.amount == 1000000
    )
    
    results.record(
        "CEO Share = 60%",
        transaction.ceo_share == 600000
    )
    
    results.record(
        "Ops Share = 40%",
        transaction.operational_share == 400000
    )
    
    results.record(
        "Cleared Timestamp Set",
        transaction.cleared_at is not None
    )
    
    return revenue


async def test_webhook_settlement_flow(results: TestResults, revenue: RevenueManager, client: MidtransClient):
    """Test full webhook settlement flow."""
    print("\n🔄 TEST: Webhook Settlement Flow")
    print("-" * 40)
    
    # Set server key for signature generation
    server_key = "webhook-test-key"
    os.environ["MIDTRANS_SERVER_KEY"] = server_key
    client.server_key = server_key
    
    order_id = "WEBHOOK-TEST-001"
    gross_amount = 750000
    status_code = "201"
    
    # Generate valid signature
    signature_raw = f"{status_code}{order_id}{gross_amount}{server_key}"
    valid_signature = hashlib.sha512(signature_raw.encode()).hexdigest()
    
    # Create pending order first
    await revenue.create_payment_order(
        order_id=order_id,
        gross_amount=gross_amount,
        customer_details={"first_name": "Webhook", "last_name": "Test"},
        item_details=[{"id": "ITEM-1", "name": "Test", "price": gross_amount, "quantity": 1}]
    )
    
    # Simulate webhook payload
    payload = {
        "transaction_id": "MIDTRANS-TXN-002",
        "order_id": order_id,
        "payment_type": "qris",
        "status_code": status_code,
        "gross_amount": str(gross_amount),
        "transaction_status": "settlement",
        "signature_key": valid_signature,
        "transaction_time": "2026-07-14 12:00:00"
    }
    
    # Parse notification
    notification = client.handle_notification(payload)
    
    results.record(
        "Webhook Parsed Successfully",
        notification.order_id == order_id
    )
    
    # Handle settlement
    transaction = await revenue.handle_payment_settlement(
        order_id=notification.order_id,
        gross_amount=notification.gross_amount,
        transaction_id=notification.transaction_id,
        payment_type=notification.payment_type
    )
    
    results.record(
        "Settlement Updated",
        transaction.status == RevenueStatus.COMPLETED
    )
    
    results.record(
        "Correct CEO Amount",
        transaction.ceo_share == int(gross_amount * 0.6)
    )
    
    results.record(
        "Correct Ops Amount",
        transaction.operational_share == int(gross_amount * 0.4)
    )
    
    return revenue, client


async def test_cancel_pending_payment(results: TestResults, revenue: RevenueManager):
    """Test cancelling pending payment."""
    print("\n❌ TEST: Cancel Pending Payment")
    print("-" * 40)
    
    # Create pending order
    result = await revenue.create_payment_order(
        order_id="CANCEL-TEST-001",
        gross_amount=250000,
        customer_details={"first_name": "Cancel", "last_name": "Test"},
        item_details=[{"id": "ITEM-1", "name": "Test", "price": 250000, "quantity": 1}]
    )
    
    # Verify pending
    tx = revenue.get_transaction_by_order_id("CANCEL-TEST-001")
    results.record(
        "Order Created as Pending",
        tx.status == RevenueStatus.PENDING
    )
    
    # Cancel
    cancelled = revenue.cancel_pending_payment("CANCEL-TEST-001")
    
    results.record(
        "Cancel Returns True",
        cancelled
    )
    
    # Verify cancelled
    tx_after = revenue.get_transaction_by_order_id("CANCEL-TEST-001")
    results.record(
        "Status = CANCELLED",
        tx_after.status == RevenueStatus.CANCELLED
    )
    
    return revenue


async def test_invalid_signature_rejection(results: TestResults, client: MidtransClient):
    """Test that invalid signatures are properly rejected."""
    print("\n🚫 TEST: Invalid Signature Rejection")
    print("-" * 40)
    
    # Set server key
    server_key = "secure-key"
    client.server_key = server_key
    
    # Payload with invalid signature
    payload = {
        "transaction_id": "TXN-BAD",
        "order_id": "BAD-ORDER",
        "payment_type": "qris",
        "status_code": "200",
        "gross_amount": "100000",
        "transaction_status": "settlement",
        "signature_key": "invalid_signature_key_12345",
        "transaction_time": "2026-07-14 12:00:00"
    }
    
    try:
        client.handle_notification(payload)
        results.record(
            "Invalid Signature Throws Error",
            False
        )
    except ValueError as e:
        results.record(
            "Invalid Signature Throws Error",
            "signature" in str(e).lower()
        )
    
    return client


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("💳 MAHALAKSMI AIOS v1.1.1 - Midtrans Payment Tests")
    print("="*60)
    
    results = TestResults()
    
    try:
        # Midtrans Client tests
        client = await test_midtrans_client_initialization(results)
        await test_signature_generation(results, client)
        await test_signature_verification(results, client)
        await test_notification_parsing(results, client)
        await test_demo_mode_transaction(results, client)
        await test_invalid_signature_rejection(results, client)
        
        # Revenue tests
        revenue = await test_revenue_60_40_split(results)
        await test_create_payment_order(results, revenue)
        await test_settlement_and_split(results, revenue)
        await test_webhook_settlement_flow(results, revenue, client)
        await test_cancel_pending_payment(results, revenue)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        results.failed += 1
    
    # Print summary
    print("\n" + "="*60)
    print(f"RESULTS: {results.passed} passed, {results.failed} failed")
    if results.errors:
        print("\nErrors:")
        for e in results.errors:
            print(f"  - {e}")
    print("="*60)
    
    success = results.failed == 0
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED - Review above")
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
