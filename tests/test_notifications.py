"""
MAHALAKSMI AIOS v1.0.4 - Notification Center Tests
Simulates critical system alerts and verifies async event queue processing
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.enterprise.notification import (
    get_notification_center,
    NotificationCenter,
    NotificationPriority,
    NotificationChannel,
    Notification,
    RevenueNotifier
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
    
    def summary(self):
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nErrors:")
            for e in self.errors:
                print(f"  - {e}")
        print("="*60)
        return self.failed == 0


async def test_notification_center_initialization(results: TestResults):
    """Test notification center initializes correctly."""
    print("\n🔔 TEST: Notification Center Initialization")
    print("-" * 40)
    
    nc = get_notification_center()
    
    results.record(
        "Notification Center Created",
        nc is not None,
        "Failed to create"
    )
    
    results.record(
        "Channels Initialized",
        len(nc.channels) >= 3,
        f"Expected 3+ channels, got {len(nc.channels)}"
    )
    
    results.record(
        "Database Initialized",
        nc.db is not None,
        "Database not initialized"
    )
    
    results.record(
        "Queue Empty",
        nc.queue.empty(),
        f"Queue size: {nc.queue.qsize()}"
    )
    
    return nc


async def test_notification_creation(results: TestResults):
    """Test notification creation."""
    print("\n📝 TEST: Notification Creation")
    print("-" * 40)
    
    nc = get_notification_center()
    
    notification_id = nc.notify(
        event_type="test.notification",
        title="Test Alert",
        message="This is a test notification",
        priority=NotificationPriority.NORMAL,
        channels=[NotificationChannel.CONSOLE]
    )
    
    results.record(
        "Notification ID Generated",
        notification_id is not None and len(notification_id) > 0,
        f"ID: {notification_id}"
    )
    
    results.record(
        "Notification Queued",
        not nc.queue.empty(),
        "Queue still empty"
    )
    
    return nc


async def test_notification_queue_processing(results: TestResults):
    """Test async notification queue processing."""
    print("\n⚡ TEST: Async Queue Processing")
    print("-" * 40)
    
    nc = get_notification_center()
    
    # Start the worker
    await nc.start()
    
    # Queue multiple notifications
    for i in range(3):
        nc.notify(
            event_type=f"test.event_{i}",
            title=f"Event {i}",
            message=f"Processing event {i}",
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.CONSOLE]
        )
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Check queue was processed
    results.record(
        "Notifications Processed",
        nc.stats["total_sent"] >= 3,
        f"Only {nc.stats['total_sent']} processed"
    )
    
    # Stop worker
    await nc.stop()
    
    results.record(
        "Worker Stopped Gracefully",
        not nc.running,
        "Worker still running"
    )
    
    return nc


async def test_critical_notification(results: TestResults):
    """Test critical priority notifications."""
    print("\n🚨 TEST: Critical Notifications")
    print("-" * 40)
    
    nc = get_notification_center()
    
    # Start worker
    await nc.start()
    
    # Send critical notification
    notification_id = nc.notify_critical(
        event_type="system.critical",
        title="CRITICAL SYSTEM ALERT",
        message="Database connection failed!",
        data={"component": "database", "error": "connection_timeout"}
    )
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Verify stats
    results.record(
        "Critical Notification Queued",
        nc.stats["by_priority"]["critical"] >= 1,
        f"Critical count: {nc.stats['by_priority'].get('critical', 0)}"
    )
    
    results.record(
        "Multi-channel Sent",
        nc.stats["by_channel"].get("console", 0) >= 1,
        "Console channel not used"
    )
    
    # Stop worker
    await nc.stop()
    
    return nc


async def test_revenue_notifications(results: TestResults):
    """Test revenue system notifications."""
    print("\n💰 TEST: Revenue Notifications")
    print("-" * 40)
    
    nc = get_notification_center()
    revenue_notifier = RevenueNotifier(nc)
    
    # Start worker
    await nc.start()
    
    # Simulate revenue event
    await revenue_notifier.on_revenue_recorded(
        source="digital_products",
        amount=1000000,
        transaction_id="REV-TEST-001"
    )
    
    await asyncio.sleep(0.5)
    
    # Verify notification was sent
    recent = nc.get_recent(limit=5)
    
    results.record(
        "Revenue Notification Sent",
        len(recent) > 0,
        "No notifications in history"
    )
    
    if recent:
        latest = recent[0]
        results.record(
            "Correct Event Type",
            latest["event_type"] == "revenue.recorded",
            f"Wrong event: {latest['event_type']}"
        )
    
    # Simulate CEO disbursement
    await revenue_notifier.on_ceo_disbursement(
        amount=600000,
        transaction_id="CEO-TEST-001"
    )
    
    await asyncio.sleep(0.5)
    
    recent = nc.get_recent(limit=5)
    results.record(
        "CEO Disbursement Notified",
        any(n["event_type"] == "revenue.ceo_disbursement" for n in recent),
        "CEO disbursement not found"
    )
    
    # Stop worker
    await nc.stop()
    
    return nc


async def test_license_notification(results: TestResults):
    """Test license purchase notifications."""
    print("\n🔑 TEST: License Notifications")
    print("-" * 40)
    
    nc = get_notification_center()
    revenue_notifier = RevenueNotifier(nc)
    
    # Start worker
    await nc.start()
    
    # Simulate license purchase
    await revenue_notifier.on_license_purchased(
        license_key="MLK-XXXX-XXXX-XXXX-XXXX-TEST",
        customer_id="CUST-001",
        product_id="MLK-SOFTWARE-001"
    )
    
    await asyncio.sleep(0.5)
    
    recent = nc.get_recent(limit=5)
    
    results.record(
        "License Notification Sent",
        any(n["event_type"] == "product.license_purchased" for n in recent),
        "License notification not found"
    )
    
    # Stop worker
    await nc.stop()
    
    return nc


async def test_notification_statistics(results: TestResults):
    """Test notification statistics."""
    print("\n📊 TEST: Notification Statistics")
    print("-" * 40)
    
    nc = get_notification_center()
    
    stats = nc.get_stats()
    
    results.record(
        "Stats Returned",
        "total_sent" in stats,
        "Missing total_sent"
    )
    
    results.record(
        "Stats Has Failed Count",
        "total_failed" in stats,
        "Missing total_failed"
    )
    
    results.record(
        "Stats Has Channel Breakdown",
        "by_channel" in stats,
        "Missing by_channel"
    )
    
    results.record(
        "Stats Has Priority Breakdown",
        "by_priority" in stats,
        "Missing by_priority"
    )
    
    results.record(
        "Stats Has Queue Size",
        "queue_size" in stats,
        "Missing queue_size"
    )
    
    return stats


async def test_notification_history(results: TestResults):
    """Test notification history retrieval."""
    print("\n📜 TEST: Notification History")
    print("-" * 40)
    
    nc = get_notification_center()
    
    # Get recent notifications
    recent = nc.get_recent(limit=10)
    
    results.record(
        "History Retrieved",
        isinstance(recent, list),
        "Not a list"
    )
    
    if recent:
        first = recent[0]
        results.record(
            "History Has ID",
            "id" in first,
            "Missing id field"
        )
        
        results.record(
            "History Has Event Type",
            "event_type" in first,
            "Missing event_type"
        )
        
        results.record(
            "History Has Priority",
            "priority" in first,
            "Missing priority"
        )
    
    return recent


async def test_handler_registration(results: TestResults):
    """Test event handler registration."""
    print("\n🔗 TEST: Event Handler Registration")
    print("-" * 40)
    
    nc = get_notification_center()
    
    # Track handler calls
    handler_called = {"count": 0}
    
    def test_handler(notification):
        handler_called["count"] += 1
    
    # Register handler
    nc.register_handler("test.custom_event", test_handler)
    
    results.record(
        "Handler Registered",
        len(nc.handlers.get("test.custom_event", [])) > 0,
        "Handler not registered"
    )
    
    # Start worker
    await nc.start()
    
    # Trigger event
    nc.notify(
        event_type="test.custom_event",
        title="Custom Event Test",
        message="Testing custom handler",
        channels=[NotificationChannel.CONSOLE]
    )
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Stop worker
    await nc.stop()
    
    results.record(
        "Handler Was Called",
        handler_called["count"] >= 1,
        f"Handler called {handler_called['count']} times"
    )
    
    return nc


async def run_all_tests():
    """Run all notification tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.0.4 - Notification Center Tests")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    results = TestResults()
    
    try:
        await test_notification_center_initialization(results)
        await test_notification_creation(results)
        await test_notification_queue_processing(results)
        await test_critical_notification(results)
        await test_revenue_notifications(results)
        await test_license_notification(results)
        await test_notification_statistics(results)
        await test_notification_history(results)
        await test_handler_registration(results)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        results.failed += 1
    
    success = results.summary()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED - Notification Center Operational!")
    else:
        print("⚠️ SOME TESTS FAILED - Review above")
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
