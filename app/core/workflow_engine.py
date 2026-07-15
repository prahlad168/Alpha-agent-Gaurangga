"""
MAHALAKSMI AIOS v1.0 - Volume I Chapter 10: Workflow & Business Operating System
State-machine based workflow runner for multi-step task execution
"""
import os
import sys
import sqlite3
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class StepState(Enum):
    """Step execution state."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowState(Enum):
    """Workflow execution state."""
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(Enum):
    """Workflow types."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class Step:
    """Workflow step definition."""
    step_id: str
    name: str
    description: str = ""
    action: str = ""  # Action name to execute
    action_params: Dict[str, Any] = field(default_factory=dict)
    state: StepState = StepState.PENDING
    result: Any = None
    error: str = ""
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 60
    depends_on: List[str] = field(default_factory=list)
    rollback_action: str = ""
    rollback_params: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class Workflow:
    """Workflow definition."""
    workflow_id: str
    name: str
    workflow_type: WorkflowType
    state: WorkflowState
    description: str = ""
    steps: List[Step] = field(default_factory=list)
    mission_id: str = ""  # Link to mission if spawned from one
    variables: Dict[str, Any] = field(default_factory=dict)
    current_step_index: int = 0
    result: Any = None
    error: str = ""
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ============================================================================
# WORKFLOW ACTION HANDLERS
# ============================================================================

class ActionHandler(ABC):
    """Base class for workflow action handlers."""
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Any:
        """Execute the action."""
        pass
    
    async def rollback(self, params: Dict[str, Any]) -> bool:
        """Rollback the action."""
        return True


class NotificationAction(ActionHandler):
    """Send notification action."""
    
    async def execute(self, params: Dict[str, Any]) -> Any:
        from app.enterprise.notification import get_notification_center, NotificationPriority
        
        nc = get_notification_center()
        
        title = params.get("title", "Workflow Notification")
        message = params.get("message", "")
        priority = params.get("priority", "normal")
        
        notification_id = nc.notify(
            event_type="workflow.action",
            title=title,
            message=message,
            priority=NotificationPriority(priority)
        )
        
        return {"notification_id": notification_id, "sent": True}


class RevenueAction(ActionHandler):
    """Record revenue action."""
    
    async def execute(self, params: Dict[str, Any]) -> Any:
        from app.business.revenue import get_revenue_manager
        
        revenue = get_revenue_manager()
        
        source = params.get("source", "workflow")
        amount = params.get("amount", 0)
        payment_method = params.get("payment_method", "qris")
        
        txn = await revenue.record_digital_revenue(
            source=source,
            amount=amount,
            payment_method=payment_method
        )
        
        return {"transaction_id": txn.transaction_id, "amount": amount}


class BackupAction(ActionHandler):
    """Backup database action."""
    
    async def execute(self, params: Dict[str, Any]) -> Any:
        from app.enterprise.backup import get_backup_center
        
        bc = get_backup_center()
        
        db_name = params.get("db_name", "memory")
        
        backup = bc.backup_database(db_name)
        
        return {
            "backup_id": backup.backup_id,
            "status": backup.status.value,
            "size": backup.size_bytes
        }


class MissionAction(ActionHandler):
    """Update mission action."""
    
    async def execute(self, params: Dict[str, Any]) -> Any:
        from app.enterprise.mission_control import get_mission_control, MissionStatus
        
        mc = get_mission_control()
        
        mission_id = params.get("mission_id")
        status = params.get("status", "completed")
        progress = params.get("progress")
        
        if mission_id and status:
            mc.update_mission_status(
                mission_id,
                MissionStatus(status),
                progress
            )
        
        return {"mission_id": mission_id, "status": status}


class WebhookAction(ActionHandler):
    """Send webhook action."""
    
    async def execute(self, params: Dict[str, Any]) -> Any:
        url = params.get("url", "")
        data = params.get("data", {})
        
        # Stub implementation
        logger.info(f"Webhook would send to {url}: {data}")
        
        return {"url": url, "sent": True}


# ============================================================================
# WORKFLOW ENGINE DATABASE
# ============================================================================

class WorkflowDB:
    """SQLite database for workflows."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "workflow_engine.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                workflow_type TEXT,
                state TEXT,
                mission_id TEXT,
                variables TEXT,
                current_step_index INTEGER,
                result TEXT,
                error TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_steps (
                step_id TEXT PRIMARY KEY,
                workflow_id TEXT,
                name TEXT,
                description TEXT,
                action TEXT,
                action_params TEXT,
                state TEXT,
                result TEXT,
                error TEXT,
                retry_count INTEGER,
                max_retries INTEGER,
                timeout_seconds INTEGER,
                depends_on TEXT,
                rollback_action TEXT,
                rollback_params TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_workflow(self, workflow: Workflow) -> bool:
        """Save workflow."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO workflows VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow.workflow_id,
                workflow.name,
                workflow.description,
                workflow.workflow_type.value,
                workflow.state.value,
                workflow.mission_id,
                json.dumps(workflow.variables),
                workflow.current_step_index,
                json.dumps(workflow.result) if workflow.result else None,
                workflow.error,
                workflow.created_at,
                workflow.started_at,
                workflow.completed_at
            ))
            
            conn.commit()
            conn.close()
            
            # Save steps
            for step in workflow.steps:
                self._save_step(workflow.workflow_id, step)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            return False
    
    def _save_step(self, workflow_id: str, step: Step) -> bool:
        """Save workflow step."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO workflow_steps 
                (step_id, workflow_id, name, description, action, action_params, state, result, error, 
                 retry_count, max_retries, timeout_seconds, depends_on, rollback_action, rollback_params, 
                 created_at, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                step.step_id,
                workflow_id,
                step.name,
                step.description,
                step.action,
                json.dumps(step.action_params),
                step.state.value,
                json.dumps(step.result) if step.result else None,
                step.error,
                step.retry_count,
                step.max_retries,
                step.timeout_seconds,
                json.dumps(step.depends_on),
                step.rollback_action,
                json.dumps(step.rollback_params),
                step.created_at,
                step.started_at,
                step.completed_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save step: {e}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM workflows WHERE workflow_id = ?", (workflow_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Get steps
        cursor.execute("SELECT * FROM workflow_steps WHERE workflow_id = ?", (workflow_id,))
        step_rows = cursor.fetchall()
        conn.close()
        
        workflow = self._row_to_workflow(row)
        workflow.steps = [self._row_to_step(sr) for sr in step_rows]
        
        return workflow
    
    def _row_to_workflow(self, row) -> Workflow:
        """Convert row to Workflow."""
        return Workflow(
            workflow_id=row['workflow_id'],
            name=row['name'],
            description=row['description'] or "",
            workflow_type=WorkflowType(row['workflow_type']),
            state=WorkflowState(row['state']),
            mission_id=row['mission_id'] or "",
            variables=json.loads(row['variables']) if row['variables'] else {},
            current_step_index=row['current_step_index'],
            result=json.loads(row['result']) if row['result'] else None,
            error=row['error'] or "",
            created_at=row['created_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at']
        )
    
    def _row_to_step(self, row) -> Step:
        """Convert row to Step."""
        return Step(
            step_id=row['step_id'],
            name=row['name'],
            description=row['description'] or "",
            action=row['action'],
            action_params=json.loads(row['action_params']) if row['action_params'] else {},
            state=StepState(row['state']),
            result=json.loads(row['result']) if row['result'] else None,
            error=row['error'] or "",
            retry_count=row['retry_count'],
            max_retries=row['max_retries'],
            timeout_seconds=row['timeout_seconds'],
            depends_on=json.loads(row['depends_on']) if row['depends_on'] else [],
            rollback_action=row['rollback_action'],
            rollback_params=json.loads(row['rollback_params']) if row['rollback_params'] else {},
            created_at=row['created_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at']
        )
    
    def get_all_workflows(self) -> List[Workflow]:
        """Get all workflows."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT workflow_id FROM workflows ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        workflows = []
        for row in rows:
            wf = self.get_workflow(row['workflow_id'])
            if wf:
                workflows.append(wf)
        
        return workflows


# ============================================================================
# WORKFLOW ENGINE
# ============================================================================

class WorkflowEngine:
    """
    State-machine Workflow Engine.
    Executes multi-step workflows with retry and rollback logic.
    """
    
    def __init__(self):
        self.db = WorkflowDB()
        
        # Register action handlers
        self.action_handlers: Dict[str, ActionHandler] = {
            "notification": NotificationAction(),
            "revenue": RevenueAction(),
            "backup": BackupAction(),
            "mission_update": MissionAction(),
            "webhook": WebhookAction()
        }
        
        logger.info("WorkflowEngine initialized")
    
    def create_workflow(
        self,
        name: str,
        description: str = "",
        workflow_type: WorkflowType = WorkflowType.SEQUENTIAL,
        mission_id: str = "",
        variables: Dict[str, Any] = None
    ) -> Workflow:
        """Create a new workflow."""
        import hashlib
        workflow_id = hashlib.md5(
            f"{name}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        workflow = Workflow(
            workflow_id=f"WF-{workflow_id}",
            name=name,
            workflow_type=workflow_type,
            state=WorkflowState.CREATED,
            description=description,
            mission_id=mission_id,
            variables=variables or {}
        )
        
        self.db.save_workflow(workflow)
        logger.info(f"Workflow created: {workflow.workflow_id}")
        
        return workflow
    
    def add_step(
        self,
        workflow_id: str,
        name: str,
        action: str,
        action_params: Dict[str, Any] = None,
        depends_on: List[str] = None,
        rollback_action: str = "",
        rollback_params: Dict[str, Any] = None,
        max_retries: int = 3,
        timeout_seconds: int = 60
    ) -> Step:
        """Add a step to workflow."""
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        import hashlib
        step_id = hashlib.md5(
            f"{workflow_id}{name}{len(workflow.steps)}".encode()
        ).hexdigest()[:12].upper()
        
        step = Step(
            step_id=f"STEP-{step_id}",
            name=name,
            action=action,
            action_params=action_params or {},
            depends_on=depends_on or [],
            rollback_action=rollback_action,
            rollback_params=rollback_params or {},
            max_retries=max_retries,
            timeout_seconds=timeout_seconds
        )
        
        workflow.steps.append(step)
        self.db.save_workflow(workflow)
        
        logger.info(f"Step added to {workflow_id}: {step.step_id}")
        return step
    
    async def execute_workflow(self, workflow_id: str) -> Workflow:
        """Execute a workflow."""
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if workflow.state == WorkflowState.RUNNING:
            raise ValueError(f"Workflow already running: {workflow_id}")
        
        # Update state
        workflow.state = WorkflowState.RUNNING
        workflow.started_at = datetime.now().isoformat()
        self.db.save_workflow(workflow)
        
        logger.info(f"Executing workflow: {workflow_id}")
        
        try:
            # Execute based on workflow type
            if workflow.workflow_type == WorkflowType.SEQUENTIAL:
                await self._execute_sequential(workflow)
            elif workflow.workflow_type == WorkflowType.PARALLEL:
                await self._execute_parallel(workflow)
            else:
                await self._execute_sequential(workflow)
            
            # Check if all steps completed
            all_completed = all(s.state == StepState.COMPLETED for s in workflow.steps)
            any_failed = any(s.state == StepState.FAILED for s in workflow.steps)
            
            if all_completed:
                workflow.state = WorkflowState.COMPLETED
                workflow.result = {"status": "completed", "steps_executed": len(workflow.steps)}
            elif any_failed:
                workflow.state = WorkflowState.FAILED
                workflow.error = "One or more steps failed"
            else:
                workflow.state = WorkflowState.PAUSED
            
        except Exception as e:
            workflow.state = WorkflowState.FAILED
            workflow.error = str(e)
            logger.error(f"Workflow execution failed: {e}")
            
            # Attempt rollback
            await self._rollback_workflow(workflow)
        
        workflow.completed_at = datetime.now().isoformat()
        self.db.save_workflow(workflow)
        
        return workflow
    
    async def _execute_sequential(self, workflow: Workflow):
        """Execute steps sequentially."""
        for i, step in enumerate(workflow.steps):
            workflow.current_step_index = i
            
            # Check dependencies
            if not self._can_execute_step(step, workflow.steps):
                step.state = StepState.SKIPPED
                self.db.save_workflow(workflow)
                continue
            
            # Execute step
            await self._execute_step(step)
            self.db.save_workflow(workflow)
            
            # Stop on failure if no retries
            if step.state == StepState.FAILED and step.retry_count >= step.max_retries:
                break
    
    async def _execute_parallel(self, workflow: Workflow):
        """Execute independent steps in parallel."""
        while True:
            # Find steps that can execute
            ready_steps = [
                s for s in workflow.steps
                if s.state == StepState.PENDING and self._can_execute_step(s, workflow.steps)
            ]
            
            if not ready_steps:
                break
            
            # Execute in parallel
            tasks = [self._execute_step(step) for step in ready_steps]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            self.db.save_workflow(workflow)
    
    def _can_execute_step(self, step: Step, all_steps: List[Step]) -> bool:
        """Check if step dependencies are satisfied."""
        for dep_id in step.depends_on:
            dep_step = next((s for s in all_steps if s.step_id == dep_id), None)
            if dep_step and dep_step.state != StepState.COMPLETED:
                return False
        return True
    
    async def _execute_step(self, step: Step):
        """Execute a single step."""
        step.state = StepState.RUNNING
        step.started_at = datetime.now().isoformat()
        
        handler = self.action_handlers.get(step.action)
        
        if not handler:
            step.state = StepState.FAILED
            step.error = f"Unknown action: {step.action}"
            return
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                handler.execute(step.action_params),
                timeout=step.timeout_seconds
            )
            
            step.state = StepState.COMPLETED
            step.result = result
            logger.info(f"Step completed: {step.step_id}")
        
        except asyncio.TimeoutError:
            step.state = StepState.FAILED
            step.error = f"Timeout after {step.timeout_seconds}s"
            logger.error(f"Step timeout: {step.step_id}")
        
        except Exception as e:
            step.error = str(e)
            logger.error(f"Step failed: {step.step_id} - {e}")
            
            # Retry logic
            step.retry_count += 1
            if step.retry_count < step.max_retries:
                step.state = StepState.RETRYING
                logger.info(f"Retrying step {step.step_id} ({step.retry_count}/{step.max_retries})")
            else:
                step.state = StepState.FAILED
        
        step.completed_at = datetime.now().isoformat()
    
    async def _rollback_workflow(self, workflow: Workflow):
        """Rollback completed steps in reverse order."""
        completed_steps = [
            s for s in workflow.steps
            if s.state == StepState.COMPLETED
        ][::-1]  # Reverse order
        
        for step in completed_steps:
            if step.rollback_action:
                handler = self.action_handlers.get(step.rollback_action)
                if handler:
                    try:
                        await handler.rollback(step.rollback_params)
                        logger.info(f"Rolled back step: {step.step_id}")
                    except Exception as e:
                        logger.error(f"Rollback failed for {step.step_id}: {e}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get workflow status."""
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "state": workflow.state.value,
            "type": workflow.workflow_type.value,
            "mission_id": workflow.mission_id,
            "current_step": workflow.current_step_index,
            "total_steps": len(workflow.steps),
            "completed_steps": sum(1 for s in workflow.steps if s.state == StepState.COMPLETED),
            "failed_steps": sum(1 for s in workflow.steps if s.state == StepState.FAILED),
            "result": workflow.result,
            "error": workflow.error,
            "steps": [
                {
                    "id": s.step_id,
                    "name": s.name,
                    "state": s.state.value,
                    "retry_count": s.retry_count,
                    "error": s.error
                }
                for s in workflow.steps
            ],
            "created_at": workflow.created_at,
            "started_at": workflow.started_at,
            "completed_at": workflow.completed_at
        }
    
    def spawn_from_mission(self, mission_id: str, mission_title: str) -> Workflow:
        """Create workflow from mission."""
        workflow = self.create_workflow(
            name=f"Workflow for: {mission_title}",
            description=f"Auto-generated from mission {mission_id}",
            workflow_type=WorkflowType.SEQUENTIAL,
            mission_id=mission_id
        )
        
        # Add default steps
        self.add_step(
            workflow_id=workflow.workflow_id,
            name="Send mission start notification",
            action="notification",
            action_params={
                "title": f"Mission Started: {mission_title}",
                "message": f"Mission {mission_id} has started execution",
                "priority": "high"
            }
        )
        
        self.add_step(
            workflow_id=workflow.workflow_id,
            name="Update mission status",
            action="mission_update",
            action_params={
                "mission_id": mission_id,
                "status": "in_progress",
                "progress": 50
            }
        )
        
        self.add_step(
            workflow_id=workflow.workflow_id,
            name="Send completion notification",
            action="notification",
            action_params={
                "title": f"Mission Completed: {mission_title}",
                "message": f"Mission {mission_id} has completed",
                "priority": "normal"
            },
            rollback_action="notification",
            rollback_params={
                "title": f"Mission Failed: {mission_title}",
                "message": f"Mission {mission_id} has failed",
                "priority": "critical"
            }
        )
        
        return workflow


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """Get or create global workflow engine."""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
