"""
MAHALAKSMI AIOS v1.0 - Volume V: Enterprise Integration Hub
System communication bus with pub/sub orchestration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventType(Enum):
    """System event types."""
    # Revenue Events
    REVENUE_RECEIVED = "revenue.received"
    DISBURSEMENT_COMPLETED = "disbursement.completed"
    
    # Intelligence Events
    AI_QUERY = "ai.query"
    AI_RESPONSE = "ai.response"
    
    # System Events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    HEALTH_CHECK = "system.health"
    
    # Business Events
    TRANSACTION_CREATED = "transaction.created"
    ALERT_TRIGGERED = "alert.triggered"


@dataclass
class Event:
    """System event."""
    event_id: str
    event_type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None


@dataclass
class Subscription:
    """Event subscription."""
    subscription_id: str
    event_type: EventType
    callback: Callable
    description: str = ""
    active: bool = True


class PubSubBus:
    """
    Enterprise Pub/Sub Communication Bus.
    Enables seamless orchestration between Revenue Center and Intelligence layer.
    """
    
    def __init__(self):
        self.subscriptions: Dict[EventType, List[Subscription]] = defaultdict(list)
        self.event_history: List[Event] = []
        self._subscription_counter = 0
        
        logger.info("Enterprise Pub/Sub Bus initialized")
    
    def subscribe(
        self,
        event_type: EventType,
        callback: Callable,
        description: str = ""
    ) -> str:
        """Subscribe to event type."""
        self._subscription_counter += 1
        subscription_id = f"sub_{self._subscription_counter}"
        
        subscription = Subscription(
            subscription_id=subscription_id,
            event_type=event_type,
            callback=callback,
            description=description
        )
        
        self.subscriptions[event_type].append(subscription)
        logger.info(f"Subscription created: {subscription_id} for {event_type.value}")
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from event."""
        for event_type, subs in self.subscriptions.items():
            for sub in subs:
                if sub.subscription_id == subscription_id:
                    sub.active = False
                    logger.info(f"Unsubscribed: {subscription_id}")
                    return True
        return False
    
    async def publish(self, event: Event) -> None:
        """Publish event to all subscribers."""
        self.event_history.append(event)
        
        # Keep last 1000 events
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
        
        subscribers = self.subscriptions.get(event.event_type, [])
        
        logger.debug(f"Publishing {event.event_type.value} to {len(subscribers)} subscribers")
        
        for subscription in subscribers:
            if not subscription.active:
                continue
            
            try:
                if asyncio.iscoroutinefunction(subscription.callback):
                    await subscription.callback(event)
                else:
                    subscription.callback(event)
            except Exception as e:
                logger.error(f"Subscription callback error: {subscription.subscription_id} - {e}")
    
    def get_subscriptions(self) -> List[Dict]:
        """Get all active subscriptions."""
        return [
            {
                "id": sub.subscription_id,
                "event_type": sub.event_type.value,
                "description": sub.description,
                "active": sub.active
            }
            for subs in self.subscriptions.values()
            for sub in subs
            if sub.active
        ]
    
    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Dict]:
        """Get event history."""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "source": e.source,
                "data": e.data,
                "timestamp": e.timestamp.isoformat()
            }
            for e in events[-limit:]
        ]


class EnterpriseHub:
    """
    Central enterprise integration hub.
    Orchestrates all system components and services.
    """
    
    def __init__(self):
        self.pubsub = PubSubBus()
        self._running = False
        self._subscriptions: List[str] = []
        
        # Register default event handlers
        self._setup_default_handlers()
        
        logger.info("Enterprise Hub initialized")
    
    def _setup_default_handlers(self) -> None:
        """Setup default event handlers."""
        # Revenue -> Finance sync
        self._subscriptions.append(
            self.pubsub.subscribe(
                EventType.REVENUE_RECEIVED,
                self._handle_revenue_received,
                "Sync revenue to finance ledger"
            )
        )
        
        # Disbursement -> Alert
        self._subscriptions.append(
            self.pubsub.subscribe(
                EventType.DISBURSEMENT_COMPLETED,
                self._handle_disbursement_completed,
                "Alert on disbursement completion"
            )
        )
        
        # Health check subscriber
        self._subscriptions.append(
            self.pubsub.subscribe(
                EventType.HEALTH_CHECK,
                self._handle_health_check,
                "Health check aggregator"
            )
        )
    
    async def _handle_revenue_received(self, event: Event) -> None:
        """Handle revenue received event."""
        logger.info(f"Revenue event received: {event.data.get('amount', 0)}")
    
    async def _handle_disbursement_completed(self, event: Event) -> None:
        """Handle disbursement completed event."""
        logger.info(f"Disbursement completed: {event.data.get('request_id', 'unknown')}")
    
    async def _handle_health_check(self, event: Event) -> None:
        """Handle health check event."""
        logger.debug("Health check event received")
    
    async def start(self) -> None:
        """Start the enterprise hub."""
        self._running = True
        logger.info("Enterprise Hub started")
    
    async def stop(self) -> None:
        """Stop the enterprise hub."""
        self._running = False
        logger.info("Enterprise Hub stopped")
    
    async def emit_event(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        correlation_id: str = None
    ) -> Event:
        """Emit a new event."""
        import uuid
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source=source,
            data=data,
            correlation_id=correlation_id
        )
        
        await self.pubsub.publish(event)
        return event
    
    def get_status(self) -> Dict[str, Any]:
        """Get hub status."""
        return {
            "running": self._running,
            "active_subscriptions": len(self._subscriptions),
            "event_types_subscribed": list(set(
                sub.split(" -> ")[0] if " -> " in sub else "unknown"
                for sub in self._subscriptions
            )),
            "recent_events": len(self.pubsub.event_history)
        }


# Global enterprise hub
_enterprise_hub: Optional[EnterpriseHub] = None


def get_enterprise_hub() -> EnterpriseHub:
    """Get or create global enterprise hub."""
    global _enterprise_hub
    if _enterprise_hub is None:
        _enterprise_hub = EnterpriseHub()
    return _enterprise_hub
