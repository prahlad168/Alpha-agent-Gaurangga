"""
MAHALAKSMI AIOS v1.0 - Volume II Chapter 20: AI Learning Engine
Self-improving feedback loop with weight adjustment for action pathways
"""
import os
import sys
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class FeedbackType(Enum):
    """Type of feedback."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    NEGATIVE = "negative"


class InsightType(Enum):
    """Type of learned insight."""
    ACTION_SUCCESS_RATE = "action_success_rate"
    PATTERN = "pattern"
    OPTIMIZATION = "optimization"
    RECOMMENDATION = "recommendation"


@dataclass
class ActionFeedback:
    """Feedback for an action."""
    feedback_id: str
    action_id: str
    plan_id: str
    feedback_type: FeedbackType
    score: float  # 0.0 - 1.0
    outcome: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class LearnedInsight:
    """Learned insight from feedback."""
    insight_id: str
    insight_type: InsightType
    description: str
    action_id: str = ""
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class WeightAdjustment:
    """Record of weight adjustment."""
    action_id: str
    previous_weight: float
    new_weight: float
    adjustment_factor: float
    reason: str
    timestamp: str = ""


# ============================================================================
# LEARNING DATABASE
# ============================================================================

class LearningDB:
    """SQLite database for learning engine."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "learning_engine.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_stats (
                action_id TEXT PRIMARY KEY,
                total_executions INTEGER DEFAULT 0,
                successful_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                total_score REAL DEFAULT 0.0,
                average_score REAL DEFAULT 0.5,
                last_execution_at TEXT,
                weight REAL DEFAULT 1.0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                action_id TEXT,
                plan_id TEXT,
                feedback_type TEXT,
                score REAL,
                outcome TEXT,
                context TEXT,
                timestamp TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                insight_id TEXT PRIMARY KEY,
                insight_type TEXT,
                description TEXT,
                action_id TEXT,
                confidence REAL,
                evidence TEXT,
                recommendations TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT,
                previous_weight REAL,
                new_weight REAL,
                adjustment_factor REAL,
                reason TEXT,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_feedback(self, feedback: ActionFeedback) -> bool:
        """Record feedback."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.feedback_id,
                feedback.action_id,
                feedback.plan_id,
                feedback.feedback_type.value,
                feedback.score,
                feedback.outcome,
                json.dumps(feedback.context),
                feedback.timestamp
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False
    
    def update_action_stats(self, action_id: str, feedback_type: FeedbackType, score: float) -> bool:
        """Update action statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current stats
            cursor.execute(
                "SELECT * FROM action_stats WHERE action_id = ?",
                (action_id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing
                total = row[1] + 1
                successful = row[2] + (1 if feedback_type == FeedbackType.SUCCESS else 0)
                failed = row[3] + (1 if feedback_type == FeedbackType.FAILURE else 0)
                total_score = row[4] + score
                avg_score = total_score / total
                
                cursor.execute("""
                    UPDATE action_stats SET
                        total_executions = ?,
                        successful_executions = ?,
                        failed_executions = ?,
                        total_score = ?,
                        average_score = ?,
                        last_execution_at = ?
                    WHERE action_id = ?
                """, (total, successful, failed, total_score, avg_score, datetime.now().isoformat(), action_id))
            else:
                # Insert new
                successful = 1 if feedback_type == FeedbackType.SUCCESS else 0
                failed = 1 if feedback_type == FeedbackType.FAILURE else 0
                
                cursor.execute("""
                    INSERT INTO action_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    action_id,
                    1,  # total
                    successful,
                    failed,
                    score,
                    score,
                    datetime.now().isoformat(),
                    1.0  # initial weight
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
            return False
    
    def get_action_stats(self, action_id: str) -> Optional[Dict]:
        """Get action statistics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM action_stats WHERE action_id = ?",
            (action_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "action_id": row['action_id'],
                "total_executions": row['total_executions'],
                "successful_executions": row['successful_executions'],
                "failed_executions": row['failed_executions'],
                "success_rate": row['successful_executions'] / max(row['total_executions'], 1),
                "average_score": row['average_score'],
                "weight": row['weight'],
                "last_execution_at": row['last_execution_at']
            }
        return None
    
    def get_all_action_stats(self) -> List[Dict]:
        """Get all action statistics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM action_stats ORDER BY average_score DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "action_id": row['action_id'],
                "total_executions": row['total_executions'],
                "successful_executions": row['successful_executions'],
                "failed_executions": row['failed_executions'],
                "success_rate": row['successful_executions'] / max(row['total_executions'], 1),
                "average_score": row['average_score'],
                "weight": row['weight'],
                "last_execution_at": row['last_execution_at']
            }
            for row in rows
        ]
    
    def save_insight(self, insight: LearnedInsight) -> bool:
        """Save learned insight."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO insights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.insight_id,
                insight.insight_type.value,
                insight.description,
                insight.action_id,
                insight.confidence,
                json.dumps(insight.evidence),
                json.dumps(insight.recommendations),
                insight.created_at,
                insight.updated_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save insight: {e}")
            return False
    
    def get_insights(self, insight_type: InsightType = None) -> List[LearnedInsight]:
        """Get learned insights."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if insight_type:
            cursor.execute(
                "SELECT * FROM insights WHERE insight_type = ? ORDER BY confidence DESC",
                (insight_type.value,)
            )
        else:
            cursor.execute("SELECT * FROM insights ORDER BY confidence DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in rows:
            insights.append(LearnedInsight(
                insight_id=row['insight_id'],
                insight_type=InsightType(row['insight_type']),
                description=row['description'],
                action_id=row['action_id'] or "",
                confidence=row['confidence'],
                evidence=json.loads(row['evidence']) if row['evidence'] else [],
                recommendations=json.loads(row['recommendations']) if row['recommendations'] else [],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        return insights
    
    def log_weight_adjustment(self, adjustment: WeightAdjustment) -> bool:
        """Log weight adjustment."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO weight_adjustments VALUES (NULL, ?, ?, ?, ?, ?, ?)
            """, (
                adjustment.action_id,
                adjustment.previous_weight,
                adjustment.new_weight,
                adjustment.adjustment_factor,
                adjustment.reason,
                adjustment.timestamp
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to log adjustment: {e}")
            return False
    
    def update_weight(self, action_id: str, new_weight: float) -> bool:
        """Update action weight."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE action_stats SET weight = ? WHERE action_id = ?",
                (new_weight, action_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update weight: {e}")
            return False


# ============================================================================
# AI LEARNING ENGINE
# ============================================================================

class LearningEngine:
    """
    AI Learning Engine.
    Self-improving feedback loop with weight adjustment.
    """
    
    # Learning parameters
    LEARNING_RATE = 0.1
    MIN_WEIGHT = 0.1
    MAX_WEIGHT = 2.0
    SUCCESS_BONUS = 1.2
    FAILURE_PENALTY = 0.8
    
    def __init__(self):
        self.db = LearningDB()
        
        logger.info("LearningEngine initialized")
    
    def submit_feedback(
        self,
        action_id: str,
        plan_id: str,
        feedback_type: FeedbackType,
        score: float,
        outcome: str,
        context: Dict[str, Any] = None
    ) -> Dict:
        """
        Submit feedback for an action.
        Triggers weight adjustment.
        """
        import hashlib
        feedback_id = hashlib.md5(
            f"{action_id}{plan_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        feedback = ActionFeedback(
            feedback_id=f"FB-{feedback_id}",
            action_id=action_id,
            plan_id=plan_id,
            feedback_type=feedback_type,
            score=max(0.0, min(1.0, score)),  # Clamp to 0-1
            outcome=outcome,
            context=context or {},
            timestamp=datetime.now().isoformat()
        )
        
        # Record feedback
        self.db.record_feedback(feedback)
        
        # Update action stats
        self.db.update_action_stats(action_id, feedback_type, score)
        
        # Adjust weight
        weight_adjustment = self._adjust_weight(action_id, feedback_type, score)
        
        # Generate insights if needed
        self._check_and_generate_insights(action_id)
        
        return {
            "feedback_id": feedback.feedback_id,
            "action_id": action_id,
            "score": score,
            "weight_adjustment": {
                "previous": weight_adjustment.previous_weight,
                "new": weight_adjustment.new_weight,
                "factor": weight_adjustment.adjustment_factor
            }
        }
    
    def _adjust_weight(self, action_id: str, feedback_type: FeedbackType, score: float) -> WeightAdjustment:
        """Adjust action weight based on feedback."""
        stats = self.db.get_action_stats(action_id)
        
        current_weight = stats.get("weight", 1.0) if stats else 1.0
        
        # Calculate adjustment factor
        if feedback_type == FeedbackType.SUCCESS:
            # Success increases weight
            factor = self.SUCCESS_BONUS + (score - 0.5) * self.LEARNING_RATE
        elif feedback_type == FeedbackType.PARTIAL_SUCCESS:
            # Partial success maintains weight
            factor = 1.0 + (score - 0.5) * self.LEARNING_RATE * 0.5
        else:
            # Failure decreases weight
            factor = self.FAILURE_PENALTY - (1.0 - score) * self.LEARNING_RATE
        
        # Calculate new weight
        new_weight = current_weight * factor
        new_weight = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))
        
        # Update in database
        self.db.update_weight(action_id, new_weight)
        
        # Log adjustment
        adjustment = WeightAdjustment(
            action_id=action_id,
            previous_weight=current_weight,
            new_weight=new_weight,
            adjustment_factor=factor,
            reason=f"{feedback_type.value}: {score:.2f}",
            timestamp=datetime.now().isoformat()
        )
        self.db.log_weight_adjustment(adjustment)
        
        # Also sync with Planning Engine
        self._sync_weight_to_planning(action_id, new_weight)
        
        logger.info(f"Weight adjusted for {action_id}: {current_weight:.2f} -> {new_weight:.2f}")
        
        return adjustment
    
    def _sync_weight_to_planning(self, action_id: str, weight: float):
        """Sync weight to planning engine."""
        try:
            from app.intelligence.planning_engine import get_planning_engine
            
            planning = get_planning_engine()
            if hasattr(planning.db, 'update_action_weight'):
                planning.db.update_action_weight(action_id, weight)
        except Exception as e:
            logger.debug(f"Could not sync weight to planning: {e}")
    
    def _check_and_generate_insights(self, action_id: str):
        """Check for patterns and generate insights."""
        stats = self.db.get_action_stats(action_id)
        
        if not stats or stats["total_executions"] < 3:
            return
        
        # Generate insight if confidence is high
        if stats["success_rate"] > 0.8 and stats["total_executions"] >= 5:
            import hashlib
            insight_id = hashlib.md5(
                f"insight-{action_id}-{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12].upper()
            
            insight = LearnedInsight(
                insight_id=f"INS-{insight_id}",
                insight_type=InsightType.ACTION_SUCCESS_RATE,
                description=f"Action {action_id} has {stats['success_rate']*100:.0f}% success rate over {stats['total_executions']} executions",
                action_id=action_id,
                confidence=min(0.9, stats["success_rate"]),
                evidence=[
                    f"{stats['successful_executions']} successful executions",
                    f"Average score: {stats['average_score']:.2f}"
                ],
                recommendations=[
                    f"Increase weight for {action_id}" if stats["success_rate"] > 0.8 else None,
                    "Consider as default action"
                ],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.db.save_insight(insight)
    
    def get_insights(self, insight_type: str = None) -> List[Dict]:
        """Get learned insights."""
        itype = None
        if insight_type:
            try:
                itype = InsightType(insight_type)
            except:
                pass
        
        insights = self.db.get_insights(itype)
        
        return [
            {
                "id": i.insight_id,
                "type": i.insight_type.value,
                "description": i.description,
                "action_id": i.action_id,
                "confidence": i.confidence,
                "evidence": i.evidence,
                "recommendations": i.recommendations,
                "created_at": i.created_at
            }
            for i in insights
        ]
    
    def get_action_performance(self, action_id: str = None) -> List[Dict]:
        """Get action performance data."""
        if action_id:
            stats = self.db.get_action_stats(action_id)
            return [stats] if stats else []
        
        return self.db.get_all_action_stats()
    
    def optimize_weights(self) -> Dict:
        """Optimize all action weights based on accumulated data."""
        all_stats = self.db.get_all_action_stats()
        
        optimizations = []
        
        for stats in all_stats:
            if stats["total_executions"] < 3:
                continue
            
            action_id = stats["action_id"]
            success_rate = stats["success_rate"]
            avg_score = stats["average_score"]
            
            # Calculate optimal weight based on performance
            if success_rate > 0.8:
                optimal_weight = 1.5
            elif success_rate > 0.6:
                optimal_weight = 1.0
            elif success_rate > 0.4:
                optimal_weight = 0.7
            else:
                optimal_weight = 0.3
            
            # Apply gradual adjustment
            current_weight = stats["weight"]
            adjustment = (optimal_weight - current_weight) * 0.1  # Gradual change
            new_weight = current_weight + adjustment
            new_weight = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))
            
            if abs(new_weight - current_weight) > 0.01:
                self.db.update_weight(action_id, new_weight)
                self._sync_weight_to_planning(action_id, new_weight)
                
                optimizations.append({
                    "action_id": action_id,
                    "previous_weight": current_weight,
                    "new_weight": new_weight,
                    "success_rate": success_rate,
                    "reason": "Performance-based optimization"
                })
        
        return {
            "total_actions": len(all_stats),
            "optimized": len(optimizations),
            "optimizations": optimizations
        }
    
    def get_learning_summary(self) -> Dict:
        """Get overall learning summary."""
        all_stats = self.db.get_all_action_stats()
        insights = self.db.get_insights()
        
        total_executions = sum(s["total_executions"] for s in all_stats)
        total_successes = sum(s["successful_executions"] for s in all_stats)
        overall_success_rate = total_successes / max(total_executions, 1)
        
        # Top performing actions
        top_actions = sorted(
            all_stats,
            key=lambda x: x["success_rate"],
            reverse=True
        )[:5]
        
        # Actions needing improvement
        needs_work = sorted(
            [s for s in all_stats if s["total_executions"] >= 3],
            key=lambda x: x["success_rate"]
        )[:5]
        
        return {
            "total_actions": len(all_stats),
            "total_executions": total_executions,
            "total_successes": total_successes,
            "overall_success_rate": overall_success_rate,
            "insights_generated": len(insights),
            "top_performing_actions": [
                {"action_id": a["action_id"], "success_rate": a["success_rate"]}
                for a in top_actions
            ],
            "actions_needing_work": [
                {"action_id": a["action_id"], "success_rate": a["success_rate"]}
                for a in needs_work
            ]
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_learning_engine: Optional[LearningEngine] = None


def get_learning_engine() -> LearningEngine:
    """Get or create global learning engine."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine()
    return _learning_engine
