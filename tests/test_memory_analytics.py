"""
MAHALAKSMI AIOS v1.0.2 - Memory & Analytics Integration Tests
Validates analytics calculations match ledger inputs exactly
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.intelligence.memory import get_memory, EnterpriseMemory
from app.business.analytics import get_analytics, AnalyticsCenter
from app.business.revenue import get_revenue_manager
from app.business.finance import get_finance_ledger, TransactionType, Category


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
    
    def summary(self):
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nErrors:")
            for e in self.errors:
                print(f"  - {e}")
        print("="*60)
        return self.failed == 0


async def test_memory_storage(results: TestResults):
    """Test memory storage functionality."""
    print("\n💾 TEST: Memory Storage")
    print("-" * 40)
    
    memory = get_memory()
    
    # Store conversation memory
    entry = memory.store(
        content="Revenue transaction completed for digital products",
        memory_type="conversation",
        metadata={"user": "test", "source": "api"}
    )
    
    results.record(
        "Store Memory Entry",
        entry.entry_id is not None,
        f"No entry ID: {entry.entry_id}"
    )
    
    # Retrieve memory
    entries = memory.retrieve("revenue transaction")
    results.record(
        "Retrieve Similar Memory",
        len(entries) > 0,
        "No similar memories found"
    )
    
    # Store revenue event
    rev_entry = memory.store_revenue_event(
        transaction_id="TEST-001",
        source="test_products",
        amount=1000000,
        ceo_share=600000,
        operational_share=400000
    )
    
    results.record(
        "Store Revenue Event",
        rev_entry.entry_id is not None,
        "Revenue event not stored"
    )
    
    return memory


async def test_memory_similarity(results: TestResults):
    """Test memory similarity search."""
    print("\n🔍 TEST: Memory Similarity Search")
    print("-" * 40)
    
    memory = get_memory()
    
    # Store multiple entries with overlapping terms
    memory.store("Revenue transaction for digital products", "revenue")
    memory.store("Analytics dashboard shows revenue metrics", "revenue")
    memory.store("System monitoring tracks revenue events", "system")
    
    # Search for similar with revenue-related query
    results_list = memory.retrieve("revenue transaction analytics", min_similarity=0.01)
    
    results.record(
        "Similarity Search Returns Results",
        len(results_list) > 0,
        f"No results: {len(results_list)}"
    )
    
    if results_list:
        results.record(
            "Relevance Score Calculated",
            all(e.relevance_score >= 0 for e in results_list),
            "Some scores invalid"
        )
    
    return memory


async def test_memory_stats(results: TestResults):
    """Test memory statistics."""
    print("\n📊 TEST: Memory Statistics")
    print("-" * 40)
    
    memory = get_memory()
    stats = memory.get_stats()
    
    results.record(
        "Stats Contains Total Entries",
        "total_entries" in stats,
        "Missing total_entries"
    )
    
    results.record(
        "Stats Contains Vocabulary",
        "vocabulary_size" in stats,
        "Missing vocabulary_size"
    )
    
    results.record(
        "Stats Contains Type Breakdown",
        "by_type" in stats,
        "Missing by_type"
    )
    
    return stats


async def test_analytics_summary(results: TestResults):
    """Test analytics summary generation."""
    print("\n📈 TEST: Analytics Summary")
    print("-" * 40)
    
    analytics = get_analytics()
    
    # Generate summary
    summary = analytics.generate_summary()
    
    results.record(
        "Summary Has Revenue Metrics",
        hasattr(summary, 'revenue'),
        "Missing revenue metrics"
    )
    
    results.record(
        "Summary Has Growth Metrics",
        hasattr(summary, 'growth'),
        "Missing growth metrics"
    )
    
    results.record(
        "Summary Has Burn Rate",
        hasattr(summary, 'burn_rate'),
        "Missing burn rate"
    )
    
    results.record(
        "Summary Has Distribution",
        hasattr(summary, 'distribution'),
        "Missing distribution"
    )
    
    return summary


async def test_distribution_calculation(results: TestResults):
    """Test 60/40 distribution calculation."""
    print("\n💰 TEST: 60/40 Distribution Calculation")
    print("-" * 40)
    
    analytics = get_analytics()
    
    # Add test revenue
    revenue = get_revenue_manager()
    await revenue.record_digital_revenue(
        source="test_distribution",
        amount=10000000,
        payment_method="qris"
    )
    
    distribution = analytics.calculate_distribution()
    
    # Verify CEO share is 60%
    expected_ceo = 10000000 * 0.60
    ceo_match = abs(distribution.ceo_share - expected_ceo) < 1
    results.record(
        "CEO Share (60%)",
        ceo_match,
        f"Expected {expected_ceo}, got {distribution.ceo_share}"
    )
    
    # Verify Operational is 40%
    expected_ops = 10000000 * 0.40
    ops_match = abs(distribution.operational_reserve - expected_ops) < 1
    results.record(
        "Operational Reserve (40%)",
        ops_match,
        f"Expected {expected_ops}, got {distribution.operational_reserve}"
    )
    
    # Verify sub-allocations
    reinvestment = distribution.operational_reserve * 0.25
    reinvestment_match = abs(distribution.reinvestment_allocated - reinvestment) < 1
    results.record(
        "Reinvestment Allocation (25%)",
        reinvestment_match,
        f"Expected {reinvestment}, got {distribution.reinvestment_allocated}"
    )
    
    return distribution


async def test_analytics_ledger_sync(results: TestResults):
    """Test that analytics matches ledger exactly."""
    print("\n🔗 TEST: Analytics-Ledger Synchronization")
    print("-" * 40)
    
    analytics = get_analytics()
    finance = get_finance_ledger()
    revenue = get_revenue_manager()
    
    # Get initial state
    ledger_balance = finance.get_balance()
    revenue_summary = revenue.get_summary()
    
    # Add test entry
    await revenue.record_digital_revenue(
        source="test_sync",
        amount=5000000,
        payment_method="bank_transfer"
    )
    
    # Verify analytics picks up the change
    analytics_summary = analytics.generate_summary()
    
    results.record(
        "Analytics Reflects Revenue",
        analytics_summary.revenue.total_gross_revenue >= revenue_summary["total_revenue"] + 5000000,
        f"Revenue not synced: {analytics_summary.revenue.total_gross_revenue}"
    )
    
    # Verify distribution calculation
    distribution = analytics.calculate_distribution()
    expected = revenue_summary["total_revenue"] + 5000000
    results.record(
        "Distribution Matches Total",
        abs(distribution.total_revenue - expected) < 1,
        f"Mismatch: {distribution.total_revenue} vs {expected}"
    )
    
    return True


async def test_analytics_json_output(results: TestResults):
    """Test analytics JSON output format."""
    print("\n📋 TEST: Analytics JSON Output")
    print("-" * 40)
    
    analytics = get_analytics()
    json_output = analytics.get_summary_json()
    
    # Verify required fields
    results.record(
        "JSON Has Generated At",
        "generated_at" in json_output,
        "Missing generated_at"
    )
    
    results.record(
        "JSON Has Period",
        "period" in json_output,
        "Missing period"
    )
    
    results.record(
        "JSON Has Revenue Metrics",
        "revenue_metrics" in json_output,
        "Missing revenue_metrics"
    )
    
    results.record(
        "JSON Has Growth Metrics",
        "growth_metrics" in json_output,
        "Missing growth_metrics"
    )
    
    results.record(
        "JSON Has Distribution",
        "distribution_breakdown" in json_output,
        "Missing distribution_breakdown"
    )
    
    return json_output


async def test_top_sources(results: TestResults):
    """Test top revenue sources calculation."""
    print("\n🏆 TEST: Top Revenue Sources")
    print("-" * 40)
    
    analytics = get_analytics()
    
    # Add multiple sources
    revenue = get_revenue_manager()
    await revenue.record_digital_revenue("products", 10000000, "qris")
    await revenue.record_digital_revenue("services", 15000000, "bank")
    await revenue.record_digital_revenue("products", 5000000, "ewallet")
    
    sources = analytics.get_top_sources()
    
    results.record(
        "Returns Sources List",
        len(sources) > 0,
        "No sources returned"
    )
    
    results.record(
        "Sources Have Total",
        all("total" in s for s in sources),
        "Missing total field"
    )
    
    results.record(
        "Sources Have Percentage",
        all("percentage" in s for s in sources),
        "Missing percentage field"
    )
    
    return sources


async def run_all_tests():
    """Run all memory and analytics tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.0.2 - Memory & Analytics Tests")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    results = TestResults()
    
    try:
        await test_memory_storage(results)
        await test_memory_similarity(results)
        await test_memory_stats(results)
        await test_analytics_summary(results)
        await test_distribution_calculation(results)
        await test_analytics_ledger_sync(results)
        await test_analytics_json_output(results)
        await test_top_sources(results)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        results.failed += 1
    
    success = results.summary()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED - Memory & Analytics Operational!")
    else:
        print("⚠️ SOME TESTS FAILED - Review above")
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
