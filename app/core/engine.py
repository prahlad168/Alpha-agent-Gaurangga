"""
MAHALAKSMI AIOS v1.0 - Volume I: Core Engine
The heart of Mahalaksmi Core - Lifecycle Manager & Executive Scheduler
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """System lifecycle states."""
    INITIALIZING = "initializing"
    BOOTING = "booting"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"


class ComponentStatus(Enum):
    """Component health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class Component:
    """Represents a system component."""
    name: str
    version: str
    status: ComponentStatus = ComponentStatus.UNKNOWN
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class LifecycleEvent:
    """System lifecycle event."""
    timestamp: datetime
    state: SystemState
    component: Optional[str]
    message: str
    data: Dict[str, Any] = field(default_factory=dict)


class CoreEngine:
    """
    Central lifecycle manager and executive scheduler for MAHALAKSMI AIOS.
    Manages system initialization, component health, and graceful shutdown.
    """
    
    def __init__(self):
        self.state = SystemState.INITIALIZING
        self.components: Dict[str, Component] = {}
        self.event_history: List[LifecycleEvent] = []
        self.schedulers: Dict[str, asyncio.Task] = {}
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        # Callbacks for state changes
        self._state_callbacks: Dict[SystemState, List[Callable]] = defaultdict(list)
        
        logger.info("MAHALAKSMI AIOS Core Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize all system components."""
        try:
            self.transition_state(SystemState.INITIALIZING)
            logger.info("Starting system initialization...")
            
            # Register core components
            self.register_component("core.engine", "1.0.0")
            self.register_component("core.security", "1.0.0")
            self.register_component("core.lifecycle", "1.0.0")
            
            # Simulate initialization phases
            await self._init_phase_1()  # Core systems
            await self._init_phase_2()  # Intelligence layer
            await self._init_phase_3()  # Business systems
            await self._init_phase_4()  # Enterprise services
            
            self.transition_state(SystemState.RUNNING)
            self._running = True
            
            logger.info("✅ System initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.transition_state(SystemState.ERROR)
            return False
    
    async def _init_phase_1(self) -> None:
        """Phase 1: Core systems initialization."""
        logger.info("Phase 1/4: Initializing core systems...")
        await asyncio.sleep(0.1)  # Simulate work
        self.register_component("core.runtime", "1.0.0")
        self.register_component("core.config", "1.0.0")
    
    async def _init_phase_2(self) -> None:
        """Phase 2: Intelligence layer initialization."""
        logger.info("Phase 2/4: Initializing intelligence layer...")
        await asyncio.sleep(0.1)
        self.register_component("intelligence.gateway", "1.0.0")
        self.register_component("intelligence.nlp", "1.0.0")
        self.register_component("intelligence.memory", "1.0.0")
    
    async def _init_phase_3(self) -> None:
        """Phase 3: Business systems initialization."""
        logger.info("Phase 3/4: Initializing business systems...")
        await asyncio.sleep(0.1)
        self.register_component("business.revenue", "1.0.0")
        self.register_component("business.finance", "1.0.0")
    
    async def _init_phase_4(self) -> None:
        """Phase 4: Enterprise services initialization."""
        logger.info("Phase 4/4: Initializing enterprise services...")
        await asyncio.sleep(0.1)
        self.register_component("enterprise.hub", "1.0.0")
        self.register_component("enterprise.monitoring", "1.0.0")
    
    def register_component(self, name: str, version: str, **metadata) -> Component:
        """Register a new system component."""
        component = Component(
            name=name,
            version=version,
            status=ComponentStatus.HEALTHY,
            metadata=metadata
        )
        self.components[name] = component
        logger.info(f"Component registered: {name} v{version}")
        return component
    
    def update_component_status(self, name: str, status: ComponentStatus) -> bool:
        """Update component health status."""
        if name in self.components:
            self.components[name].status = status
            self.components[name].last_heartbeat = datetime.now()
            return True
        return False
    
    def transition_state(self, new_state: SystemState) -> None:
        """Transition to new system state."""
        old_state = self.state
        self.state = new_state
        
        event = LifecycleEvent(
            timestamp=datetime.now(),
            state=new_state,
            component=None,
            message=f"State transition: {old_state.value} -> {new_state.value}"
        )
        self.event_history.append(event)
        
        logger.info(f"System state: {old_state.value} -> {new_state.value}")
        
        # Trigger callbacks
        for callback in self._state_callbacks[new_state]:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"State callback error: {e}")
    
    def on_state_change(self, state: SystemState, callback: Callable) -> None:
        """Register callback for state changes."""
        self._state_callbacks[state].append(callback)
    
    async def shutdown(self, graceful: bool = True) -> None:
        """Graceful system shutdown."""
        logger.info(f"Initiating {'graceful' if graceful else 'force'} shutdown...")
        self.transition_state(SystemState.SHUTTING_DOWN)
        
        # Cancel all scheduled tasks
        for name, task in self.schedulers.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled scheduler: {name}")
        
        # Wait for cleanup
        if graceful:
            await asyncio.sleep(0.5)  # Cleanup time
        
        self._running = False
        self._shutdown_event.set()
        logger.info("System shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        healthy = sum(1 for c in self.components.values() if c.status == ComponentStatus.HEALTHY)
        
        return {
            "system": {
                "name": "MAHALAKSMI AIOS",
                "version": "1.0.0",
                "state": self.state.value,
                "running": self._running,
                "uptime_seconds": (datetime.now() - self.event_history[0].timestamp).total_seconds() if self.event_history else 0
            },
            "components": {
                "total": len(self.components),
                "healthy": healthy,
                "degraded": sum(1 for c in self.components.values() if c.status == ComponentStatus.DEGRADED),
                "failed": sum(1 for c in self.components.values() if c.status == ComponentStatus.FAILED),
                "list": [
                    {
                        "name": c.name,
                        "version": c.version,
                        "status": c.status.value,
                        "last_heartbeat": c.last_heartbeat.isoformat()
                    }
                    for c in self.components.values()
                ]
            },
            "events": {
                "total": len(self.event_history),
                "recent": [
                    {"timestamp": e.timestamp.isoformat(), "state": e.state.value, "message": e.message}
                    for e in self.event_history[-10:]
                ]
            }
        }
    
    async def health_check(self) -> bool:
        """Perform system health check."""
        if self.state == SystemState.ERROR:
            return False
        
        # Check all components
        for component in self.components.values():
            # Components should have heartbeat within 60 seconds
            age = (datetime.now() - component.last_heartbeat).total_seconds()
            if age > 60:
                component.status = ComponentStatus.DEGRADED
        
        return True


# Global engine instance
_engine: Optional[CoreEngine] = None


def get_engine() -> CoreEngine:
    """Get or create global engine instance."""
    global _engine
    if _engine is None:
        _engine = CoreEngine()
    return _engine


async def initialize_system() -> bool:
    """Initialize the system."""
    engine = get_engine()
    return await engine.initialize()


async def shutdown_system() -> None:
    """Shutdown the system."""
    engine = get_engine()
    await engine.shutdown()
