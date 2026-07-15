"""
MAHALAKSMI AIOS v1.0 - Master Application
FastAPI High-Performance Enterprise Application
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import configuration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import settings

# Import all system components
from app.core.engine import get_engine, initialize_system, shutdown_system, SystemState
from app.core.security import get_security_manager, Permission
from app.core.security_ext import (
    SecurityMiddleware, 
    get_crypto, 
    get_jwt_manager, 
    get_license_generator
)
from app.intelligence.gateway import get_gateway
from app.intelligence.memory import get_memory
from app.development.openhands_connector import get_connector
from app.development.testing_center import get_testing_center
from app.business.revenue import get_revenue_manager
from app.business.finance import get_finance_ledger, TransactionType, Category
from app.business.analytics import get_analytics
from app.business.product import get_product_center, ProductType, PricingModel
from app.enterprise.notification import (
    get_notification_center, 
    NotificationPriority, 
    NotificationChannel,
    RevenueNotifier
)
from app.enterprise.hub import get_enterprise_hub, EventType

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ==================== Pydantic Models ====================

class HealthResponse(BaseModel):
    status: str
    version: str
    system_state: str
    uptime_seconds: float


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    provider: str


class RevenueRequest(BaseModel):
    source: str
    amount: float
    payment_method: str = "bank_transfer"


class DisbursementRequest(BaseModel):
    amount: float
    method: str = "bank_transfer"


class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = None


class TaskRequest(BaseModel):
    command: str
    args: Dict[str, Any] = {}


# ==================== Lifespan Management ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("🚀 Starting MAHALAKSMI AIOS v1.0...")
    
    # Initialize core engine
    await initialize_system()
    
    # Start enterprise hub
    hub = get_enterprise_hub()
    await hub.start()
    
    # Start OpenHands connector
    connector = get_connector()
    await connector.start()
    
    logger.info("✅ MAHALAKSMI AIOS Ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MAHALAKSMI AIOS...")
    await connector.stop()
    await hub.stop()
    await shutdown_system()
    logger.info("👋 Shutdown complete")


# ==================== FastAPI Application ====================

app = FastAPI(
    title="MAHALAKSMI AIOS v1.0",
    description="Enterprise AI Operating System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware for logging and injection prevention
app.add_middleware(SecurityMiddleware)


# ==================== Health & Status Endpoints ====================

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint."""
    return {
        "name": "MAHALAKSMI AIOS",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    engine = get_engine()
    status = engine.get_status()
    
    return HealthResponse(
        status="healthy" if status["system"]["state"] == "running" else "degraded",
        version="1.0.0",
        system_state=status["system"]["state"],
        uptime_seconds=status["system"].get("uptime_seconds", 0)
    )


@app.get("/status")
async def get_status():
    """Get comprehensive system status."""
    engine = get_engine()
    gateway = get_gateway()
    connector = get_connector()
    revenue = get_revenue_manager()
    finance = get_finance_ledger()
    hub = get_enterprise_hub()
    
    return {
        "system": engine.get_status(),
        "intelligence": gateway.get_status(),
        "connector": connector.get_status(),
        "revenue": revenue.get_summary(),
        "finance": finance.get_summary(),
        "enterprise": hub.get_status()
    }


# ==================== Authentication Endpoints ====================

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Login and get access token."""
    security = get_security_manager()
    token = security.authenticate(request.username, request.password)
    
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": request.username
    }


@app.get("/auth/users")
async def list_users():
    """List all users."""
    security = get_security_manager()
    return {"users": security.list_users()}


@app.get("/auth/rbac")
async def get_rbac_matrix():
    """Get RBAC permission matrix."""
    security = get_security_manager()
    return {"rbac_matrix": security.get_rbac_matrix()}


# ==================== AI/Intelligence Endpoints ====================

@app.post("/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI."""
    gateway = get_gateway()
    
    response = await gateway.generate(
        prompt=request.message,
        conversation_id=request.conversation_id,
        system_prompt=request.system_prompt
    )
    
    return ChatResponse(
        response=response.content,
        conversation_id=request.conversation_id or gateway.conversations and list(gateway.conversations.keys())[-1] or "",
        provider=response.provider.value
    )


@app.post("/ai/conversation")
async def create_conversation():
    """Create new conversation."""
    gateway = get_gateway()
    conv_id = gateway.create_conversation()
    return {"conversation_id": conv_id}


# ==================== Revenue Endpoints ====================

@app.post("/revenue/record")
async def record_revenue(request: RevenueRequest):
    """Record new revenue."""
    revenue = get_revenue_manager()
    transaction = await revenue.record_digital_revenue(
        source=request.source,
        amount=request.amount,
        payment_method=request.payment_method
    )
    
    # Emit event
    hub = get_enterprise_hub()
    await hub.emit_event(
        EventType.REVENUE_RECEIVED,
        source="revenue_api",
        data={
            "transaction_id": transaction.transaction_id,
            "amount": transaction.amount,
            "ceo_share": transaction.ceo_share
        }
    )
    
    return {
        "status": "recorded",
        "transaction": {
            "id": transaction.transaction_id,
            "amount": transaction.amount,
            "ceo_share": transaction.ceo_share,
            "status": transaction.status.value
        }
    }


@app.post("/revenue/disbursement")
async def request_disbursement(request: DisbursementRequest):
    """Request CEO disbursement."""
    revenue = get_revenue_manager()
    disbursement = await revenue.request_ceo_disbursement(
        amount=request.amount,
        method=request.method
    )
    
    # Emit event
    hub = get_enterprise_hub()
    await hub.emit_event(
        EventType.DISBURSEMENT_COMPLETED,
        source="revenue_api",
        data={
            "request_id": disbursement.request_id,
            "amount": disbursement.amount
        }
    )
    
    return {
        "status": disbursement.status,
        "disbursement": {
            "id": disbursement.request_id,
            "amount": disbursement.amount,
            "transaction_id": disbursement.transaction_id
        }
    }


@app.get("/revenue/summary")
async def get_revenue_summary():
    """Get revenue summary."""
    revenue = get_revenue_manager()
    return revenue.get_summary()


# ==================== Finance Endpoints ====================

@app.get("/finance/balance")
async def get_balance():
    """Get current balance."""
    finance = get_finance_ledger()
    return {"balance": finance.get_balance()}


@app.get("/finance/summary")
async def get_finance_summary(period: str = None):
    """Get finance summary."""
    finance = get_finance_ledger()
    return finance.get_summary(period)


@app.post("/finance/expense")
async def record_expense(
    amount: float,
    description: str,
    category: str = "operations"
):
    """Record expense."""
    finance = get_finance_ledger()
    entry = finance.add_entry(
        TransactionType.EXPENSE,
        Category(category),
        amount,
        description
    )
    return {"entry_id": entry.entry_id, "balance": entry.balance_after}


# ==================== Analytics Endpoints ====================

@app.get("/business/analytics/summary")
async def get_analytics_summary(period_days: int = 30):
    """
    Get comprehensive business analytics summary.
    Returns structured JSON for frontend visualization.
    """
    analytics = get_analytics()
    return analytics.get_summary_json()


@app.get("/business/analytics/distribution")
async def get_distribution():
    """Get 60/40 CEO vs Operational distribution."""
    analytics = get_analytics()
    distribution = analytics.calculate_distribution()
    return {
        "total_revenue": distribution.total_revenue,
        "ceo_share": {
            "amount": distribution.ceo_share,
            "percentage": distribution.ceo_share_percentage,
            "bank": distribution.ceo_bank,
            "account": distribution.ceo_account,
            "holder": distribution.ceo_holder
        },
        "operational_reserve": {
            "amount": distribution.operational_reserve,
            "percentage": distribution.operational_percentage,
            "reinvestment": distribution.reinvestment_allocated,
            "team_bonus": distribution.team_bonus_allocated,
            "csr": distribution.csr_allocated
        }
    }


@app.get("/business/analytics/growth")
async def get_growth_metrics():
    """Get growth velocity metrics."""
    analytics = get_analytics()
    growth = analytics.calculate_growth_metrics()
    return {
        "period_over_period_growth_percent": round(growth.period_over_period_growth, 2),
        "monthly_recurring_revenue": growth.monthly_recurring_revenue,
        "average_transaction_value": growth.average_transaction_value,
        "projected_revenue_30d": growth.projected_revenue_30d,
        "projected_revenue_90d": growth.projected_revenue_90d
    }


@app.get("/business/analytics/burn-rate")
async def get_burn_rate():
    """Get burn rate and runway metrics."""
    analytics = get_analytics()
    burn = analytics.calculate_burn_rate()
    return {
        "monthly_burn_rate": burn.monthly_burn_rate,
        "monthly_revenue_run_rate": burn.monthly_revenue_run_rate,
        "runway_months": round(burn.runway_months, 1),
        "operational_costs": burn.operational_costs,
        "infrastructure_costs": burn.infrastructure_costs,
        "marketing_costs": burn.marketing_costs
    }


# ==================== Memory Endpoints ====================

@app.post("/memory/store")
async def store_memory(
    content: str,
    memory_type: str = "conversation",
    metadata: Optional[Dict] = None
):
    """Store new memory entry."""
    memory = get_memory()
    entry = memory.store(content, memory_type, metadata)
    return {"entry_id": entry.entry_id, "created_at": entry.created_at}


@app.post("/memory/retrieve")
async def retrieve_memory(
    query: str,
    memory_type: Optional[str] = None,
    limit: int = 5
):
    """Retrieve memories similar to query."""
    memory = get_memory()
    entries = memory.retrieve(query, memory_type, limit)
    return {
        "entries": [
            {
                "id": e.entry_id,
                "type": e.memory_type,
                "content": e.content,
                "relevance_score": round(e.relevance_score, 3),
                "created_at": e.created_at
            }
            for e in entries
        ]
    }


@app.get("/memory/stats")
async def get_memory_stats():
    """Get memory system statistics."""
    memory = get_memory()
    return memory.get_stats()


@app.get("/memory/history")
async def get_memory_history(memory_type: str = None, limit: int = 100):
    """Get memory history."""
    memory = get_memory()
    if memory_type:
        entries = memory.storage.get_entries_by_type(memory_type, limit)
    else:
        entries = memory.storage.get_recent_entries(limit)
    return {
        "entries": [
            {
                "id": e.entry_id,
                "type": e.memory_type,
                "content": e.content,
                "access_count": e.access_count,
                "created_at": e.created_at
            }
            for e in entries
        ]
    }


# ==================== Product Center Endpoints ====================

@app.get("/products")
async def list_products():
    """List all available products."""
    product_center = get_product_center()
    return {"products": product_center.list_products()}


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product details."""
    product_center = get_product_center()
    product = product_center.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product_id": product.product_id,
        "name": product.name,
        "description": product.description,
        "type": product.product_type.value,
        "pricing_model": product.pricing_model.value,
        "price": product.price,
        "currency": product.currency,
        "license_duration_days": product.license_duration_days,
        "version": product.version
    }


@app.post("/products/purchase")
async def purchase_product(
    product_id: str,
    customer_id: str,
    customer_name: str,
    customer_email: str,
    payment_amount: float
):
    """
    Purchase product and automatically generate license.
    Links payment to Revenue Engine and generates cryptographic license key.
    """
    product_center = get_product_center()
    
    try:
        result = product_center.purchase_and_activate(
            product_id=product_id,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_email=customer_email,
            payment_amount=payment_amount
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/products/validate-license")
async def validate_license(license_key: str):
    """Validate a license key."""
    product_center = get_product_center()
    result = product_center.validate_license(license_key)
    return result


@app.get("/products/customer/{customer_id}")
async def get_customer_portal(customer_id: str):
    """Get customer dashboard with all licenses."""
    product_center = get_product_center()
    return product_center.get_customer_portal(customer_id)


@app.get("/products/stats")
async def get_product_stats():
    """Get product catalog statistics."""
    product_center = get_product_center()
    return product_center.get_catalog_stats()


# ==================== Security Endpoints ====================

@app.get("/security/audit-log")
async def get_audit_log(limit: int = 100, event_type: str = None):
    """Get security audit log."""
    # This would need to be accessed through the middleware
    # For now, return placeholder
    return {
        "message": "Security audit log available",
        "limit": limit,
        "event_type": event_type
    }


@app.post("/security/encrypt")
async def encrypt_data(data: str):
    """Encrypt data using Fernet."""
    crypto = get_crypto()
    encrypted = crypto.encrypt(data)
    return {"encrypted": encrypted}


@app.post("/security/decrypt")
async def decrypt_data(encrypted_data: str):
    """Decrypt data using Fernet."""
    crypto = get_crypto()
    try:
        decrypted = crypto.decrypt(encrypted_data)
        return {"decrypted": decrypted}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/security/token")
async def create_token(
    user_id: str,
    username: str,
    role: str = "user"
):
    """Create JWT token."""
    jwt_manager = get_jwt_manager()
    token = jwt_manager.create_token({
        "user_id": user_id,
        "username": username,
        "role": role
    })
    return {"access_token": token, "token_type": "bearer"}


@app.post("/security/token/verify")
async def verify_token(token: str):
    """Verify JWT token."""
    jwt_manager = get_jwt_manager()
    payload = jwt_manager.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"valid": True, "payload": payload}


# ==================== OpenHands Connector Endpoints ====================

@app.post("/connector/task")
async def submit_task(request: TaskRequest):
    """Submit execution task."""
    connector = get_connector()
    task = await connector.create_task(request.task_type, request.prompt, request.context)
    return {"task_id": task.task_id, "status": task.status}


@app.get("/connector/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status."""
    connector = get_connector()
    task = connector.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "result": task.result,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }


# ==================== Notification Center Endpoints ====================

@app.post("/notifications/send")
async def send_notification(
    event_type: str,
    title: str,
    message: str,
    priority: str = "normal",
    channels: str = "console"
):
    """
    Send a notification through specified channels.
    Channels: console, webhook, email (comma-separated)
    """
    nc = get_notification_center()
    
    priority_enum = NotificationPriority(priority)
    channel_list = [
        NotificationChannel(c.strip()) 
        for c in channels.split(",")
    ]
    
    notification_id = nc.notify(
        event_type=event_type,
        title=title,
        message=message,
        priority=priority_enum,
        channels=channel_list
    )
    
    return {
        "notification_id": notification_id,
        "status": "queued"
    }


@app.post("/notifications/critical")
async def send_critical_notification(
    event_type: str,
    title: str,
    message: str
):
    """Send critical notification to all channels."""
    nc = get_notification_center()
    
    notification_id = nc.notify_critical(
        event_type=event_type,
        title=title,
        message=message
    )
    
    return {
        "notification_id": notification_id,
        "status": "queued",
        "priority": "critical"
    }


@app.get("/notifications/recent")
async def get_recent_notifications(limit: int = 50):
    """Get recent notifications."""
    nc = get_notification_center()
    return {"notifications": nc.get_recent(limit)}


@app.get("/notifications/stats")
async def get_notification_stats():
    """Get notification statistics."""
    nc = get_notification_center()
    return nc.get_stats()


@app.post("/notifications/immediate")
async def send_immediate_notification(
    title: str,
    message: str,
    channel: str = "console"
):
    """Send immediate notification (bypasses queue)."""
    nc = get_notification_center()
    channel_enum = NotificationChannel(channel)
    
    success = await nc.send_immediate(title, message, channel_enum)
    
    return {
        "success": success,
        "channel": channel
    }


# ==================== Testing Center Endpoints ====================

@app.get("/dev/tests/discover")
async def discover_tests():
    """Discover all available tests."""
    tc = get_testing_center()
    tests = tc.discover_tests()
    return {
        "total_tests": len(tests),
        "tests": [
            {
                "name": t.test_name,
                "file": t.file_path,
                "module": t.module_name
            }
            for t in tests
        ]
    }


@app.post("/dev/diagnostics/run")
async def run_diagnostics(include_health: bool = True):
    """
    Run full diagnostic suite.
    Auto-discovers tests, runs pytest, checks health.
    Returns JSON summary.
    """
    tc = get_testing_center()
    result = await tc.run_diagnostics(include_health)
    
    return tc.get_summary()


@app.get("/dev/diagnostics/summary")
async def get_diagnostics_summary():
    """Get last diagnostic summary."""
    tc = get_testing_center()
    return tc.get_summary()


@app.get("/dev/health")
async def get_quick_health():
    """Quick health check without full test run."""
    tc = get_testing_center()
    return tc.run_quick_health()


# ==================== OpenHands Connector Endpoints (continued) ====================

@app.get("/connector/tasks")
async def list_tasks():
    """List all tasks."""
    connector = get_connector()
    tasks = connector.list_tasks()
    return {"tasks": tasks}


@app.delete("/connector/task/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a task."""
    connector = get_connector()
    success = connector.cancel_task(task_id)
    return {"success": success, "task_id": task_id}


@app.get("/connector/status")
async def get_connector_status():
    """Get connector status."""
    connector = get_connector()
    return connector.get_status()


# ==================== Enterprise Hub Endpoints ====================

@app.get("/enterprise/events")
async def get_events(event_type: str = None, limit: int = 100):
    """Get event history."""
    hub = get_enterprise_hub()
    
    event_enum = None
    if event_type:
        try:
            event_enum = EventType(event_type)
        except ValueError:
            pass
    
    return {
        "events": hub.pubsub.get_event_history(event_enum, limit)
    }


@app.get("/enterprise/subscriptions")
async def get_subscriptions():
    """Get active subscriptions."""
    hub = get_enterprise_hub()
    return {"subscriptions": hub.pubsub.get_subscriptions()}


# ==================== Debug Endpoints ====================

@app.post("/debug/seed")
async def seed_demo_data():
    """Seed demo data for testing."""
    revenue = get_revenue_manager()
    finance = get_finance_ledger()
    
    # Record demo revenue
    await revenue.record_digital_revenue(
        source="digital_products",
        amount=417900145,
        payment_method="qris"
    )
    
    # Record some expenses
    finance.record_cost("OpenAI API", 150000, "2026-07")
    finance.record_cost("Vercel Hosting", 250000, "2026-07")
    finance.add_entry(TransactionType.EXPENSE, Category.MARKETING, 500000, "Marketing campaign")
    
    return {"status": "Demo data seeded"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
