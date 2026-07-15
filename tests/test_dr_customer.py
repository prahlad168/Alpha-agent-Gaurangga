"""
MAHALAKSMI AIOS v1.0.9 - Disaster Recovery & Customer Center Tests
Tests failover sequences and CLV calculations
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.enterprise.disaster_recovery import (
    get_disaster_recovery_engine,
    DisasterRecoveryEngine,
    SystemState,
    HealthStatus
)
from app.business.customer import (
    get_customer_center,
    CustomerCenter,
    CustomerStatus,
    TicketPriority,
    TicketStatus
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


async def test_dr_engine_initialization(results: TestResults):
    """Test disaster recovery engine initialization."""
    print("\n🔒 TEST: Disaster Recovery Engine Initialization")
    print("-" * 40)
    
    dr = get_disaster_recovery_engine()
    
    results.record(
        "DR Engine Created",
        dr is not None
    )
    
    results.record(
        "Database Initialized",
        dr.db is not None
    )
    
    results.record(
        "Components Defined",
        len(dr.components) > 0
    )
    
    return dr


async def test_system_state_management(results: TestResults, dr: DisasterRecoveryEngine):
    """Test system state management."""
    print("\n⚡ TEST: System State Management")
    print("-" * 40)
    
    # Get initial state
    state = dr.get_system_state()
    results.record(
        "Initial State Retrieved",
        state is not None
    )
    
    # Change state
    dr.db.set_system_state(SystemState.DEGRADED)
    new_state = dr.get_system_state()
    results.record(
        "State Change Works",
        new_state == SystemState.DEGRADED
    )
    
    # Reset to normal
    dr.db.set_system_state(SystemState.NORMAL)
    
    return dr


async def test_health_check(results: TestResults, dr: DisasterRecoveryEngine):
    """Test health check functionality."""
    print("\n🏥 TEST: Health Check")
    print("-" * 40)
    
    # Perform health check
    health = dr.perform_health_check()
    
    results.record(
        "Health Check Returns Result",
        health is not None
    )
    
    results.record(
        "Has Overall Status",
        "overall_healthy" in health
    )
    
    results.record(
        "Has Components",
        "components" in health
    )
    
    results.record(
        "Has System State",
        "system_state" in health
    )
    
    return dr


async def test_failover_sequence(results: TestResults, dr: DisasterRecoveryEngine):
    """Test failover sequence."""
    print("\n🔄 TEST: Failover Sequence")
    print("-" * 40)
    
    # Ensure normal state first
    dr.db.set_system_state(SystemState.NORMAL)
    
    # Initiate failover
    record = dr.initiate_failover("Test failover")
    
    results.record(
        "Failover Record Created",
        record.failover_id.startswith("FO-")
    )
    
    results.record(
        "Previous State Captured",
        record.previous_state == SystemState.NORMAL
    )
    
    results.record(
        "New State Set",
        record.new_state in [SystemState.READ_ONLY, SystemState.STANDBY, SystemState.OFFLINE]
    )
    
    results.record(
        "Status Recorded",
        record.status.value == "in_progress"
    )
    
    return dr


async def test_recovery_plan(results: TestResults, dr: DisasterRecoveryEngine):
    """Test recovery plan execution."""
    print("\n🔧 TEST: Recovery Plan")
    print("-" * 40)
    
    # Set to degraded state for recovery
    dr.db.set_system_state(SystemState.DEGRADED)
    
    # Execute recovery
    plan = dr.execute_recovery()
    
    results.record(
        "Recovery Plan Created",
        plan.recovery_id.startswith("REC-")
    )
    
    results.record(
        "Has Recovery Steps",
        len(plan.steps) > 0
    )
    
    results.record(
        "Has Estimated Duration",
        plan.estimated_duration_minutes > 0
    )
    
    # Complete recovery
    success = dr.complete_recovery()
    results.record(
        "Recovery Completion",
        success
    )
    
    # Verify state
    final_state = dr.get_system_state()
    results.record(
        "State Returns to Normal",
        final_state == SystemState.NORMAL
    )
    
    return dr


async def test_customer_center_initialization(results: TestResults):
    """Test customer center initialization."""
    print("\n👥 TEST: Customer Center Initialization")
    print("-" * 40)
    
    customer = get_customer_center()
    
    results.record(
        "Customer Center Created",
        customer is not None
    )
    
    results.record(
        "Database Initialized",
        customer.db is not None
    )
    
    return customer


async def test_customer_creation(results: TestResults, customer: CustomerCenter):
    """Test customer creation."""
    print("\n🆕 TEST: Customer Creation")
    print("-" * 40)
    
    c = customer.create_customer(
        name="John Doe",
        email="john@example.com",
        phone="08123456789"
    )
    
    results.record(
        "Customer Created",
        c.customer_id.startswith("CUST-")
    )
    
    results.record(
        "Customer Name Set",
        c.name == "John Doe"
    )
    
    results.record(
        "Customer Email Set",
        c.email == "john@example.com"
    )
    
    results.record(
        "Initial Status Prospect",
        c.status == CustomerStatus.PROSPECT
    )
    
    return customer, c


async def test_support_ticket(results: TestResults, customer: CustomerCenter, c):
    """Test support ticket creation."""
    print("\n🎫 TEST: Support Ticket")
    print("-" * 40)
    
    ticket = customer.create_ticket(
        customer_id=c.customer_id,
        subject="Need help with purchase",
        description="I cannot complete my checkout",
        priority=TicketPriority.HIGH
    )
    
    results.record(
        "Ticket Created",
        ticket.ticket_id.startswith("TICKET-")
    )
    
    results.record(
        "Ticket Linked to Customer",
        ticket.customer_id == c.customer_id
    )
    
    results.record(
        "Priority Set",
        ticket.priority == TicketPriority.HIGH
    )
    
    results.record(
        "Initial Status Open",
        ticket.status == TicketStatus.OPEN
    )
    
    # Update status
    success = customer.update_ticket_status(ticket.ticket_id, TicketStatus.RESOLVED)
    results.record(
        "Status Update Works",
        success
    )
    
    return customer


async def test_purchase_recording(results: TestResults, customer: CustomerCenter, c):
    """Test purchase recording and CLV."""
    print("\n💰 TEST: Purchase Recording & CLV")
    print("-" * 40)
    
    # Record purchase
    success = customer.record_purchase(
        customer_id=c.customer_id,
        product_id="PROD-001",
        product_name="Digital Course",
        amount=500000
    )
    
    results.record(
        "Purchase Recorded",
        success
    )
    
    # Get updated customer
    updated = customer.get_customer(c.customer_id)
    
    results.record(
        "Purchase Count Updated",
        updated.total_purchases == 1
    )
    
    results.record(
        "Total Spent Updated",
        updated.total_spent == 500000
    )
    
    results.record(
        "Status Upgraded to Active",
        updated.status == CustomerStatus.ACTIVE
    )
    
    results.record(
        "CLV Score Calculated",
        updated.clv_score > 0
    )
    
    return customer


async def test_clv_calculation(results: TestResults, customer: CustomerCenter):
    """Test CLV and churn calculations."""
    print("\n📊 TEST: CLV & Churn Calculation")
    print("-" * 40)
    
    # Create customer with purchases
    c = customer.create_customer(
        name="High Value Customer",
        email="hvc@example.com"
    )
    
    # Record multiple purchases
    for i in range(5):
        customer.record_purchase(
            customer_id=c.customer_id,
            product_id=f"PROD-{i}",
            product_name=f"Product {i}",
            amount=200000
        )
    
    # Get analytics
    analytics = customer.get_customer_analytics(c.customer_id)
    
    results.record(
        "Analytics Returned",
        "clv_score" in analytics
    )
    
    results.record(
        "CLV Score Present",
        analytics["clv_score"] > 0
    )
    
    results.record(
        "Churn Probability Present",
        "churn_probability" in analytics
    )
    
    results.record(
        "Engagement Score Calculated",
        "engagement_score" in analytics
    )
    
    return customer


async def test_customer_overview(results: TestResults, customer: CustomerCenter):
    """Test overall customer analytics."""
    print("\n📈 TEST: Customer Overview")
    print("-" * 40)
    
    overview = customer.get_overall_analytics()
    
    results.record(
        "Overview Returned",
        overview is not None
    )
    
    results.record(
        "Has Total Customers",
        "total_customers" in overview
    )
    
    results.record(
        "Has Active Count",
        "active" in overview
    )
    
    results.record(
        "Has Revenue",
        "total_revenue" in overview
    )
    
    results.record(
        "Has At-Risk Count",
        "at_risk_customers" in overview
    )
    
    return customer


async def test_integration_failover_customer(results: TestResults):
    """Test integration between DR and Customer."""
    print("\n🔗 TEST: DR-Customer Integration")
    print("-" * 40)
    
    dr = get_disaster_recovery_engine()
    customer = get_customer_center()
    
    # Ensure normal operation
    dr.db.set_system_state(SystemState.NORMAL)
    
    # Create customer during normal operation
    c = customer.create_customer(
        name="Integration Test",
        email="integration@test.com"
    )
    
    results.record(
        "Customer Created During Normal",
        c is not None
    )
    
    # Perform failover
    failover = dr.initiate_failover("Integration test")
    results.record(
        "Failover During Active Use",
        failover is not None
    )
    
    # Customer data should still be accessible
    customer_data = customer.get_customer(c.customer_id)
    results.record(
        "Customer Data Accessible Post-Failover",
        customer_data is not None
    )
    
    # Recover
    dr.complete_recovery()
    
    return dr, customer


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.0.9 - DR & Customer Tests")
    print("="*60)
    
    results = TestResults()
    
    try:
        # DR tests
        dr = await test_dr_engine_initialization(results)
        await test_system_state_management(results, dr)
        await test_health_check(results, dr)
        await test_failover_sequence(results, dr)
        await test_recovery_plan(results, dr)
        
        # Customer tests
        customer = await test_customer_center_initialization(results)
        customer, cust = await test_customer_creation(results, customer)
        await test_support_ticket(results, customer, cust)
        await test_purchase_recording(results, customer, cust)
        await test_clv_calculation(results, customer)
        await test_customer_overview(results, customer)
        
        # Integration tests
        await test_integration_failover_customer(results)
        
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
