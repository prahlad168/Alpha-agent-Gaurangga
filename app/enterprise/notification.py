"""
MAHALAKSMI AIOS v1.0 - Volume V Chapter 42: Notification Center
Asynchronous event-driven notification manager with multiple delivery channels
"""
import os
import sys
import asyncio
import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification delivery channels."""
    WEBHOOK = "webhook"
    EMAIL = "email"
    CONSOLE = "console"
    SMS = "sms"


class NotificationStatus(Enum):
    """Notification status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class Notification:
    """Notification event."""
    notification_id: str
    event_type: str
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    data: Dict[str, Any] = field(default_factory=dict)
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: str = ""
    sent_at: str = ""
    recipients: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    url: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    secret: str = ""


@dataclass
class EmailConfig:
    """Email configuration (stub)."""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender: str = "noreply@mahalaksmi.ai"
    username: str = ""
    password: str = ""


# ============================================================================
# NOTIFICATION CHANNELS
# ============================================================================

class BaseChannel:
    """Base notification channel."""
    
    async def send(self, notification: Notification) -> bool:
        """Send notification. Override in subclasses."""
        raise NotImplementedError


class WebhookChannel(BaseChannel):
    """Webhook notification channel."""
    
    def __init__(self, config: WebhookConfig = None):
        self.config = config
        self.webhook_url = os.environ.get("WEBHOOK_URL", "")
    
    async def send(self, notification: Notification) -> bool:
        """Send webhook notification."""
        if not self.webhook_url:
            logger.debug(f"Webhook URL not configured, skipping: {notification.notification_id}")
            return True
        
        try:
            payload = {
                "event_type": notification.event_type,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority.value,
                "data": notification.data,
                "timestamp": notification.created_at
            }
            
            # Simulate webhook call (in production, use httpx or requests)
            logger.info(f"Webhook would send to {self.webhook_url}: {notification.title}")
            
            # In real implementation:
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(self.webhook_url, json=payload)
            #     return response.status_code == 200
            
            return True
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return False


class EmailChannel(BaseChannel):
    """Email notification channel (SMTP stub)."""
    
    def __init__(self, config: EmailConfig = None):
        self.config = config or EmailConfig()
    
    async def send(self, notification: Notification) -> bool:
        """Send email notification (stub)."""
        try:
            logger.info(f"Email stub: Would send to {notification.recipients}")
            logger.info(f"  Subject: {notification.title}")
            logger.info(f"  Body: {notification.message}")
            
            # In real implementation with SMTP:
            # import smtplib
            # from email.mime.text import MIMEText
            # msg = MIMEText(notification.message)
            # msg['Subject'] = notification.title
            # msg['From'] = self.config.sender
            # msg['To'] = ', '.join(notification.recipients)
            # 
            # with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.config.username, self.config.password)
            #     server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False


class ConsoleChannel(BaseChannel):
    """Console/Terminal notification channel."""
    
    def __init__(self):
        self.emoji_map = {
            NotificationPriority.LOW: "ℹ️",
            NotificationPriority.NORMAL: "📢",
            NotificationPriority.HIGH: "⚠️",
            NotificationPriority.CRITICAL: "🚨"
        }
    
    async def send(self, notification: Notification) -> bool:
        """Send console notification."""
        emoji = self.emoji_map.get(notification.priority, "📢")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*60}")
        print(f"{emoji} NOTIFICATION [{notification.priority.value.upper()}] - {timestamp}")
        print(f"{'='*60}")
        print(f"Type: {notification.event_type}")
        print(f"Title: {notification.title}")
        print(f"Message: {notification.message}")
        if notification.data:
            print(f"Data: {json.dumps(notification.data, indent=2)}")
        print(f"{'='*60}\n")
        
        return True


# ============================================================================
# NOTIFICATION DATABASE
# ============================================================================

class NotificationDatabase:
    """SQLite database for notification storage."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "notifications.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id TEXT PRIMARY KEY,
                event_type TEXT,
                title TEXT,
                message TEXT,
                priority TEXT,
                channels TEXT,
                data TEXT,
                status TEXT,
                created_at TEXT,
                sent_at TEXT,
                recipients TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_preferences (
                user_id TEXT PRIMARY KEY,
                channels TEXT,
                priority_threshold TEXT,
                quiet_hours_start TEXT,
                quiet_hours_end TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save(self, notification: Notification) -> bool:
        """Save notification to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO notifications 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.notification_id,
                notification.event_type,
                notification.title,
                notification.message,
                notification.priority.value,
                json.dumps([c.value for c in notification.channels]),
                json.dumps(notification.data),
                notification.status.value,
                notification.created_at,
                notification.sent_at,
                json.dumps(notification.recipients),
                json.dumps(notification.metadata)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save notification: {e}")
            return False
    
    def get_recent(self, limit: int = 50) -> List[Notification]:
        """Get recent notifications."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        notifications = []
        for row in rows:
            notifications.append(self._row_to_notification(row))
        return notifications
    
    def get_by_event_type(self, event_type: str) -> List[Notification]:
        """Get notifications by event type."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM notifications WHERE event_type = ? ORDER BY created_at DESC",
            (event_type,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_notification(row) for row in rows]
    
    def _row_to_notification(self, row) -> Notification:
        """Convert row to Notification."""
        return Notification(
            notification_id=row['notification_id'],
            event_type=row['event_type'],
            title=row['title'],
            message=row['message'],
            priority=NotificationPriority(row['priority']),
            channels=[NotificationChannel(c) for c in json.loads(row['channels'])],
            data=json.loads(row['data']),
            status=NotificationStatus(row['status']),
            created_at=row['created_at'],
            sent_at=row['sent_at'],
            recipients=json.loads(row['recipients']),
            metadata=json.loads(row['metadata'])
        )


# ============================================================================
# NOTIFICATION CENTER
# ============================================================================

class NotificationCenter:
    """
    Event-driven asynchronous notification manager.
    Supports multiple delivery channels: Webhook, Email, Console.
    """
    
    def __init__(self):
        self.db = NotificationDatabase()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None
        
        # Initialize channels
        self.channels = {
            NotificationChannel.WEBHOOK: WebhookChannel(),
            NotificationChannel.EMAIL: EmailChannel(),
            NotificationChannel.CONSOLE: ConsoleChannel()
        }
        
        # Event handlers
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "by_channel": defaultdict(int),
            "by_priority": defaultdict(int)
        }
        
        logger.info("NotificationCenter initialized")
    
    async def start(self):
        """Start notification worker."""
        if self.running:
            return
        
        self.running = True
        self.worker_task = asyncio.create_task(self._process_queue())
        logger.info("NotificationCenter worker started")
    
    async def stop(self):
        """Stop notification worker."""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("NotificationCenter worker stopped")
    
    async def _process_queue(self):
        """Process notification queue."""
        while self.running:
            try:
                notification = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
                await self._send_notification(notification)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
    
    async def _send_notification(self, notification: Notification):
        """Send notification through configured channels."""
        success_count = 0
        
        for channel in notification.channels:
            channel_handler = self.channels.get(channel)
            if not channel_handler:
                continue
            
            try:
                success = await channel_handler.send(notification)
                if success:
                    success_count += 1
                    self.stats["by_channel"][channel.value] += 1
                else:
                    self.stats["total_failed"] += 1
            except Exception as e:
                logger.error(f"Channel {channel.value} failed: {e}")
                self.stats["total_failed"] += 1
        
        # Update notification status
        notification.status = NotificationStatus.SENT if success_count > 0 else NotificationStatus.FAILED
        notification.sent_at = datetime.now().isoformat()
        
        # Save to database
        self.db.save(notification)
        
        self.stats["total_sent"] += 1
        self.stats["by_priority"][notification.priority.value] += 1
        
        # Trigger event handlers
        await self._trigger_handlers(notification)
    
    async def _trigger_handlers(self, notification: Notification):
        """Trigger registered event handlers."""
        handlers = self.handlers.get(notification.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(notification)
                else:
                    handler(notification)
            except Exception as e:
                logger.error(f"Handler error: {e}")
    
    def notify(
        self,
        event_type: str,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: List[NotificationChannel] = None,
        data: Dict[str, Any] = None,
        recipients: List[str] = None
    ) -> str:
        """
        Queue a notification for async delivery.
        Returns notification ID.
        """
        if channels is None:
            channels = [NotificationChannel.CONSOLE]
        
        notification_id = hashlib.md5(
            f"{event_type}{title}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        notification = Notification(
            notification_id=notification_id,
            event_type=event_type,
            title=title,
            message=message,
            priority=priority,
            channels=channels,
            data=data or {},
            recipients=recipients or []
        )
        
        # Save to database
        self.db.save(notification)
        
        # Queue for async processing
        self.queue.put_nowait(notification)
        
        logger.info(f"Notification queued: {notification_id} ({event_type})")
        return notification_id
    
    def notify_critical(
        self,
        event_type: str,
        title: str,
        message: str,
        data: Dict[str, Any] = None
    ) -> str:
        """Send critical priority notification to all channels."""
        return self.notify(
            event_type=event_type,
            title=title,
            message=message,
            priority=NotificationPriority.CRITICAL,
            channels=[NotificationChannel.CONSOLE, NotificationChannel.WEBHOOK, NotificationChannel.EMAIL],
            data=data
        )
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific event type."""
        self.handlers[event_type].append(handler)
        logger.info(f"Handler registered for event: {event_type}")
    
    async def send_immediate(
        self,
        title: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.CONSOLE
    ) -> bool:
        """Send notification immediately (bypass queue)."""
        notification = Notification(
            notification_id="IMMEDIATE",
            event_type="immediate",
            title=title,
            message=message,
            priority=NotificationPriority.HIGH,
            channels=[channel]
        )
        
        await self._send_notification(notification)
        return notification.status == NotificationStatus.SENT
    
    def get_recent(self, limit: int = 50) -> List[Dict]:
        """Get recent notifications."""
        notifications = self.db.get_recent(limit)
        return [
            {
                "id": n.notification_id,
                "event_type": n.event_type,
                "title": n.title,
                "priority": n.priority.value,
                "status": n.status.value,
                "created_at": n.created_at,
                "sent_at": n.sent_at
            }
            for n in notifications
        ]
    
    def get_stats(self) -> Dict:
        """Get notification statistics."""
        return {
            "total_sent": self.stats["total_sent"],
            "total_failed": self.stats["total_failed"],
            "success_rate": (
                self.stats["total_sent"] / max(self.stats["total_sent"] + self.stats["total_failed"], 1)
            ) * 100,
            "by_channel": dict(self.stats["by_channel"]),
            "by_priority": dict(self.stats["by_priority"]),
            "queue_size": self.queue.qsize()
        }


# ============================================================================
# SYSTEM EVENT NOTIFICATIONS
# ============================================================================

class RevenueNotifier:
    """Revenue system event notifications."""
    
    def __init__(self, notification_center: NotificationCenter):
        self.nc = notification_center
    
    async def on_revenue_recorded(self, source: str, amount: float, transaction_id: str):
        """Called when revenue is recorded."""
        self.nc.notify_critical(
            event_type="revenue.recorded",
            title=f"Revenue Recorded: Rp {amount:,.0f}",
            message=f"New revenue from {source}. Transaction: {transaction_id}",
            data={
                "source": source,
                "amount": amount,
                "transaction_id": transaction_id,
                "ceo_share": amount * 0.60,
                "operational_share": amount * 0.40
            }
        )
    
    async def on_ceo_disbursement(self, amount: float, transaction_id: str):
        """Called when CEO share is disbursed."""
        self.nc.notify_critical(
            event_type="revenue.ceo_disbursement",
            title=f"CEO Share Disbursed: Rp {amount:,.0f}",
            message=f"60% share transferred to BCA 6485086645. TX: {transaction_id}",
            data={
                "amount": amount,
                "account": "6485086645",
                "bank": "BCA",
                "transaction_id": transaction_id
            }
        )
    
    async def on_license_purchased(self, license_key: str, customer_id: str, product_id: str):
        """Called when a license is purchased."""
        self.nc.notify_critical(
            event_type="product.license_purchased",
            title="New License Purchased",
            message=f"License {license_key[:20]}... for product {product_id}",
            data={
                "license_key": license_key,
                "customer_id": customer_id,
                "product_id": product_id
            }
        )


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_notification_center: Optional[NotificationCenter] = None


def get_notification_center() -> NotificationCenter:
    """Get or create global notification center."""
    global _notification_center
    if _notification_center is None:
        _notification_center = NotificationCenter()
    return _notification_center
