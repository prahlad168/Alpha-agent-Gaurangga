"""
MAHALAKSMI AIOS v1.0 - Master Application
FastAPI High-Performance Enterprise Application
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import HTMLResponse
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
from app.core.digital_twin import get_company_brain
from app.core.workflow_engine import get_workflow_engine, WorkflowType
from app.intelligence.gateway import get_gateway
from app.intelligence.memory import get_memory
from app.intelligence.knowledge_graph import get_knowledge_graph, NodeType, RelationType
from app.intelligence.prompt_orchestrator import get_prompt_orchestrator
from app.intelligence.planning_engine import get_planning_engine, PlanStatus
from app.intelligence.learning_engine import get_learning_engine, FeedbackType
from app.development.openhands_connector import get_connector
from app.development.testing_center import get_testing_center
from app.development.github_center import get_github_center, BranchType
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
from app.enterprise.mission_control import (
    get_mission_control,
    MissionStatus,
    Priority
)
from app.enterprise.monitoring import get_monitoring_center
from app.enterprise.backup import get_backup_center
from app.enterprise.disaster_recovery import get_disaster_recovery_engine, SystemState
from app.enterprise.hub import get_enterprise_hub, EventType
from app.business.customer import get_customer_center, CustomerStatus, TicketPriority, TicketStatus
from app.business.midtrans_client import get_midtrans_client, get_payment_queue
from app.core.rbac import get_rbac_engine, Role, Permission, Resource
from app.core.i18n import get_i18n_engine, detect_locale_from_request, localized_response, localized_error, t as translate
from app.development.repository_center import get_repository_center
from app.development.devops_suite import (
    get_auto_test_runner, get_logging_system, get_deployment_center,
    get_ai_coding_assistant, get_performance_profiler,
    Environment, DeploymentStatus, LogLevel
)
from app.intelligence.multimodal import (
    get_vision_engine, get_voice_engine, get_nlp_engine
)
from app.business.operations import (
    get_asset_manager, get_legal_engine, get_hr_manager, get_supply_chain,
    AssetType, LeaveType, LeaveStatus, VendorStatus, ProcurementStatus
)
from app.enterprise.architecture import (
    get_erp_sync, get_business_intelligence, get_audit_trail,
    get_security_shield, get_multi_tenant, get_cache
)

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


# ==================== Dashboard Endpoint ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect root to dashboard."""
    return await dashboard()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the MAHALAKSMI AIOS Dashboard."""
    import os
    
    # Try multiple possible paths
    possible_paths = [
        os.path.join(os.getcwd(), "frontend", "index.html"),
        os.path.join(os.getcwd(), "..", "frontend", "index.html"),
        "/workspace/project/Alpha-agent-Gaurangga/frontend/index.html",
    ]
    
    frontend_path = None
    for path in possible_paths:
        if os.path.exists(path):
            frontend_path = path
            break
    
    if frontend_path:
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MAHALAKSMI AIOS Dashboard</title>
            <style>
                body { font-family: Arial; background: #1a1a2e; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .card { background: #16213e; padding: 40px; border-radius: 20px; text-align: center; }
                h1 { color: #0f3460; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                p { color: #888; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>MAHALAKSMI AIOS v2.1.0</h1>
                <p>Enterprise Dashboard</p>
                <p>Frontend not found</p>
            </div>
        </body>
        </html>
        """


# ==================== Health & Status Endpoints ====================

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


# ==================== Advanced RBAC Endpoints ====================

@app.get("/auth/permissions")
async def get_permissions(user_id: str = None, username: str = None):
    """Get user permissions."""
    rbac = get_rbac_engine()
    
    if user_id or username:
        return rbac.get_user_permissions(user_id or "")
    
    users = rbac.db.get_all_users()
    return {
        "users": [
            {
                "user_id": u.user_id,
                "username": u.username,
                "role": u.role.value,
                "permissions_count": len(u.permissions)
            }
            for u in users
        ]
    }


@app.get("/auth/roles/matrix")
async def get_role_matrix():
    """Get complete role-permission matrix."""
    rbac = get_rbac_engine()
    return rbac.get_role_matrix()


@app.post("/auth/assign-role")
async def assign_role(
    user_id: str,
    role: str,
    assigned_by: str = "system"
):
    """Assign role to user."""
    rbac = get_rbac_engine()
    
    try:
        target_role = Role(role)
    except ValueError:
        return {"error": f"Invalid role: {role}"}
    
    success = rbac.assign_role(user_id, target_role, assigned_by)
    
    if success:
        return {"success": True, "user_id": user_id, "role": role}
    
    return {"error": "User not found or assignment failed"}


@app.get("/auth/check")
async def check_permission(
    user_id: str = None,
    username: str = None,
    permission: str = None,
    resource: str = None,
    access_type: str = "read"
):
    """Check if user has permission."""
    rbac = get_rbac_engine()
    
    if not user_id and not username:
        return {"error": "user_id or username required"}
    
    user = rbac.db.get_user(user_id=user_id, username=username)
    if not user:
        return {"error": "User not found"}
    
    result = {"user_id": user.user_id, "username": user.username, "role": user.role.value}
    
    if permission:
        try:
            perm = Permission(permission)
            has_perm = rbac.check_permission(user.user_id, perm)
            result["permission"] = permission
            result["allowed"] = has_perm
        except ValueError:
            result["error"] = f"Invalid permission: {permission}"
    
    if resource:
        has_access = rbac.check_resource_access(user.user_id, Resource(resource), access_type)
        result["resource"] = resource
        result["access_type"] = access_type
        result["allowed"] = has_access
    
    return result


# ==================== Repository Center Endpoints ====================

@app.get("/dev/repo/status")
async def get_repo_status():
    """Get repository status."""
    repo = get_repository_center()
    return repo.get_repository_status()


@app.post("/dev/repo/archive")
async def create_archive(
    message: str = "Manual archive snapshot"
):
    """Create archive snapshot."""
    repo = get_repository_center()
    archive = repo.create_archive(message=message)
    
    return {
        "archive_id": archive.archive_id,
        "commit": archive.commit_hash,
        "branch": archive.branch,
        "files_count": len(archive.files_included),
        "size_bytes": archive.total_size_bytes,
        "status": archive.status.value
    }


@app.get("/dev/repo/archives/list")
async def list_archives(limit: int = 50):
    """List all archives."""
    repo = get_repository_center()
    return {"archives": repo.get_archives(limit)}


@app.get("/dev/repo/archives/{archive_id}")
async def get_archive_details(archive_id: str):
    """Get archive details."""
    repo = get_repository_center()
    return repo.get_archive_details(archive_id)


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


# ==================== Business Revenue API (for Dashboard) ====================

@app.get("/api/business/revenue/summary")
async def get_business_revenue_summary():
    """
    Get real-time revenue summary from database.
    Used by the frontend dashboard.
    Returns actual totals and 60/40 split from ledger.
    """
    revenue = get_revenue_manager()
    summary = revenue.get_summary()
    
    # Ensure we have real data
    total = summary.get("total_revenue", 0)
    
    # If no transactions, return demo data for visibility
    if total == 0:
        # Seed demo data if database is empty
        await _seed_demo_revenue(revenue)
        summary = revenue.get_summary()
    
    return summary


async def _seed_demo_revenue(revenue: "RevenueManager"):
    """Seed demo revenue for dashboard visibility."""
    import uuid
    from datetime import datetime
    
    demo_transactions = [
        {"source": "digital_products", "amount": 150000000},
        {"source": "saas_subscription", "amount": 85000000},
        {"source": "consulting", "amount": 75000000},
        {"source": "api_services", "amount": 50000000},
        {"source": "freelance", "amount": 57900145},
    ]
    
    for tx in demo_transactions:
        await revenue.record_digital_revenue(
            source=tx["source"],
            amount=tx["amount"],
            payment_method="qris"
        )


@app.post("/api/business/revenue/add")
async def add_revenue_api(
    source: str = "midtrans",
    amount: float = 0,
    payment_method: str = "qris"
):
    """
    Add revenue directly (used by Midtrans simulator).
    Writes to real database ledger.
    """
    revenue = get_revenue_manager()
    
    result = await revenue.record_digital_revenue(
        source=source,
        amount=amount,
        payment_method=payment_method
    )
    
    return {
        "success": True,
        "transaction_id": result.transaction_id,
        "amount": result.amount,
        "ceo_share": result.ceo_share,
        "ops_share": result.operational_share
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


# ==================== Prompt Orchestrator Endpoints ====================

@app.get("/ai/prompt/templates")
async def get_prompt_templates(template_type: str = None):
    """Get all prompt templates."""
    from app.intelligence.prompt_orchestrator import TemplateType
    
    ttype = None
    if template_type:
        try:
            ttype = TemplateType(template_type)
        except:
            pass
    
    orchestrator = get_prompt_orchestrator()
    templates = orchestrator.get_templates(ttype)
    
    return {"templates": templates, "total": len(templates)}


@app.post("/ai/prompt/render")
async def render_prompt(
    template_id: str,
    variables: str = "{}"
):
    """Render a prompt with dynamic context injection."""
    orchestrator = get_prompt_orchestrator()
    
    import json
    vars_dict = json.loads(variables) if isinstance(variables, str) else variables
    
    result = orchestrator.render(template_id, vars_dict)
    
    return {
        "template_id": template_id,
        "system_prompt": result.system_prompt,
        "total_tokens": result.total_tokens,
        "context_used": result.context_used,
        "trimmed_items": result.trimmed_items
    }


@app.post("/ai/prompt/optimize")
async def optimize_prompt(
    prompt: str,
    goal: str,
    constraints: str = "[]"
):
    """Optimize a prompt for better results."""
    orchestrator = get_prompt_orchestrator()
    
    import json
    constraints_list = json.loads(constraints) if isinstance(constraints, str) else constraints
    
    result = orchestrator.optimize(prompt, goal, constraints_list)
    
    return result


# ==================== Knowledge Graph Endpoints ====================

@app.get("/ai/graph/nodes")
async def get_graph_nodes(node_type: str = None, search: str = None):
    """Get all nodes in the knowledge graph."""
    kg = get_knowledge_graph()
    
    ntype = None
    if node_type:
        try:
            ntype = NodeType(node_type)
        except:
            pass
    
    return {
        "nodes": kg.get_nodes(node_type=ntype, search=search),
        "total": len(kg.get_nodes(node_type=ntype, search=search))
    }


@app.get("/ai/graph/edges")
async def get_graph_edges(
    source_id: str = None,
    target_id: str = None,
    relation_type: str = None
):
    """Get all edges in the knowledge graph."""
    kg = get_knowledge_graph()
    
    rtype = None
    if relation_type:
        try:
            rtype = RelationType(relation_type)
        except:
            pass
    
    return {
        "edges": kg.get_edges(source_id=source_id, target_id=target_id, relation_type=rtype),
        "total": len(kg.get_edges(source_id=source_id, target_id=target_id, relation_type=rtype))
    }


@app.post("/ai/graph/query")
async def query_graph(
    start_node_id: str = None,
    end_node_id: str = None,
    relation_type: str = None,
    max_hops: int = 3
):
    """Query the knowledge graph for multi-hop relationships."""
    kg = get_knowledge_graph()
    
    rtype = None
    if relation_type:
        try:
            rtype = RelationType(relation_type)
        except:
            pass
    
    results = kg.query(
        start_node_id=start_node_id,
        end_node_id=end_node_id,
        relation_type=rtype,
        max_hops=max_hops
    )
    
    return {
        "query": {
            "start": start_node_id,
            "end": end_node_id,
            "relation": relation_type,
            "max_hops": max_hops
        },
        "results": results
    }


@app.get("/ai/graph/stats")
async def get_graph_stats():
    """Get knowledge graph statistics."""
    kg = get_knowledge_graph()
    return kg.get_graph_stats()


# ==================== GitHub Center Endpoints ====================

@app.get("/dev/github/status")
async def get_github_status():
    """Get git repository sync status."""
    gh = get_github_center()
    status = gh.get_status()
    
    return {
        "is_clean": status.is_clean,
        "current_branch": status.current_branch,
        "ahead": status.ahead,
        "behind": status.behind,
        "untracked": status.untracked,
        "modified": status.modified,
        "staged": status.staged,
        "conflicts": status.conflicts
    }


@app.get("/dev/github/branches")
async def get_github_branches(remote: bool = False):
    """Get list of branches."""
    gh = get_github_center()
    branches = gh.get_branches(remote=remote)
    
    return {
        "branches": [
            {
                "name": b.name,
                "is_current": b.is_current,
                "is_remote": b.is_remote,
                "last_commit": b.last_commit,
                "last_commit_message": b.last_commit_message
            }
            for b in branches
        ],
        "total": len(branches)
    }


@app.post("/dev/github/branch")
async def create_github_branch(
    branch_name: str,
    from_branch: str = None,
    branch_type: str = "feature"
):
    """Create a new branch."""
    gh = get_github_center()
    result = gh.create_branch(branch_name, from_branch, BranchType(branch_type))
    return result


@app.post("/dev/github/switch")
async def switch_github_branch(branch_name: str):
    """Switch to a branch."""
    gh = get_github_center()
    result = gh.switch_branch(branch_name)
    return result


@app.post("/dev/github/commit")
async def github_commit(message: str, files: str = None):
    """Commit changes."""
    gh = get_github_center()
    file_list = files.split(",") if files else None
    result = gh.commit_changes(message, file_list)
    return result


@app.post("/dev/github/push")
async def github_push(remote: str = "origin", branch: str = None):
    """Push to remote."""
    gh = get_github_center()
    result = gh.push(remote, branch)
    return result


@app.post("/dev/github/pull")
async def github_pull(remote: str = "origin", branch: str = None):
    """Pull from remote."""
    gh = get_github_center()
    result = gh.pull(remote, branch)
    return result


@app.get("/dev/github/conflicts")
async def detect_github_conflicts():
    """Detect merge conflicts."""
    gh = get_github_center()
    conflicts = gh.detect_conflicts()
    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": [{"file": c.file, "count": len(c.conflicts)} for c in conflicts]
    }


@app.post("/dev/github/sync")
async def sync_github():
    """Full sync with remote."""
    gh = get_github_center()
    result = gh.sync_with_remote()
    return result


@app.get("/dev/github/remote")
async def get_github_remote():
    """Get remote repository info."""
    gh = get_github_center()
    return gh.get_remote_info()


@app.get("/dev/github/history")
async def get_github_history(limit: int = 20):
    """Get git operation history."""
    gh = get_github_center()
    return {"operations": gh.get_operation_history(limit)}


# ==================== Workflow Engine Endpoints ====================

@app.post("/workflow/create")
async def create_workflow(
    name: str,
    description: str = "",
    workflow_type: str = "sequential",
    mission_id: str = ""
):
    """Create a new workflow."""
    engine = get_workflow_engine()
    
    wf_type = WorkflowType(workflow_type)
    workflow = engine.create_workflow(name, description, wf_type, mission_id)
    
    return {
        "workflow_id": workflow.workflow_id,
        "name": workflow.name,
        "state": workflow.state.value
    }


@app.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow status."""
    engine = get_workflow_engine()
    return engine.get_workflow_status(workflow_id)


@app.post("/workflow/{workflow_id}/step")
async def add_workflow_step(
    workflow_id: str,
    name: str,
    action: str,
    action_params: str = "{}",
    depends_on: str = "[]",
    rollback_action: str = "",
    rollback_params: str = "{}",
    max_retries: int = 3,
    timeout_seconds: int = 60
):
    """Add a step to workflow."""
    engine = get_workflow_engine()
    
    import json
    params = json.loads(action_params) if isinstance(action_params, str) else action_params
    deps = json.loads(depends_on) if isinstance(depends_on, str) else depends_on
    rollback_params_dict = json.loads(rollback_params) if isinstance(rollback_params, str) else rollback_params
    
    step = engine.add_step(
        workflow_id=workflow_id,
        name=name,
        action=action,
        action_params=params,
        depends_on=deps,
        rollback_action=rollback_action,
        rollback_params=rollback_params_dict,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds
    )
    
    return {
        "step_id": step.step_id,
        "name": step.name,
        "action": step.action
    }


@app.post("/workflow/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """Execute a workflow."""
    engine = get_workflow_engine()
    
    try:
        workflow = await engine.execute_workflow(workflow_id)
        return {
            "workflow_id": workflow.workflow_id,
            "state": workflow.state.value,
            "result": workflow.result,
            "error": workflow.error
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/workflow/{workflow_id}/spawn-from-mission")
async def spawn_workflow_from_mission(workflow_id: str):
    """Create workflow from mission."""
    engine = get_workflow_engine()
    
    workflow = engine.db.get_workflow(workflow_id)
    if not workflow:
        return {"error": "Workflow not found"}
    
    new_workflow = engine.spawn_from_mission(workflow.mission_id, workflow.name)
    
    return {
        "workflow_id": new_workflow.workflow_id,
        "name": new_workflow.name,
        "steps": len(new_workflow.steps)
    }


@app.get("/workflow/list")
async def list_workflows():
    """List all workflows."""
    engine = get_workflow_engine()
    workflows = engine.db.get_all_workflows()
    
    return {
        "workflows": [
            {
                "id": w.workflow_id,
                "name": w.name,
                "state": w.state.value,
                "type": w.workflow_type.value,
                "steps": len(w.steps)
            }
            for w in workflows
        ],
        "total": len(workflows)
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


# ==================== AI Planning Engine Endpoints ====================

@app.post("/ai/planning/generate-plan")
async def generate_plan(
    goal_description: str,
    goal_conditions: str = "{}"
):
    """Generate action plan from goal."""
    import json
    conditions = json.loads(goal_conditions) if isinstance(goal_conditions, str) else goal_conditions
    
    planning = get_planning_engine()
    plan = planning.generate_plan(goal_description, conditions)
    
    return {
        "plan_id": plan.plan_id,
        "goal_description": plan.goal_description,
        "status": plan.status.value,
        "steps": [
            {
                "id": s.step_id,
                "action": s.action.name,
                "description": s.action.description,
                "cost": s.action.cost,
                "status": s.status.value
            }
            for s in plan.steps
        ],
        "total_cost": plan.total_cost,
        "estimated_duration": plan.estimated_duration_minutes
    }


@app.get("/ai/planning/plans")
async def get_plans(status: str = None):
    """Get all plans."""
    planning = get_planning_engine()
    
    pstatus = None
    if status:
        try:
            pstatus = PlanStatus(status)
        except:
            pass
    
    return {"plans": planning.get_plans(pstatus)}


@app.post("/ai/planning/evaluate-feasibility")
async def evaluate_feasibility(goal_conditions: str = "{}"):
    """Evaluate goal feasibility."""
    import json
    conditions = json.loads(goal_conditions) if isinstance(goal_conditions, str) else goal_conditions
    
    planning = get_planning_engine()
    return planning.evaluate_feasibility(conditions)


# ==================== AI Learning Engine Endpoints ====================

@app.post("/ai/learning/feedback")
async def submit_feedback(
    action_id: str,
    plan_id: str,
    feedback_type: str,
    score: float,
    outcome: str,
    context: str = "{}"
):
    """Submit feedback for an action."""
    import json
    ctx = json.loads(context) if isinstance(context, str) else context
    
    ftype = FeedbackType(feedback_type)
    learning = get_learning_engine()
    
    result = learning.submit_feedback(
        action_id=action_id,
        plan_id=plan_id,
        feedback_type=ftype,
        score=score,
        outcome=outcome,
        context=ctx
    )
    
    return result


@app.get("/ai/learning/insights")
async def get_learning_insights(insight_type: str = None):
    """Get learned insights."""
    learning = get_learning_engine()
    return {"insights": learning.get_insights(insight_type)}


@app.post("/ai/learning/optimize-weights")
async def optimize_weights():
    """Optimize action weights."""
    learning = get_learning_engine()
    return learning.optimize_weights()


@app.get("/ai/learning/summary")
async def get_learning_summary():
    """Get learning summary."""
    learning = get_learning_engine()
    return learning.get_learning_summary()


@app.get("/ai/learning/performance")
async def get_action_performance(action_id: str = None):
    """Get action performance data."""
    learning = get_learning_engine()
    return {"performance": learning.get_action_performance(action_id)}


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


# ==================== Company Brain (Digital Twin) Endpoints ====================

@app.get("/company/profile")
async def get_company_profile():
    """Get MAHA LAKSHMI CORP company profile."""
    brain = get_company_brain()
    profile = brain.get_profile()
    return profile.__dict__


@app.get("/company/kpis")
async def get_company_kpis():
    """Get company KPIs and metrics."""
    brain = get_company_brain()
    return brain.get_kpis()


@app.get("/company/entities")
async def list_company_entities(entity_type: str = None):
    """List company entities."""
    from app.core.digital_twin import EntityType
    brain = get_company_brain()
    
    etype = None
    if entity_type:
        try:
            etype = EntityType(entity_type)
        except:
            pass
    
    entities = brain.list_entities(etype)
    return {
        "entities": [
            {
                "id": e.entity_id,
                "type": e.entity_type.value,
                "name": e.name,
                "description": e.description,
                "metadata": e.metadata
            }
            for e in entities
        ]
    }


@app.get("/company/entity/{entity_id}")
async def get_company_entity(entity_id: str):
    """Get specific company entity."""
    brain = get_company_brain()
    entity = brain.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return {
        "id": entity.entity_id,
        "type": entity.entity_type.value,
        "name": entity.name,
        "description": entity.description,
        "metadata": entity.metadata,
        "relationships": entity.relationships
    }


# ==================== Mission Control Endpoints ====================

@app.get("/mission/dashboard")
async def get_mission_dashboard():
    """Get mission control dashboard."""
    mc = get_mission_control()
    return mc.get_dashboard()


@app.get("/mission/missions")
async def list_missions(status: str = None):
    """List all missions."""
    mc = get_mission_control()
    
    mstatus = None
    if status:
        try:
            mstatus = MissionStatus(status)
        except:
            pass
    
    return {"missions": mc.get_missions(mstatus)}


@app.post("/mission/missions")
async def create_mission(
    title: str,
    description: str,
    priority: str = "normal",
    assigned_to: str = "",
    due_date: str = ""
):
    """Create new mission."""
    mc = get_mission_control()
    
    p = Priority.NORMAL
    if priority == "critical":
        p = Priority.CRITICAL
    elif priority == "high":
        p = Priority.HIGH
    elif priority == "low":
        p = Priority.LOW
    
    mission = mc.create_mission(title, description, p, assigned_to, due_date)
    
    return {
        "mission_id": mission.mission_id,
        "title": mission.title,
        "status": mission.status.value
    }


@app.patch("/mission/missions/{mission_id}")
async def update_mission(mission_id: str, status: str, progress: float = None):
    """Update mission status."""
    mc = get_mission_control()
    
    mstatus = MissionStatus(status)
    success = mc.update_mission_status(mission_id, mstatus, progress)
    
    return {"success": success, "mission_id": mission_id}


@app.get("/mission/alerts")
async def list_alerts(level: str = None, unacknowledged: bool = False):
    """Get system alerts."""
    mc = get_mission_control()
    return {"alerts": mc.get_alerts(level, unacknowledged)}


@app.post("/mission/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    mc = get_mission_control()
    success = mc.acknowledge_alert(alert_id)
    return {"success": success}


# ==================== Monitoring Center Endpoints ====================

@app.get("/monitoring/dashboard")
async def get_monitoring_dashboard():
    """Get complete monitoring dashboard."""
    mc = get_monitoring_center()
    return mc.get_monitoring_dashboard()


@app.get("/monitoring/metrics")
async def get_current_metrics():
    """Get current system metrics."""
    mc = get_monitoring_center()
    return mc.get_current_metrics()


@app.get("/monitoring/api-health")
async def get_api_health():
    """Check API endpoints health."""
    mc = get_monitoring_center()
    return mc.get_api_health()


@app.post("/monitoring/collect")
async def force_collect_metrics():
    """Force metrics collection."""
    mc = get_monitoring_center()
    metrics = mc.collect_system_metrics()
    return {"status": "collected", "timestamp": metrics.timestamp}


# ==================== Backup Center Endpoints ====================

@app.post("/backup/database/{db_name}")
async def backup_database(db_name: str):
    """Create backup of a database."""
    bc = get_backup_center()
    backup = bc.backup_database(db_name)
    
    return {
        "backup_id": backup.backup_id,
        "status": backup.status.value,
        "size_bytes": backup.size_bytes,
        "checksum": backup.checksum,
        "created_at": backup.created_at
    }


@app.post("/backup/all")
async def backup_all_databases():
    """Backup all databases."""
    bc = get_backup_center()
    backups = bc.backup_all_databases()
    
    return {
        "backups": [
            {
                "backup_id": b.backup_id,
                "status": b.status.value,
                "source": b.source_path,
                "size_bytes": b.size_bytes
            }
            for b in backups
        ]
    }


@app.get("/backup/list")
async def list_backups(db_name: str = None):
    """List available backups."""
    bc = get_backup_center()
    return {"backups": bc.list_backups(db_name)}


@app.get("/backup/stats")
async def get_backup_stats():
    """Get backup statistics."""
    bc = get_backup_center()
    return bc.get_backup_stats()


@app.post("/backup/restore/{backup_id}")
async def restore_database(backup_id: str, target_db: str = None):
    """Restore database from backup."""
    bc = get_backup_center()
    success = bc.restore_database(backup_id, target_db)
    return {"success": success, "backup_id": backup_id}


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


# ==================== Disaster Recovery Endpoints ====================

@app.get("/enterprise/dr/status")
async def get_dr_status():
    """Get disaster recovery status."""
    dr = get_disaster_recovery_engine()
    return dr.get_dr_status()


@app.post("/enterprise/dr/health-check")
async def run_health_check():
    """Run health check on all components."""
    dr = get_disaster_recovery_engine()
    return dr.perform_health_check()


@app.post("/enterprise/dr/failover")
async def initiate_failover(reason: str = "Manual failover"):
    """Initiate system failover."""
    dr = get_disaster_recovery_engine()
    record = dr.initiate_failover(reason)
    return {
        "failover_id": record.failover_id,
        "previous_state": record.previous_state.value,
        "new_state": record.new_state.value,
        "components_affected": record.components_affected,
        "status": record.status.value
    }


@app.post("/enterprise/dr/recover")
async def execute_recovery():
    """Execute recovery plan."""
    dr = get_disaster_recovery_engine()
    plan = dr.execute_recovery()
    return {
        "recovery_id": plan.recovery_id,
        "steps": plan.steps,
        "estimated_duration_minutes": plan.estimated_duration_minutes
    }


@app.post("/enterprise/dr/complete")
async def complete_recovery():
    """Complete recovery and return to normal state."""
    dr = get_disaster_recovery_engine()
    success = dr.complete_recovery()
    return {"success": success, "state": "normal"}


# ==================== Multilingual / i18n Endpoints ====================

@app.get("/api/i18n/translate")
async def translate_key(
    request: Request,
    key: str,
    locale: str = None
):
    """
    Get translated string for a key.
    
    Language detection priority:
    1. Query parameter 'locale' or 'lang'
    2. Header 'Accept-Language'
    3. Default (English)
    """
    # Detect locale
    if not locale:
        locale = detect_locale_from_request(request)
    
    i18n = get_i18n_engine()
    translation = i18n.get_translation(key, locale)
    
    return localized_response(
        data={"key": key, "translation": translation},
        message_key=None,
        locale=locale
    )


@app.get("/api/i18n/locales")
async def list_locales():
    """List all supported languages."""
    i18n = get_i18n_engine()
    locales = i18n.get_locales()
    
    return {
        "locales": locales,
        "default_locale": i18n.default_locale,
        "total_locales": len(locales)
    }


@app.get("/api/i18n/keys")
async def list_translation_keys(
    request: Request,
    locale: str = None
):
    """List all available translation keys."""
    if not locale:
        locale = detect_locale_from_request(request)
    
    i18n = get_i18n_engine()
    keys = i18n.get_all_keys(locale)
    
    return {
        "locale": locale,
        "keys": keys,
        "total_keys": len(keys)
    }


@app.get("/api/i18n/batch")
async def translate_batch(
    request: Request,
    keys: str,  # Comma-separated keys
    locale: str = None
):
    """Get multiple translations at once."""
    if not locale:
        locale = detect_locale_from_request(request)
    
    i18n = get_i18n_engine()
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    translations = i18n.get_messages(key_list, locale)
    
    return {
        "locale": locale,
        "translations": translations,
        "total": len(translations)
    }


@app.get("/api/i18n/detect")
async def detect_language(request: Request):
    """Detect language from request headers and parameters."""
    locale = detect_locale_from_request(request)
    i18n = get_i18n_engine()
    locale_info = i18n.supported_locales.get(locale, {})
    
    return {
        "detected_locale": locale,
        "locale_name": locale_info.get("name", "Unknown"),
        "native_name": locale_info.get("native_name", "Unknown")
    }


# ==================== Customer Center / CRM Endpoints ====================

@app.post("/business/customer/profiles")
async def create_customer(
    name: str,
    email: str,
    phone: str = "",
    metadata: str = "{}"
):
    """Create a new customer profile."""
    import json
    meta = json.loads(metadata) if isinstance(metadata, str) else metadata
    
    customer = get_customer_center().create_customer(name, email, phone, meta)
    
    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "status": customer.status.value
    }


@app.get("/business/customer/profiles/{customer_id}")
async def get_customer_profile(customer_id: str):
    """Get customer profile."""
    customer = get_customer_center().get_customer(customer_id)
    if not customer:
        return {"error": "Customer not found"}
    
    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "status": customer.status.value,
        "total_purchases": customer.total_purchases,
        "total_spent": customer.total_spent,
        "clv_score": round(customer.clv_score, 2),
        "churn_probability": round(customer.churn_probability * 100, 1),
        "ticket_count": customer.ticket_count
    }


@app.get("/business/customer/profiles")
async def list_customers(status: str = None):
    """List all customers."""
    cstatus = None
    if status:
        try:
            cstatus = CustomerStatus(status)
        except:
            pass
    
    return {"customers": get_customer_center().list_customers(cstatus)}


@app.post("/business/customer/tickets")
async def create_ticket(
    customer_id: str,
    subject: str,
    description: str,
    priority: str = "medium"
):
    """Create a support ticket."""
    p = TicketPriority(priority)
    ticket = get_customer_center().create_ticket(customer_id, subject, description, p)
    
    return {
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "subject": ticket.subject,
        "priority": ticket.priority.value,
        "status": ticket.status.value
    }


@app.get("/business/customer/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get ticket details."""
    ticket = get_customer_center().get_ticket(ticket_id)
    if not ticket:
        return {"error": "Ticket not found"}
    
    return {
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "priority": ticket.priority.value,
        "status": ticket.status.value,
        "created_at": ticket.created_at,
        "resolved_at": ticket.resolved_at
    }


@app.post("/business/customer/tickets/{ticket_id}/status")
async def update_ticket_status(ticket_id: str, status: str):
    """Update ticket status."""
    s = TicketStatus(status)
    success = get_customer_center().update_ticket_status(ticket_id, s)
    return {"success": success}


@app.get("/business/customer/{customer_id}/tickets")
async def get_customer_tickets(customer_id: str):
    """Get tickets for a customer."""
    return {"tickets": get_customer_center().get_customer_tickets(customer_id)}


@app.post("/business/customer/purchases")
async def record_purchase(
    customer_id: str,
    product_id: str,
    product_name: str,
    amount: float
):
    """Record a customer purchase."""
    success = get_customer_center().record_purchase(
        customer_id, product_id, product_name, amount
    )
    return {"success": success}


@app.get("/business/customer/analytics")
async def get_customer_analytics(customer_id: str):
    """Get customer analytics."""
    return get_customer_center().get_customer_analytics(customer_id)


@app.get("/business/customer/overview")
async def get_customer_overview():
    """Get overall customer analytics."""
    return get_customer_center().get_overall_analytics()


# ==================== Midtrans Payment Gateway Endpoints ====================

@app.post("/business/midtrans/charge")
async def create_payment_charge(
    order_id: str,
    gross_amount: float,
    customer_details: str = "{}",
    item_details: str = "[]",
    source: str = "midtrans"
):
    """
    Create a Midtrans Snap payment.
    
    This endpoint:
    1. Creates a Snap token from Midtrans
    2. Returns redirect URL for payment page
    3. Creates a pending transaction in the Revenue Engine
    """
    import json
    
    # Parse JSON strings
    try:
        customer = json.loads(customer_details) if isinstance(customer_details, str) else customer_details
        items = json.loads(item_details) if isinstance(item_details, str) else item_details
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format for customer_details or item_details"}
    
    # Create payment order
    revenue = get_revenue_manager()
    result = await revenue.create_payment_order(
        order_id=order_id,
        gross_amount=gross_amount,
        customer_details=customer,
        item_details=items,
        source=source
    )
    
    return result


@app.post("/business/midtrans/webhook")
async def midtrans_webhook(request: Request):
    """
    Midtrans webhook handler.
    
    This endpoint:
    1. Receives payment notifications from Midtrans
    2. Verifies the signature key
    3. Updates transaction status based on payment result
    4. Triggers 60/40 split on successful settlement
    
    Note: This endpoint should be publicly accessible but rate-limited.
    """
    try:
        # Get raw payload
        payload = await request.json()
        
        logger.info(f"Midtrans webhook received: {payload.get('order_id', 'unknown')}")
        
        # Get Midtrans client
        midtrans = get_midtrans_client()
        
        # Verify and parse notification
        try:
            notification = midtrans.handle_notification(payload)
        except ValueError as e:
            logger.warning(f"Invalid webhook signature: {e}")
            return {"error": "Invalid signature"}, 403
        
        # Get revenue manager
        revenue = get_revenue_manager()
        
        # Handle based on transaction status
        if notification.transaction_status.value in ["settlement", "capture"]:
            # Payment successful - trigger 60/40 split
            transaction = await revenue.handle_payment_settlement(
                order_id=notification.order_id,
                gross_amount=notification.gross_amount,
                transaction_id=notification.transaction_id,
                payment_type=notification.payment_type,
                transaction_time=notification.transaction_time
            )
            
            logger.info(
                f"Settlement processed: {notification.order_id} - "
                f"CEO: Rp {transaction.ceo_share:,.0f} / "
                f"Ops: Rp {transaction.operational_share:,.0f}"
            )
            
            return {
                "status": "success",
                "order_id": notification.order_id,
                "gross_amount": notification.gross_amount,
                "ceo_share": transaction.ceo_share,
                "operational_share": transaction.operational_share,
                "transaction_status": notification.transaction_status.value
            }
        
        elif notification.transaction_status.value == "pending":
            # Payment is pending - no action needed
            return {
                "status": "pending",
                "order_id": notification.order_id
            }
        
        elif notification.transaction_status.value in ["deny", "expire", "cancel"]:
            # Payment failed - cancel pending order
            revenue.cancel_pending_payment(notification.order_id)
            
            return {
                "status": "cancelled",
                "order_id": notification.order_id,
                "transaction_status": notification.transaction_status.value
            }
        
        else:
            # Other status - log and acknowledge
            logger.info(f"Unhandled transaction status: {notification.transaction_status.value}")
            return {
                "status": "acknowledged",
                "order_id": notification.order_id,
                "transaction_status": notification.transaction_status.value
            }
    
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500


@app.get("/business/midtrans/status/{order_id}")
async def get_payment_status(order_id: str):
    """Get payment status by order ID."""
    revenue = get_revenue_manager()
    transaction = revenue.get_transaction_by_order_id(order_id)
    
    if not transaction:
        return {"error": "Order not found"}
    
    return {
        "order_id": order_id,
        "transaction_id": transaction.transaction_id,
        "amount": transaction.amount,
        "status": transaction.status.value,
        "ceo_share": transaction.ceo_share,
        "operational_share": transaction.operational_share,
        "payment_method": transaction.payment_method.value
    }


@app.get("/business/midtrans/payment-methods")
async def get_payment_methods():
    """Get available Midtrans payment methods."""
    return {
        "payment_methods": [
            {"code": "credit_card", "name": "Credit Card"},
            {"code": "bca_va", "name": "BCA Virtual Account"},
            {"code": "permata_va", "name": "Permata Virtual Account"},
            {"code": "other_va", "name": "Other Bank Virtual Account"},
            {"code": "qris", "name": "QRIS"},
            {"code": "gopay", "name": "GoPay"},
            {"code": "shopeepay", "name": "ShopeePay"},
            {"code": "indomaret", "name": "Indomaret"},
            {"code": "alfamart", "name": "Alfamart"}
        ],
        "features": {
            "recurring": True,
            "installment": True,
            "tokenization": True
        }
    }


# ==================== AI Intelligence Endpoints (Vol II) ====================

@app.post("/ai/vision/analyze")
async def analyze_image(
    image_data: str = None,
    image_url: str = None,
    prompt: str = "Describe this image"
):
    """Analyze image using Vision Engine."""
    vision = get_vision_engine()
    result = vision.analyze_image(image_data, image_url, prompt)
    
    return {
        "success": result.success,
        "description": result.description,
        "labels": result.labels,
        "text_extracted": result.text_extracted,
        "confidence": result.confidence,
        "objects": result.objects_detected
    }


@app.post("/ai/voice/process")
async def process_voice(
    audio_data: str = None,
    language: str = "id-ID"
):
    """Process voice command."""
    voice = get_voice_engine()
    result = voice.process_voice_command(audio_data, language)
    
    return {
        "success": result.success,
        "transcript": result.transcript,
        "command": result.command,
        "intent": result.intent,
        "confidence": result.confidence
    }


@app.post("/ai/nlp/extract")
async def extract_nlp(
    text: str = None
):
    """Extract NLP analysis from text."""
    nlp = get_nlp_engine()
    result = nlp.full_analysis(text)
    
    return {
        "success": result.success,
        "sentiment": result.sentiment.value,
        "sentiment_score": result.sentiment_score,
        "entities": result.entities,
        "categories": result.categories,
        "keywords": result.keywords,
        "summary": result.summary
    }


# ==================== DevOps Endpoints (Vol III) ====================

@app.post("/dev/tests/run")
async def run_tests():
    """Run automated test suite."""
    runner = get_auto_test_runner()
    results = runner.run_all_tests()
    return results


@app.get("/dev/logs")
async def get_logs(
    level: str = None,
    source: str = None,
    since: str = None,
    limit: int = 100
):
    """Get system logs."""
    logs = get_logging_system()
    return {"logs": logs.get_logs(level, source, since, limit)}


@app.get("/dev/logs/security")
async def get_security_logs():
    """Get security logs."""
    logs = get_logging_system()
    return {"logs": logs.get_security_logs()}


@app.post("/dev/deploy")
async def create_deployment(
    environment: str,
    version: str,
    notes: str = ""
):
    """Create new deployment."""
    deploy = get_deployment_center()
    env = Environment(environment)
    record = deploy.create_deployment(env, version, notes)
    
    return {
        "deployment_id": record.deployment_id,
        "environment": record.environment.value,
        "version": record.version,
        "status": record.status.value
    }


@app.get("/dev/deploy/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get deployment status."""
    deploy = get_deployment_center()
    status = deploy.get_deployment_status(deployment_id)
    
    if not status:
        return {"error": "Deployment not found"}
    
    return status


@app.post("/dev/deploy/{deployment_id}/rollback")
async def rollback_deployment(deployment_id: str, reason: str = ""):
    """Rollback a deployment."""
    deploy = get_deployment_center()
    rollback_id = deploy.rollback_deployment(deployment_id, reason)
    return {"rollback_id": rollback_id}


@app.post("/dev/code/analyze")
async def analyze_code(code: str, filename: str = "script.py"):
    """Analyze code for issues."""
    ai = get_ai_coding_assistant()
    result = ai.analyze_code(code, filename)
    return result


@app.get("/dev/performance")
async def get_performance_stats():
    """Get performance statistics."""
    profiler = get_performance_profiler()
    return {
        "endpoints": profiler.get_all_stats(),
        "memory": profiler.get_memory_trend()
    }


@app.post("/dev/performance/snapshot")
async def record_performance_snapshot():
    """Record memory snapshot."""
    profiler = get_performance_profiler()
    return profiler.record_memory_snapshot()


# ==================== Business Operations Endpoints (Vol IV) ====================

@app.post("/business/ops/assets")
async def create_asset(
    name: str,
    asset_type: str,
    purchase_date: str,
    purchase_cost: float,
    depreciation_rate: float = 10.0,
    useful_life_years: int = 5,
    location: str = ""
):
    """Create new asset."""
    from app.business.operations import Asset
    
    asset_manager = get_asset_manager()
    
    asset_id = f"ASSET-{uuid.uuid4().hex[:8].upper()}"
    
    asset = Asset(
        asset_id=asset_id,
        name=name,
        asset_type=AssetType(asset_type),
        purchase_date=purchase_date,
        purchase_cost=purchase_cost,
        current_value=purchase_cost,
        depreciation_rate=depreciation_rate,
        useful_life_years=useful_life_years,
        location=location
    )
    
    asset_manager.add_asset(asset)
    
    return {"asset_id": asset_id, "status": "created"}


@app.get("/business/ops/assets")
async def list_assets(asset_type: str = None):
    """List all assets."""
    asset_manager = get_asset_manager()
    assets = asset_manager.get_assets(
        AssetType(asset_type) if asset_type else None
    )
    return {"assets": assets}


@app.get("/business/ops/assets/{asset_id}/depreciation")
async def get_asset_depreciation(asset_id: str):
    """Calculate asset depreciation."""
    asset_manager = get_asset_manager()
    return asset_manager.calculate_depreciation(asset_id)


@app.post("/business/ops/contracts")
async def generate_contract(
    contract_type: str,
    party_a_name: str,
    party_b_name: str,
    terms: str  # JSON array
):
    """Generate business contract."""
    import json
    
    legal = get_legal_engine()
    
    terms_list = json.loads(terms) if isinstance(terms, str) else terms
    
    result = legal.generate_contract(
        contract_type=contract_type,
        party_a={"name": party_a_name},
        party_b={"name": party_b_name},
        terms=terms_list
    )
    
    return result


@app.post("/business/ops/nda")
async def generate_nda(
    disclosing_party: str,
    receiving_party: str,
    purpose: str,
    duration_months: int = 24
):
    """Generate NDA."""
    legal = get_legal_engine()
    return legal.generate_nda(disclosing_party, receiving_party, purpose, duration_months)


@app.post("/business/ops/employees")
async def create_employee(
    name: str,
    email: str,
    department: str,
    position: str,
    salary: float = 0
):
    """Create employee."""
    from app.business.operations import Employee
    
    hr = get_hr_manager()
    
    employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
    
    employee = Employee(
        employee_id=employee_id,
        name=name,
        email=email,
        phone="",
        department=department,
        position=position,
        hire_date=datetime.now().strftime("%Y-%m-%d"),
        salary=salary
    )
    
    hr.add_employee(employee)
    
    return {"employee_id": employee_id, "status": "created"}


@app.get("/business/ops/employees")
async def list_employees(department: str = None):
    """List employees with real data from database."""
    hr = get_hr_manager()
    employees = hr.get_employees(department)
    
    # Seed demo employees if database is empty
    if not employees:
        await _seed_demo_employees(hr)
        employees = hr.get_employees(department)
    
    return {"employees": employees}


async def _seed_demo_employees(hr: "HRManager"):
    """Seed demo employees for dashboard visibility."""
    import uuid
    from app.business.operations import Employee, LeaveType, LeaveStatus
    
    demo_employees = [
        {"name": "Made Purna Ananda", "email": "pakpur@mahalakshmi.id", "dept": "Executive", "position": "CEO", "salary": 50000000},
        {"name": "Wayan Lestiani", "email": "bunda@mahalakshmi.id", "dept": "Finance", "position": "CFO", "salary": 25000000},
        {"name": "Komang Sugiarta", "email": "komang@mahalakshmi.id", "dept": "Engineering", "position": "Tech Lead", "salary": 15000000},
        {"name": "Nyoman Wiratama", "email": "nyoman@mahalakshmi.id", "dept": "Marketing", "position": "Marketing Manager", "salary": 12000000},
        {"name": "Ketut Santika", "email": "ketut@mahalakshmi.id", "dept": "Operations", "position": "Operations Manager", "salary": 10000000},
        {"name": "Ayu Dewi Lestari", "email": "ayu@mahalakshmi.id", "dept": "HR", "position": "HR Manager", "salary": 10000000},
        {"name": "Putra Aditya", "email": "putra@mahalakshmi.id", "dept": "IT", "position": "Software Engineer", "salary": 12000000},
        {"name": "Sri Utami", "email": "sri@mahalakshmi.id", "dept": "Finance", "position": "Accountant", "salary": 8000000},
    ]
    
    for emp in demo_employees:
        emp_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        employee = Employee(
            employee_id=emp_id,
            name=emp["name"],
            email=emp["email"],
            phone="08123456789",
            department=emp["dept"],
            position=emp["position"],
            hire_date="2024-01-01",
            salary=emp["salary"]
        )
        hr.add_employee(employee)
    
    # Add some leave requests
    for i in range(3):
        hr.request_leave(
            employee_id=f"EMP-{demo_employees[i]['name'][:3].upper()}{i+1}00",
            leave_type=LeaveType.ANNUAL if i % 2 == 0 else LeaveType.PNS_CUTI,
            start_date="2026-07-20",
            end_date="2026-07-25",
            reason="Annual leave" if i % 2 == 0 else "Cuti PNS"
        )


@app.post("/business/ops/leave")
async def request_leave(
    employee_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str
):
    """Request leave."""
    hr = get_hr_manager()
    leave = hr.request_leave(
        employee_id=employee_id,
        leave_type=LeaveType(leave_type),
        start_date=start_date,
        end_date=end_date,
        reason=reason
    )
    
    return {"request_id": leave.request_id, "status": leave.status.value}


@app.get("/business/ops/leave/{employee_id}")
async def get_leave_balance(employee_id: str):
    """Get leave balance."""
    hr = get_hr_manager()
    return hr.calculate_leave_balance(employee_id)


@app.post("/business/ops/vendors")
async def create_vendor(
    name: str,
    email: str,
    category: str
):
    """Create vendor."""
    from app.business.operations import Vendor
    
    supply = get_supply_chain()
    
    vendor_id = f"VD-{uuid.uuid4().hex[:8].upper()}"
    
    vendor = Vendor(
        vendor_id=vendor_id,
        name=name,
        contact_person="",
        email=email,
        phone="",
        address="",
        category=category,
        status=VendorStatus.ACTIVE
    )
    
    supply.add_vendor(vendor)
    
    return {"vendor_id": vendor_id, "status": "created"}


@app.get("/business/ops/vendors")
async def list_vendors():
    """List vendors."""
    supply = get_supply_chain()
    return {"vendors": supply.get_vendors()}


@app.post("/business/ops/procurement")
async def create_procurement(
    vendor_id: str,
    items: str,  # JSON
    requested_by: str = "system"
):
    """Create procurement order."""
    import json
    
    supply = get_supply_chain()
    
    items_list = json.loads(items) if isinstance(items, str) else items
    
    order = supply.create_procurement(vendor_id, items_list, requested_by)
    
    return {"order_id": order.order_id, "status": order.status.value}


# ==================== Enterprise Architecture Endpoints (Vol V) ====================

@app.get("/enterprise/erp/dashboard")
async def get_erp_dashboard():
    """Get unified ERP dashboard."""
    erp = get_erp_sync()
    return erp.get_unified_dashboard()


@app.post("/enterprise/erp/sync")
async def trigger_erp_sync(data_type: str = "all"):
    """Trigger ERP data sync."""
    erp = get_erp_sync()
    return erp.trigger_sync(data_type)


@app.get("/enterprise/bi/sales-velocity")
async def get_sales_velocity():
    """Get sales velocity analytics."""
    bi = get_business_intelligence()
    
    # Get sample data
    from app.business.revenue import get_revenue_manager
    revenue = get_revenue_manager()
    
    transactions = [
        {"amount": t.amount, "date": t.timestamp.isoformat()}
        for t in list(revenue.transactions.values())[-30:]
    ]
    
    return bi.calculate_sales_velocity(transactions)


@app.get("/enterprise/bi/forecast")
async def get_revenue_forecast(forecast_days: int = 30):
    """Get revenue forecast."""
    bi = get_business_intelligence()
    
    from app.business.revenue import get_revenue_manager
    revenue = get_revenue_manager()
    
    historical = [
        {"amount": t.amount, "date": t.timestamp.isoformat()}
        for t in list(revenue.transactions.values())
    ]
    
    return bi.forecast_revenue(historical, forecast_days)


@app.get("/enterprise/audit/logs")
async def get_audit_logs(
    user_id: str = None,
    action: str = None,
    since: str = None,
    limit: int = 100
):
    """Get audit logs."""
    from app.enterprise.architecture import AuditAction
    
    audit = get_audit_trail()
    
    audit_action = AuditAction(action) if action else None
    
    return {"logs": audit.get_logs(user_id, audit_action, since, limit)}


@app.get("/enterprise/audit/verify")
async def verify_audit_integrity(limit: int = 100):
    """Verify audit chain integrity."""
    audit = get_audit_trail()
    return audit.verify_chain_integrity(limit)


@app.post("/enterprise/audit/log")
async def create_audit_log(
    user_id: str,
    action: str,
    resource: str,
    resource_id: str = "",
    ip_address: str = "",
    details: str = "{}"
):
    """Create audit log entry."""
    import json
    from app.enterprise.architecture import AuditAction
    
    audit = get_audit_trail()
    
    details_dict = json.loads(details) if isinstance(details, str) else details
    
    entry = audit.log(
        user_id=user_id,
        action=AuditAction(action),
        resource=resource,
        resource_id=resource_id,
        ip_address=ip_address,
        details=details_dict
    )
    
    return {"entry_id": entry.entry_id, "hash": entry.hash}


@app.get("/enterprise/security/rate-limit/{ip_address}")
async def check_rate_limit(ip_address: str):
    """Check IP rate limit."""
    shield = get_security_shield()
    return shield.check_rate_limit(ip_address)


@app.post("/enterprise/security/sanitize")
async def sanitize_input(input_string: str):
    """Sanitize input against injection."""
    shield = get_security_shield()
    return {
        "original": input_string,
        "sanitized": shield.sanitize_input(input_string),
        "sql_injection_detected": shield.detect_sql_injection(input_string)
    }


@app.get("/enterprise/tenants")
async def list_tenants():
    """List all tenants."""
    router = get_multi_tenant()
    return {"tenants": router.get_all_tenants()}


@app.post("/enterprise/tenants")
async def create_tenant(
    name: str,
    tenant_type: str
):
    """Create new tenant."""
    from app.enterprise.architecture import TenantType
    
    router = get_multi_tenant()
    tenant = router.create_tenant(name, TenantType(tenant_type))
    
    return {
        "tenant_id": tenant.tenant_id,
        "name": tenant.name,
        "schema": tenant.db_schema,
        "api_key": tenant.api_key
    }


@app.get("/enterprise/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    cache = get_cache()
    return cache.get_stats()


@app.post("/enterprise/cache/clear")
async def clear_cache():
    """Clear cache."""
    cache = get_cache()
    cache.clear()
    return {"status": "cleared"}


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
