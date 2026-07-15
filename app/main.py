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
