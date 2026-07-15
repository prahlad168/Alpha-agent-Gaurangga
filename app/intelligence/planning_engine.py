"""
MAHALAKSMI AIOS v1.0 - Volume II Chapter 19: AI Planning Engine
Goal-Oriented Action Planning (GOAP) for tactical decision making
"""
import os
import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class PlanStatus(Enum):
    """Plan status."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionStatus(Enum):
    """Action status."""
    PENDING = "pending"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorldState:
    """Current world state conditions."""
    conditions: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def satisfies(self, goal: Dict[str, Any]) -> bool:
        """Check if current state satisfies goal conditions."""
        for key, value in goal.items():
            if key not in self.conditions or self.conditions[key] != value:
                return False
        return True
    
    def distance_to(self, goal: Dict[str, Any]) -> int:
        """Calculate distance to goal (number of unmet conditions)."""
        distance = 0
        for key, value in goal.items():
            if key not in self.conditions or self.conditions[key] != value:
                distance += 1
        return distance


@dataclass
class Action:
    """Plannable action with preconditions and effects."""
    action_id: str
    name: str
    description: str
    preconditions: Dict[str, Any]  # Required state
    effects: Dict[str, Any]         # State changes
    cost: float = 1.0
    duration_minutes: int = 60
    resources_required: Dict[str, float] = field(default_factory=dict)
    weight: float = 1.0  # Learning weight


@dataclass
class PlanStep:
    """Single step in a plan."""
    step_id: str
    action: Action
    status: ActionStatus = ActionStatus.PENDING
    result: Any = None
    error: str = ""
    executed_at: str = ""
    
    def __post_init__(self):
        if not self.executed_at:
            self.executed_at = datetime.now().isoformat()


@dataclass
class Plan:
    """Complete action plan."""
    plan_id: str
    goal_description: str
    goal_conditions: Dict[str, Any]
    status: PlanStatus
    steps: List[PlanStep] = field(default_factory=list)
    current_step_index: int = 0
    initial_state: WorldState = None
    final_state: WorldState = None
    total_cost: float = 0.0
    estimated_duration_minutes: int = 0
    success_score: float = 0.0
    created_at: str = ""
    completed_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    @property
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return all(s.status == ActionStatus.COMPLETED for s in self.steps)


# ============================================================================
# PLANNING DATABASE
# ============================================================================

class PlanningDB:
    """SQLite database for planning engine."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "planning_engine.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                plan_id TEXT PRIMARY KEY,
                goal_description TEXT,
                goal_conditions TEXT,
                status TEXT,
                initial_state TEXT,
                final_state TEXT,
                total_cost REAL,
                estimated_duration INTEGER,
                success_score REAL,
                created_at TEXT,
                completed_at TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                action_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                preconditions TEXT,
                effects TEXT,
                cost REAL,
                duration_minutes INTEGER,
                resources_required TEXT,
                weight REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_steps (
                step_id TEXT PRIMARY KEY,
                plan_id TEXT,
                action_id TEXT,
                status TEXT,
                result TEXT,
                error TEXT,
                executed_at TEXT,
                FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_plan(self, plan: Plan) -> bool:
        """Save plan."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            initial_state = ""
            if plan.initial_state:
                initial_state = json.dumps(plan.initial_state.conditions)
            
            final_state = ""
            if plan.final_state:
                final_state = json.dumps(plan.final_state.conditions)
            
            cursor.execute("""
                INSERT OR REPLACE INTO plans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan.plan_id,
                plan.goal_description,
                json.dumps(plan.goal_conditions),
                plan.status.value,
                initial_state,
                final_state,
                plan.total_cost,
                plan.estimated_duration_minutes,
                plan.success_score,
                plan.created_at,
                plan.completed_at,
                json.dumps(plan.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # Save steps
            for step in plan.steps:
                self._save_step(plan.plan_id, step)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
            return False
    
    def _save_step(self, plan_id: str, step: PlanStep) -> bool:
        """Save plan step."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO plan_steps VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                step.step_id,
                plan_id,
                step.action.action_id,
                step.status.value,
                json.dumps(step.result) if step.result else None,
                step.error,
                step.executed_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save step: {e}")
            return False
    
    def save_action(self, action: Action) -> bool:
        """Save action."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO actions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action.action_id,
                action.name,
                action.description,
                json.dumps(action.preconditions),
                json.dumps(action.effects),
                action.cost,
                action.duration_minutes,
                json.dumps(action.resources_required),
                action.weight
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save action: {e}")
            return False
    
    def get_action(self, action_id: str) -> Optional[Action]:
        """Get action by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_action(row)
        return None
    
    def _row_to_action(self, row) -> Action:
        """Convert row to Action."""
        return Action(
            action_id=row['action_id'],
            name=row['name'],
            description=row['description'],
            preconditions=json.loads(row['preconditions']),
            effects=json.loads(row['effects']),
            cost=row['cost'],
            duration_minutes=row['duration_minutes'],
            resources_required=json.loads(row['resources_required']),
            weight=row['weight']
        )
    
    def get_all_actions(self) -> List[Action]:
        """Get all actions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM actions")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_action(row) for row in rows]
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM plans WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        plan = self._row_to_plan(row)
        
        # Get steps
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM plan_steps WHERE plan_id = ?", (plan_id,))
        step_rows = cursor.fetchall()
        conn.close()
        
        for sr in step_rows:
            action = self.get_action(sr['action_id'])
            if action:
                step = PlanStep(
                    step_id=sr['step_id'],
                    action=action,
                    status=ActionStatus(sr['status']),
                    result=json.loads(sr['result']) if sr['result'] else None,
                    error=sr['error'] or "",
                    executed_at=sr['executed_at']
                )
                plan.steps.append(step)
        
        return plan
    
    def _row_to_plan(self, row) -> Plan:
        """Convert row to Plan."""
        return Plan(
            plan_id=row['plan_id'],
            goal_description=row['goal_description'],
            goal_conditions=json.loads(row['goal_conditions']),
            status=PlanStatus(row['status']),
            total_cost=row['total_cost'],
            estimated_duration_minutes=row['estimated_duration'],
            success_score=row['success_score'],
            created_at=row['created_at'],
            completed_at=row['completed_at'] or "",
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def get_all_plans(self) -> List[Plan]:
        """Get all plans."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT plan_id FROM plans ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        plans = []
        for row in rows:
            plan = self.get_plan(row['plan_id'])
            if plan:
                plans.append(plan)
        
        return plans
    
    def update_action_weight(self, action_id: str, new_weight: float) -> bool:
        """Update action weight based on learning."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE actions SET weight = ? WHERE action_id = ?",
                (new_weight, action_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update weight: {e}")
            return False


# ============================================================================
# AI PLANNING ENGINE (GOAP)
# ============================================================================

class PlanningEngine:
    """
    Goal-Oriented Action Planning (GOAP) Engine.
    Generates tactical action plans from high-level goals.
    """
    
    def __init__(self):
        self.db = PlanningDB()
        self._init_default_actions()
        
        logger.info("PlanningEngine initialized")
    
    def _init_default_actions(self):
        """Initialize default planning actions."""
        actions = [
            Action(
                action_id="ACTION-REVENUE-CAMPAIGN",
                name="Launch Revenue Campaign",
                description="Launch marketing campaign to boost revenue",
                preconditions={"has_marketing_kit": True, "has_budget": True},
                effects={"revenue_awareness": True, "revenue_increased": True},
                cost=3.0,
                duration_minutes=120,
                resources_required={"budget": 500000, "time": 4.0}
            ),
            Action(
                action_id="ACTION-NEW-PRODUCT",
                name="Launch New Product",
                description="Release a new digital product",
                preconditions={"has_product_idea": True},
                effects={"has_active_product": True, "revenue_increased": True},
                cost=5.0,
                duration_minutes=480,
                resources_required={"budget": 1000000, "time": 16.0}
            ),
            Action(
                action_id="ACTION-OUTREACH",
                name="Customer Outreach",
                description="Reach out to existing customers for upsell",
                preconditions={"has_customer_list": True},
                effects={"customer_engaged": True, "revenue_increased": True},
                cost=2.0,
                duration_minutes=60,
                resources_required={"time": 2.0}
            ),
            Action(
                action_id="ACTION-PARTNERSHIP",
                name="Establish Partnership",
                description="Form strategic partnership for distribution",
                preconditions={"has_partner_leads": True},
                effects={"has_partnership": True, "reach_increased": True},
                cost=4.0,
                duration_minutes=240,
                resources_required={"time": 8.0}
            ),
            Action(
                action_id="ACTION-OPTIMIZE-PRICING",
                name="Optimize Pricing",
                description="Analyze and adjust pricing strategy",
                preconditions={"has_sales_data": True},
                effects={"pricing_optimized": True, "revenue_increased": True},
                cost=2.0,
                duration_minutes=120,
                resources_required={"time": 4.0}
            ),
            Action(
                action_id="ACTION-COST-CUT",
                name="Reduce Costs",
                description="Identify and eliminate unnecessary expenses",
                preconditions={"has_expense_data": True},
                effects={"costs_reduced": True, "profit_margin_increased": True},
                cost=1.5,
                duration_minutes=60,
                resources_required={"time": 2.0}
            ),
            Action(
                action_id="ACTION-AUTOMATE",
                name="Automate Workflow",
                description="Implement automation for efficiency",
                preconditions={"has_manual_processes": True},
                effects={"efficiency_increased": True, "costs_reduced": True},
                cost=3.0,
                duration_minutes=180,
                resources_required={"budget": 200000, "time": 6.0}
            ),
            Action(
                action_id="ACTION-TEAM-HIRE",
                name="Hire Team Member",
                description="Recruit additional team capacity",
                preconditions={"has_job_description": True, "has_budget": True},
                effects={"has_added_capacity": True, "output_increased": True},
                cost=4.0,
                duration_minutes=480,
                resources_required={"budget": 5000000, "time": 16.0}
            )
        ]
        
        for action in actions:
            self.db.save_action(action)
        
        logger.info(f"Initialized {len(actions)} default actions")
    
    def get_current_state(self) -> WorldState:
        """Get current world state from system components."""
        state = WorldState()
        
        try:
            # Get revenue state
            from app.business.revenue import get_revenue_manager
            revenue = get_revenue_manager()
            summary = revenue.get_summary()
            
            state.conditions["has_revenue"] = summary.get("total_revenue", 0) > 0
            state.conditions["revenue_level"] = "high" if summary.get("total_revenue", 0) > 50000000 else "medium" if summary.get("total_revenue", 0) > 10000000 else "low"
            
            # Get mission state
            from app.enterprise.mission_control import get_mission_control
            mc = get_mission_control()
            dashboard = mc.get_dashboard()
            
            state.conditions["active_missions"] = dashboard["missions"]["by_status"].get("in_progress", 0)
            state.conditions["completed_missions"] = dashboard["missions"]["by_status"].get("completed", 0)
            
            # Get product state
            from app.business.product import get_product_center
            product_center = get_product_center()
            products = product_center.list_products()
            
            state.conditions["has_products"] = len(products) > 0
            state.conditions["has_active_product"] = any(p.get("active", False) for p in products)
            
            # Resources
            state.resources["budget"] = 10000000  # Default budget
            state.resources["time"] = 40.0  # Available hours per week
            
        except Exception as e:
            logger.warning(f"Could not load full state: {e}")
            state.conditions["has_revenue"] = False
            state.conditions["has_products"] = False
            state.conditions["active_missions"] = 0
        
        return state
    
    def get_applicable_actions(self, current_state: WorldState) -> List[Action]:
        """Get actions that can be executed in current state."""
        applicable = []
        actions = self.db.get_all_actions()
        
        for action in actions:
            # Check preconditions
            can_execute = True
            for key, value in action.preconditions.items():
                if key not in current_state.conditions:
                    can_execute = False
                    break
                if current_state.conditions[key] != value and value is not None:
                    can_execute = False
                    break
            
            if can_execute:
                applicable.append(action)
        
        # Sort by weight (favor successful actions)
        applicable.sort(key=lambda a: a.weight, reverse=True)
        
        return applicable
    
    def generate_plan(self, goal_description: str, goal_conditions: Dict[str, Any]) -> Plan:
        """
        Generate action plan using GOAP.
        """
        import hashlib
        plan_id = hashlib.md5(
            f"{goal_description}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        plan = Plan(
            plan_id=f"PLAN-{plan_id}",
            goal_description=goal_description,
            goal_conditions=goal_conditions,
            status=PlanStatus.DRAFT,
            initial_state=self.get_current_state()
        )
        
        # Get current state
        current_state = plan.initial_state
        
        # Use A* search to find plan
        steps = []
        total_cost = 0.0
        estimated_duration = 0
        visited_states = set()
        
        while not current_state.satisfies(goal_conditions):
            # Check for loops
            state_key = json.dumps(current_state.conditions, sort_keys=True)
            if state_key in visited_states and len(steps) > 0:
                break
            visited_states.add(state_key)
            
            # Get applicable actions
            applicable = self.get_applicable_actions(current_state)
            
            if not applicable:
                # Try to find actions that could enable other actions
                applicable = self.db.get_all_actions()
            
            if not applicable:
                break
            
            # Find best action (highest weight, lowest cost)
            best_action = min(
                applicable,
                key=lambda a: a.cost / max(a.weight, 0.1)
            )
            
            # Create step
            step_id = hashlib.md5(
                f"{plan_id}{best_action.action_id}{len(steps)}".encode()
            ).hexdigest()[:12].upper()
            
            step = PlanStep(
                step_id=f"STEP-{step_id}",
                action=best_action,
                status=ActionStatus.READY
            )
            steps.append(step)
            
            # Update cost and duration
            total_cost += best_action.cost
            estimated_duration += best_action.duration_minutes
            
            # Apply effects
            for key, value in best_action.effects.items():
                current_state.conditions[key] = value
        
        plan.steps = steps
        plan.total_cost = total_cost
        plan.estimated_duration_minutes = estimated_duration
        
        self.db.save_plan(plan)
        
        logger.info(f"Generated plan {plan.plan_id} with {len(steps)} steps")
        return plan
    
    def evaluate_feasibility(self, goal_conditions: Dict[str, Any]) -> Dict:
        """Evaluate if a goal is achievable."""
        current_state = self.get_current_state()
        
        # Find missing conditions
        missing_conditions = []
        for key, value in goal_conditions.items():
            if key not in current_state.conditions or current_state.conditions[key] != value:
                missing_conditions.append(key)
        
        # Check if we have actions to address missing conditions
        actions = self.db.get_all_actions()
        addressable = []
        
        for action in actions:
            for effect_key in action.effects.keys():
                if effect_key in missing_conditions:
                    addressable.append({
                        "action": action.name,
                        "effect": effect_key
                    })
                    break
        
        # Estimate difficulty
        difficulty = "easy"
        if len(missing_conditions) > 3:
            difficulty = "medium"
        if len(missing_conditions) > 5:
            difficulty = "hard"
        if len(addressable) == 0 and len(missing_conditions) > 0:
            difficulty = "impossible"
        
        return {
            "goal_conditions": goal_conditions,
            "current_state": current_state.conditions,
            "missing_conditions": missing_conditions,
            "addressable_with": addressable,
            "feasibility": "achievable" if addressable else "unachievable",
            "difficulty": difficulty
        }
    
    def get_plans(self, status: PlanStatus = None) -> List[Dict]:
        """Get all plans."""
        plans = self.db.get_all_plans()
        
        if status:
            plans = [p for p in plans if p.status == status]
        
        return [
            {
                "plan_id": p.plan_id,
                "goal_description": p.goal_description,
                "status": p.status.value,
                "steps_count": len(p.steps),
                "total_cost": p.total_cost,
                "success_score": p.success_score,
                "created_at": p.created_at
            }
            for p in plans
        ]


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_planning_engine: Optional[PlanningEngine] = None


def get_planning_engine() -> PlanningEngine:
    """Get or create global planning engine."""
    global _planning_engine
    if _planning_engine is None:
        _planning_engine = PlanningEngine()
    return _planning_engine
