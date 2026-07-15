"""
MAHALAKSMI AIOS v1.0 - Volume II Chapter 18: Prompt & Context Orchestrator
Dynamic prompt optimization with context trimming and memory injection
"""
import os
import sys
import re
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

class TemplateType(Enum):
    """Prompt template types."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"


class ContextPriority(Enum):
    """Context element priority."""
    CRITICAL = 1   # Must include
    HIGH = 2       # Include if space allows
    MEDIUM = 3    # Include if not trimmed
    LOW = 4       # First to trim


@dataclass
class PromptTemplate:
    """Prompt template definition."""
    template_id: str
    name: str
    template_type: TemplateType
    template: str
    description: str = ""
    variables: List[str] = field(default_factory=list)
    priority: ContextPriority = ContextPriority.MEDIUM
    max_tokens: int = 2000
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ContextItem:
    """Context item for prompt injection."""
    key: str
    value: str
    priority: ContextPriority
    tokens: int
    source: str = "system"


@dataclass
class RenderedPrompt:
    """Rendered prompt result."""
    system_prompt: str
    user_prompt: str
    total_tokens: int
    context_used: List[str]
    trimmed_items: List[str]


# ============================================================================
# PROMPT ORCHESTRATOR DATABASE
# ============================================================================

class PromptOrchestratorDB:
    """SQLite database for prompt templates."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "prompt_orchestrator.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                template_id TEXT PRIMARY KEY,
                name TEXT,
                template_type TEXT,
                template TEXT,
                description TEXT,
                variables TEXT,
                priority TEXT,
                max_tokens INTEGER,
                created_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS render_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT,
                tokens_used INTEGER,
                context_items TEXT,
                rendered_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_template(self, template: PromptTemplate) -> bool:
        """Save template."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO templates VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template.template_id,
                template.name,
                template.template_type.value,
                template.template,
                template.description,
                json.dumps(template.variables),
                template.priority.value,
                template.max_tokens,
                template.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM templates WHERE template_id = ?", (template_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_template(row)
        return None
    
    def _row_to_template(self, row) -> PromptTemplate:
        """Convert row to PromptTemplate."""
        priority_val = row['priority']
        # Handle both string and int values
        try:
            priority = ContextPriority(priority_val)
        except ValueError:
            priority = ContextPriority(int(priority_val))
        
        return PromptTemplate(
            template_id=row['template_id'],
            name=row['name'],
            template_type=TemplateType(row['template_type']),
            template=row['template'],
            description=row['description'] or "",
            variables=json.loads(row['variables']) if row['variables'] else [],
            priority=priority,
            max_tokens=row['max_tokens'],
            created_at=row['created_at']
        )
    
    def get_all_templates(self) -> List[PromptTemplate]:
        """Get all templates."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM templates ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_template(row) for row in rows]
    
    def log_render(self, template_id: str, tokens: int, context_items: List[str]) -> bool:
        """Log render history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO render_history (template_id, tokens_used, context_items, rendered_at)
                VALUES (?, ?, ?, ?)
            """, (template_id, tokens, json.dumps(context_items), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to log render: {e}")
            return False


# ============================================================================
# TOKEN COUNTER (Simple approximation)
# ============================================================================

class TokenCounter:
    """Simple token counter using word/char approximation."""
    
    def __init__(self):
        # Rough estimation: ~4 chars per token for English, 2 chars for Indonesian
        self.avg_chars_per_token = 3.5
    
    def count(self, text: str) -> int:
        """Count tokens in text."""
        if not text:
            return 0
        
        # Split by whitespace
        words = text.split()
        
        # Add character-based adjustment
        char_count = len(text)
        
        # Estimate tokens
        return max(len(words), int(char_count / self.avg_chars_per_token))
    
    def estimate_available(self, max_tokens: int, current_tokens: int) -> int:
        """Calculate available tokens."""
        return max(0, max_tokens - current_tokens)


# ============================================================================
# PROMPT ORCHESTRATOR
# ============================================================================

class PromptOrchestrator:
    """
    Prompt & Context Orchestrator.
    Dynamic prompt optimization with context trimming and memory injection.
    """
    
    # Default max tokens for Gemini (leave room for response)
    DEFAULT_MAX_TOKENS = 6000
    
    def __init__(self):
        self.db = PromptOrchestratorDB()
        self.token_counter = TokenCounter()
        self._init_default_templates()
        
        logger.info("PromptOrchestrator initialized")
    
    def _init_default_templates(self):
        """Initialize default prompt templates."""
        templates = [
            PromptTemplate(
                template_id="SYS-GAURANGA",
                name="GAURANGA Alpha System",
                template_type=TemplateType.SYSTEM,
                template="""You are GAURANGA, the Alpha AI Agent for MAHA LAKSHMI CORP.
Company: {company_name}
Founder: {founder_name}
Mission: {mission}
Current Time: {current_time}

Your role is to assist {founder_name} with:
- Executive decision support
- Revenue optimization
- Multi-agent coordination
- Strategic planning

Always respond in Bahasa Indonesia with professional tone.
Use emojis sparingly for emphasis.
Context: {dynamic_context}""",
                description="Main system prompt for GAURANGA",
                variables=["company_name", "founder_name", "mission", "current_time", "dynamic_context"],
                priority=ContextPriority.CRITICAL,
                max_tokens=1500
            ),
            PromptTemplate(
                template_id="SYS-DECISION",
                name="Executive Decision Maker",
                template_type=TemplateType.SYSTEM,
                template="""You are an Executive Decision AI. Analyze the following situation and provide recommendations.

Company Profile:
- Total Revenue: {total_revenue}
- Monthly Target: {monthly_target}
- CEO Share: {ceo_share_pct}%

Recent Transactions:
{recent_transactions}

Available Options:
{options}

Provide a structured recommendation with:
1. Risk Assessment
2. Financial Impact
3. Strategic Fit
4. Recommendation""",
                description="Decision-making prompt",
                variables=["total_revenue", "monthly_target", "ceo_share_pct", "recent_transactions", "options"],
                priority=ContextPriority.HIGH,
                max_tokens=2000
            ),
            PromptTemplate(
                template_id="USR-QUERY",
                name="User Query Handler",
                template_type=TemplateType.USER,
                template="""User Query: {user_input}

Relevant Context:
{relevant_context}

Conversation History:
{history}

Please provide a helpful and accurate response.""",
                description="User query prompt",
                variables=["user_input", "relevant_context", "history"],
                priority=ContextPriority.MEDIUM,
                max_tokens=1000
            ),
            PromptTemplate(
                template_id="COT-ANALYSIS",
                name="Chain of Thought Analysis",
                template_type=TemplateType.CHAIN_OF_THOUGHT,
                template="""Problem: {problem}

Let me think through this step by step:

Step 1: {step_1}
Step 2: {step_2}
Step 3: {step_3}

Therefore, my conclusion is: {conclusion}

Confidence Level: {confidence}""",
                description="Chain of thought reasoning",
                variables=["problem", "step_1", "step_2", "step_3", "conclusion", "confidence"],
                priority=ContextPriority.MEDIUM,
                max_tokens=1500
            )
        ]
        
        for template in templates:
            self.db.save_template(template)
        
        logger.info(f"Initialized {len(templates)} default templates")
    
    def get_templates(self, template_type: TemplateType = None) -> List[Dict]:
        """Get all templates."""
        templates = self.db.get_all_templates()
        
        if template_type:
            templates = [t for t in templates if t.template_type == template_type]
        
        return [
            {
                "id": t.template_id,
                "name": t.name,
                "type": t.template_type.value,
                "description": t.description,
                "variables": t.variables,
                "max_tokens": t.max_tokens
            }
            for t in templates
        ]
    
    def render(
        self,
        template_id: str,
        variables: Dict[str, Any],
        additional_context: List[ContextItem] = None,
        max_tokens: int = None
    ) -> RenderedPrompt:
        """
        Render a prompt with dynamic context injection.
        """
        template = self.db.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Set max tokens
        if max_tokens is None:
            max_tokens = self.DEFAULT_MAX_TOKENS
        
        # Collect all context items
        context_items = []
        
        # Add dynamic context from Knowledge Graph
        kg_context = self._get_knowledge_graph_context()
        context_items.extend(kg_context)
        
        # Add additional context
        if additional_context:
            context_items.extend(additional_context)
        
        # Sort by priority
        context_items.sort(key=lambda x: x.priority.value)
        
        # Render template with variables
        rendered = template.template
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            rendered = rendered.replace(placeholder, str(value))
        
        # Calculate base tokens
        base_tokens = self.token_counter.count(rendered)
        
        # Build dynamic context string
        dynamic_context = ""
        context_used = []
        trimmed_items = []
        
        available = self.token_counter.estimate_available(max_tokens, base_tokens)
        
        for item in context_items:
            if item.tokens <= available:
                dynamic_context += f"\n[{item.key}]: {item.value}"
                context_used.append(item.key)
                available -= item.tokens
            else:
                trimmed_items.append(item.key)
        
        # Inject dynamic context
        if "{dynamic_context}" in rendered:
            rendered = rendered.replace("{dynamic_context}", dynamic_context or "(No additional context)")
        
        # Trim if still too long
        final_tokens = self.token_counter.count(rendered)
        if final_tokens > max_tokens:
            rendered = self._trim_prompt(rendered, max_tokens)
            final_tokens = self.token_counter.count(rendered)
        
        # Log render
        self.db.log_render(template_id, final_tokens, context_used)
        
        return RenderedPrompt(
            system_prompt=rendered,
            user_prompt="",
            total_tokens=final_tokens,
            context_used=context_used,
            trimmed_items=trimmed_items
        )
    
    def _get_knowledge_graph_context(self) -> List[ContextItem]:
        """Get context from Knowledge Graph."""
        items = []
        
        try:
            from app.intelligence.knowledge_graph import get_knowledge_graph
            
            kg = get_knowledge_graph()
            stats = kg.get_graph_stats()
            
            # Add graph stats as context
            items.append(ContextItem(
                key="knowledge_graph_stats",
                value=f"Total entities: {stats['total_nodes']}, Total relationships: {stats['total_edges']}",
                priority=ContextPriority.MEDIUM,
                tokens=30,
                source="knowledge_graph"
            ))
            
            # Add top nodes
            nodes = kg.get_nodes()[:5]
            if nodes:
                node_names = [n['name'] for n in nodes]
                items.append(ContextItem(
                    key="top_entities",
                    value=", ".join(node_names),
                    priority=ContextPriority.LOW,
                    tokens=20,
                    source="knowledge_graph"
                ))
        
        except Exception as e:
            logger.debug(f"Could not load KG context: {e}")
        
        return items
    
    def _get_system_state_context(self) -> List[ContextItem]:
        """Get system state context."""
        items = []
        
        try:
            # Revenue state
            from app.business.revenue import get_revenue_manager
            revenue = get_revenue_manager()
            summary = revenue.get_summary()
            
            items.append(ContextItem(
                key="revenue_state",
                value=f"Total: Rp {summary.get('total_revenue', 0):,.0f}, Transactions: {summary.get('total_transactions', 0)}",
                priority=ContextPriority.HIGH,
                tokens=40,
                source="revenue_system"
            ))
            
            # Mission state
            from app.enterprise.mission_control import get_mission_control
            mc = get_mission_control()
            dashboard = mc.get_dashboard()
            
            items.append(ContextItem(
                key="mission_state",
                value=f"Missions: {dashboard['missions']['total']}, Completed: {dashboard['missions']['by_status'].get('completed', 0)}",
                priority=ContextPriority.MEDIUM,
                tokens=30,
                source="mission_control"
            ))
        
        except Exception as e:
            logger.debug(f"Could not load system state context: {e}")
        
        return items
    
    def _trim_prompt(self, prompt: str, max_tokens: int) -> str:
        """
        Trim prompt using sliding window approach.
        Preserves beginning and end, trims middle.
        """
        current_tokens = self.token_counter.count(prompt)
        
        if current_tokens <= max_tokens:
            return prompt
        
        # Keep first 30% and last 70%
        target_tokens = int(max_tokens * 0.9)
        
        lines = prompt.split("\n")
        total_lines = len(lines)
        
        keep_first = max(1, int(total_lines * 0.3))
        keep_last = max(1, int(total_lines * 0.7))
        
        trimmed = lines[:keep_first] + ["... [content trimmed] ..."] + lines[-keep_last:]
        
        result = "\n".join(trimmed)
        
        # If still too long, truncate
        while self.token_counter.count(result) > max_tokens and len(result) > 100:
            result = result[:int(len(result) * 0.9)]
        
        return result
    
    def optimize(
        self,
        prompt: str,
        goal: str,
        constraints: List[str] = None
    ) -> Dict:
        """
        Optimize a prompt for better results.
        """
        original_tokens = self.token_counter.count(prompt)
        
        # Basic optimizations
        optimized = prompt
        
        # Remove redundant whitespace
        optimized = re.sub(r'\n\s*\n\s*\n', '\n\n', optimized)
        optimized = re.sub(r' +', ' ', optimized)
        
        # Remove common filler phrases
        filler_phrases = [
            "Please provide",
            "I would like you to",
            "Can you please",
            "In conclusion,",
            "To summarize,"
        ]
        
        for phrase in filler_phrases:
            optimized = optimized.replace(phrase, "")
        
        # Ensure clear instructions
        if not optimized.strip().endswith((".", "?", "!")):
            optimized = optimized.strip() + "."
        
        optimized_tokens = self.token_counter.count(optimized)
        
        return {
            "original": prompt,
            "optimized": optimized,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": original_tokens - optimized_tokens,
            "improvement_pct": round((original_tokens - optimized_tokens) / max(original_tokens, 1) * 100, 2),
            "goal": goal,
            "constraints": constraints or []
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_prompt_orchestrator: Optional[PromptOrchestrator] = None


def get_prompt_orchestrator() -> PromptOrchestrator:
    """Get or create global prompt orchestrator."""
    global _prompt_orchestrator
    if _prompt_orchestrator is None:
        _prompt_orchestrator = PromptOrchestrator()
    return _prompt_orchestrator
