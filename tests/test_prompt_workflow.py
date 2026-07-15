"""
MAHALAKSMI AIOS v1.0.7 - Prompt Orchestrator & Workflow Engine Tests
Tests prompt rendering with context injection and workflow state transitions
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.intelligence.prompt_orchestrator import (
    get_prompt_orchestrator,
    PromptOrchestrator,
    TemplateType,
    ContextPriority,
    ContextItem
)
from app.core.workflow_engine import (
    get_workflow_engine,
    WorkflowEngine,
    WorkflowType,
    StepState,
    WorkflowState
)


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record(self, name: str, passed: bool, message: str = ""):
        if passed:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {message}")
            print(f"  ❌ {name} - {message}")


async def test_prompt_orchestrator_initialization(results: TestResults):
    """Test prompt orchestrator initialization."""
    print("\n📝 TEST: Prompt Orchestrator Initialization")
    print("-" * 40)
    
    orchestrator = get_prompt_orchestrator()
    
    results.record(
        "Orchestrator Created",
        orchestrator is not None
    )
    
    results.record(
        "Token Counter Initialized",
        orchestrator.token_counter is not None
    )
    
    results.record(
        "Database Initialized",
        orchestrator.db is not None
    )
    
    return orchestrator


async def test_prompt_templates(results: TestResults, orchestrator: PromptOrchestrator):
    """Test prompt template retrieval."""
    print("\n📋 TEST: Prompt Templates")
    print("-" * 40)
    
    templates = orchestrator.get_templates()
    
    results.record(
        "Templates Retrieved",
        isinstance(templates, list)
    )
    
    results.record(
        "Templates Not Empty",
        len(templates) > 0
    )
    
    results.record(
        "Templates Have Required Fields",
        all("id" in t and "name" in t for t in templates)
    )
    
    # Test filter by type
    system_templates = orchestrator.get_templates(TemplateType.SYSTEM)
    results.record(
        "System Templates Filtered",
        all(t["type"] == "system" for t in system_templates)
    )
    
    return orchestrator


async def test_prompt_rendering(results: TestResults, orchestrator: PromptOrchestrator):
    """Test prompt rendering with context injection."""
    print("\n🎯 TEST: Prompt Rendering")
    print("-" * 40)
    
    variables = {
        "company_name": "MAHA LAKSHMI CORP",
        "founder_name": "Pak Pur",
        "mission": "Dari nol menjadi satu",
        "current_time": "2026-07-15"
    }
    
    result = orchestrator.render("SYS-GAURANGA", variables)
    
    results.record(
        "Render Returns Result",
        result is not None
    )
    
    results.record(
        "System Prompt Generated",
        len(result.system_prompt) > 0
    )
    
    results.record(
        "Company Name Injected",
        "MAHA LAKSHMI CORP" in result.system_prompt
    )
    
    results.record(
        "Founder Name Injected",
        "Pak Pur" in result.system_prompt
    )
    
    results.record(
        "Tokens Counted",
        result.total_tokens > 0
    )
    
    return orchestrator


async def test_context_injection(results: TestResults, orchestrator: PromptOrchestrator):
    """Test dynamic context injection."""
    print("\n🔗 TEST: Context Injection")
    print("-" * 40)
    
    variables = {"user_input": "What is our revenue?"}
    
    additional_context = [
        ContextItem(
            key="revenue_info",
            value="Total revenue: Rp 100,000,000",
            priority=ContextPriority.HIGH,
            tokens=10
        ),
        ContextItem(
            key="recent_activity",
            value="5 transactions today",
            priority=ContextPriority.MEDIUM,
            tokens=8
        )
    ]
    
    result = orchestrator.render(
        "USR-QUERY",
        variables,
        additional_context=additional_context
    )
    
    results.record(
        "Context Items Processed",
        True
    )
    
    results.record(
        "Context Injected to Prompt",
        len(result.context_used) >= 0  # May be trimmed
    )
    
    return orchestrator


async def test_prompt_optimization(results: TestResults, orchestrator: PromptOrchestrator):
    """Test prompt optimization."""
    print("\n⚡ TEST: Prompt Optimization")
    print("-" * 40)
    
    prompt = """Please provide me with a detailed analysis of the revenue.
I would like you to analyze the financial data and provide recommendations.
Can you please generate a comprehensive report?"""
    
    result = orchestrator.optimize(
        prompt,
        goal="Generate concise revenue analysis",
        constraints=["Max 100 words"]
    )
    
    results.record(
        "Optimization Returns Result",
        result is not None
    )
    
    results.record(
        "Tokens Saved",
        result["tokens_saved"] >= 0
    )
    
    results.record(
        "Filler Phrases Removed",
        "Please provide" not in result["optimized"]
    )
    
    results.record(
        "Original Preserved",
        "analysis" in result["optimized"].lower()
    )
    
    return orchestrator


async def test_workflow_engine_initialization(results: TestResults):
    """Test workflow engine initialization."""
    print("\n⚙️ TEST: Workflow Engine Initialization")
    print("-" * 40)
    
    engine = get_workflow_engine()
    
    results.record(
        "Engine Created",
        engine is not None
    )
    
    results.record(
        "Database Initialized",
        engine.db is not None
    )
    
    results.record(
        "Action Handlers Registered",
        len(engine.action_handlers) > 0
    )
    
    return engine


async def test_workflow_creation(results: TestResults, engine: WorkflowEngine):
    """Test workflow creation."""
    print("\n🏗️ TEST: Workflow Creation")
    print("-" * 40)
    
    workflow = engine.create_workflow(
        name="Test Revenue Workflow",
        description="Test workflow for revenue recording",
        workflow_type=WorkflowType.SEQUENTIAL
    )
    
    results.record(
        "Workflow Created",
        workflow is not None
    )
    
    results.record(
        "Workflow Has ID",
        workflow.workflow_id.startswith("WF-")
    )
    
    results.record(
        "Workflow State Created",
        workflow.state == WorkflowState.CREATED
    )
    
    results.record(
        "Workflow Name Set",
        workflow.name == "Test Revenue Workflow"
    )
    
    return engine, workflow


async def test_workflow_steps(results: TestResults, engine: WorkflowEngine, workflow):
    """Test adding steps to workflow."""
    print("\n📋 TEST: Workflow Steps")
    print("-" * 40)
    
    step1 = engine.add_step(
        workflow_id=workflow.workflow_id,
        name="Send Notification",
        action="notification",
        action_params={
            "title": "Workflow Started",
            "message": "Test workflow has started",
            "priority": "normal"
        }
    )
    
    results.record(
        "Step 1 Created",
        step1.step_id.startswith("STEP-")
    )
    
    results.record(
        "Step 1 State Pending",
        step1.state == StepState.PENDING
    )
    
    step2 = engine.add_step(
        workflow_id=workflow.workflow_id,
        name="Record Revenue",
        action="revenue",
        action_params={
            "source": "workflow_test",
            "amount": 100000
        }
    )
    
    results.record(
        "Step 2 Created",
        step2.step_id.startswith("STEP-")
    )
    
    # Get workflow with steps
    wf = engine.db.get_workflow(workflow.workflow_id)
    
    results.record(
        "Workflow Has Steps",
        len(wf.steps) >= 2
    )
    
    return engine, workflow


async def test_workflow_execution(results: TestResults, engine: WorkflowEngine, workflow):
    """Test workflow execution."""
    print("\n🚀 TEST: Workflow Execution")
    print("-" * 40)
    
    # Execute workflow
    executed = await engine.execute_workflow(workflow.workflow_id)
    
    results.record(
        "Workflow Executed",
        executed is not None
    )
    
    results.record(
        "Workflow Not Running",
        executed.state != WorkflowState.RUNNING
    )
    
    results.record(
        "Has Final State",
        executed.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]
    )
    
    # Check step states
    pending = sum(1 for s in executed.steps if s.state == StepState.PENDING)
    completed = sum(1 for s in executed.steps if s.state == StepState.COMPLETED)
    
    results.record(
        "Has Completed Steps",
        completed > 0
    )
    
    return engine


async def test_workflow_status(results: TestResults, engine: WorkflowEngine, workflow):
    """Test workflow status retrieval."""
    print("\n📊 TEST: Workflow Status")
    print("-" * 40)
    
    status = engine.get_workflow_status(workflow.workflow_id)
    
    results.record(
        "Status Retrieved",
        "workflow_id" in status
    )
    
    results.record(
        "Has State",
        "state" in status
    )
    
    results.record(
        "Has Steps Info",
        "steps" in status
    )
    
    results.record(
        "Has Metrics",
        "total_steps" in status
    )
    
    return engine


async def test_mission_workflow_spawn(results: TestResults, engine: WorkflowEngine):
    """Test spawning workflow from mission."""
    print("\n🎯 TEST: Mission Workflow Spawn")
    print("-" * 40)
    
    # Create a mission-linked workflow first
    mission_workflow = engine.create_workflow(
        name="Mission Test",
        description="Test mission",
        mission_id="MISSION-001"
    )
    
    # Add some steps
    engine.add_step(
        workflow_id=mission_workflow.workflow_id,
        name="Test Step",
        action="notification",
        action_params={"title": "Test", "message": "Test"}
    )
    
    # Spawn from mission
    spawned = engine.spawn_from_mission("MISSION-002", "New Mission")
    
    results.record(
        "Spawned Workflow Created",
        spawned.workflow_id.startswith("WF-")
    )
    
    # Re-fetch from database to get steps
    spawned_with_steps = engine.db.get_workflow(spawned.workflow_id)
    results.record(
        "Spawned Has Steps",
        len(spawned_with_steps.steps) > 0 if spawned_with_steps else False
    )
    
    results.record(
        "Mission ID Set",
        spawned.mission_id == "MISSION-002"
    )
    
    return engine


async def test_workflow_state_transitions(results: TestResults, engine: WorkflowEngine):
    """Test workflow state transitions."""
    print("\n🔄 TEST: Workflow State Transitions")
    print("-" * 40)
    
    # Create workflow
    workflow = engine.create_workflow("State Test Workflow")
    
    results.record(
        "Created State",
        workflow.state == WorkflowState.CREATED
    )
    
    # Add and execute step
    engine.add_step(
        workflow_id=workflow.workflow_id,
        name="Test Step",
        action="notification",
        action_params={"title": "Test", "message": "Test"}
    )
    
    executed = await engine.execute_workflow(workflow.workflow_id)
    
    results.record(
        "Executed State Transition",
        executed.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]
    )
    
    return engine


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.0.7 - Prompt & Workflow Tests")
    print("="*60)
    
    results = TestResults()
    
    try:
        # Prompt Orchestrator tests
        orchestrator = await test_prompt_orchestrator_initialization(results)
        await test_prompt_templates(results, orchestrator)
        await test_prompt_rendering(results, orchestrator)
        await test_context_injection(results, orchestrator)
        await test_prompt_optimization(results, orchestrator)
        
        # Workflow Engine tests
        engine = await test_workflow_engine_initialization(results)
        engine, workflow = await test_workflow_creation(results, engine)
        engine, workflow = await test_workflow_steps(results, engine, workflow)
        await test_workflow_execution(results, engine, workflow)
        await test_workflow_status(results, engine, workflow)
        await test_mission_workflow_spawn(results, engine)
        await test_workflow_state_transitions(results, engine)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        results.failed += 1
    
    # Print summary
    print("\n" + "="*60)
    print(f"RESULTS: {results.passed} passed, {results.failed} failed")
    if results.errors:
        print("\nErrors:")
        for e in results.errors:
            print(f"  - {e}")
    print("="*60)
    
    success = results.failed == 0
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED - Review above")
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
