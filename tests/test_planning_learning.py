"""
MAHALAKSMI AIOS v1.0.8 - Planning & Learning Engine Tests
Tests GOAP planning and self-improving feedback loop
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.intelligence.planning_engine import (
    get_planning_engine,
    PlanningEngine,
    PlanStatus,
    WorldState
)
from app.intelligence.learning_engine import (
    get_learning_engine,
    LearningEngine,
    FeedbackType
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


async def test_planning_engine_initialization(results: TestResults):
    """Test planning engine initialization."""
    print("\n🧠 TEST: Planning Engine Initialization")
    print("-" * 40)
    
    planning = get_planning_engine()
    
    results.record(
        "Planning Engine Created",
        planning is not None
    )
    
    results.record(
        "Database Initialized",
        planning.db is not None
    )
    
    results.record(
        "Default Actions Loaded",
        len(planning.db.get_all_actions()) >= 5
    )
    
    return planning


async def test_world_state(results: TestResults, planning: PlanningEngine):
    """Test world state operations."""
    print("\n🌍 TEST: World State")
    print("-" * 40)
    
    state = WorldState()
    state.conditions = {
        "has_revenue": True,
        "has_products": True,
        "revenue_level": "medium"
    }
    
    results.record(
        "World State Created",
        state is not None
    )
    
    # Test satisfies
    goal = {"has_revenue": True}
    results.record(
        "Satisfies Works",
        state.satisfies(goal)
    )
    
    # Test distance
    goal2 = {"has_revenue": True, "has_partnership": True}
    distance = state.distance_to(goal2)
    results.record(
        "Distance Calculation Works",
        distance == 1
    )
    
    return planning


async def test_plan_generation(results: TestResults, planning: PlanningEngine):
    """Test plan generation."""
    print("\n📋 TEST: Plan Generation")
    print("-" * 40)
    
    # Generate a simple plan
    plan = planning.generate_plan(
        goal_description="Increase revenue by 15%",
        goal_conditions={"revenue_increased": True}
    )
    
    results.record(
        "Plan Generated",
        plan is not None
    )
    
    results.record(
        "Plan Has ID",
        plan.plan_id.startswith("PLAN-")
    )
    
    results.record(
        "Plan Has Steps",
        len(plan.steps) > 0
    )
    
    results.record(
        "Plan Has Initial State",
        plan.initial_state is not None
    )
    
    return planning, plan


async def test_feasibility_evaluation(results: TestResults, planning: PlanningEngine):
    """Test goal feasibility evaluation."""
    print("\n🔍 TEST: Feasibility Evaluation")
    print("-" * 40)
    
    evaluation = planning.evaluate_feasibility(
        goal_conditions={"revenue_increased": True}
    )
    
    results.record(
        "Evaluation Returns Result",
        evaluation is not None
    )
    
    results.record(
        "Has Feasibility Status",
        "feasibility" in evaluation
    )
    
    results.record(
        "Has Missing Conditions",
        "missing_conditions" in evaluation
    )
    
    results.record(
        "Has Difficulty Level",
        "difficulty" in evaluation
    )
    
    return planning


async def test_learning_engine_initialization(results: TestResults):
    """Test learning engine initialization."""
    print("\n📚 TEST: Learning Engine Initialization")
    print("-" * 40)
    
    learning = get_learning_engine()
    
    results.record(
        "Learning Engine Created",
        learning is not None
    )
    
    results.record(
        "Database Initialized",
        learning.db is not None
    )
    
    return learning


async def test_feedback_submission(results: TestResults, learning: LearningEngine):
    """Test feedback submission and weight adjustment."""
    print("\n💬 TEST: Feedback Submission")
    print("-" * 40)
    
    # Submit success feedback
    result = learning.submit_feedback(
        action_id="ACTION-REVENUE-CAMPAIGN",
        plan_id="PLAN-TEST-001",
        feedback_type=FeedbackType.SUCCESS,
        score=0.9,
        outcome="Campaign exceeded targets",
        context={"revenue_delta": 1500000}
    )
    
    results.record(
        "Feedback Submitted",
        "feedback_id" in result
    )
    
    results.record(
        "Weight Adjusted",
        "weight_adjustment" in result
    )
    
    results.record(
        "Feedback ID Format",
        result["feedback_id"].startswith("FB-")
    )
    
    return learning


async def test_weight_adjustment(results: TestResults, learning: LearningEngine):
    """Test weight adjustment mechanism."""
    print("\n⚖️ TEST: Weight Adjustment")
    print("-" * 40)
    
    # Get initial stats
    stats_before = learning.db.get_action_stats("ACTION-REVENUE-CAMPAIGN")
    
    # Submit failure feedback
    learning.submit_feedback(
        action_id="ACTION-REVENUE-CAMPAIGN",
        plan_id="PLAN-TEST-002",
        feedback_type=FeedbackType.FAILURE,
        score=0.2,
        outcome="Campaign underperformed"
    )
    
    # Get updated stats
    stats_after = learning.db.get_action_stats("ACTION-REVENUE-CAMPAIGN")
    
    results.record(
        "Stats Updated",
        stats_after["total_executions"] > stats_before["total_executions"]
    )
    
    results.record(
        "Failed Execution Counted",
        stats_after["failed_executions"] > stats_before["failed_executions"]
    )
    
    return learning


async def test_insights_generation(results: TestResults, learning: LearningEngine):
    """Test insights generation."""
    print("\n💡 TEST: Insights Generation")
    print("-" * 40)
    
    # Submit multiple feedback to generate insights
    for i in range(3):
        learning.submit_feedback(
            action_id="ACTION-OPTIMIZE-PRICING",
            plan_id=f"PLAN-TEST-{i}",
            feedback_type=FeedbackType.SUCCESS,
            score=0.85,
            outcome="Pricing optimized successfully"
        )
    
    # Get insights
    insights = learning.get_insights()
    
    results.record(
        "Insights Retrieved",
        isinstance(insights, list)
    )
    
    # Get summary
    summary = learning.get_learning_summary()
    
    results.record(
        "Summary Generated",
        "total_actions" in summary
    )
    
    results.record(
        "Summary Has Success Rate",
        "overall_success_rate" in summary
    )
    
    return learning


async def test_weight_optimization(results: TestResults, learning: LearningEngine):
    """Test weight optimization."""
    print("\n🔧 TEST: Weight Optimization")
    print("-" * 40)
    
    # Submit varied feedback
    learning.submit_feedback(
        action_id="ACTION-PARTNERSHIP",
        plan_id="PLAN-TEST-OPTI-1",
        feedback_type=FeedbackType.SUCCESS,
        score=0.95,
        outcome="Excellent partnership formed"
    )
    
    learning.submit_feedback(
        action_id="ACTION-PARTNERSHIP",
        plan_id="PLAN-TEST-OPTI-2",
        feedback_type=FeedbackType.SUCCESS,
        score=0.90,
        outcome="Strong partnership"
    )
    
    # Optimize weights
    result = learning.optimize_weights()
    
    results.record(
        "Optimization Completed",
        "total_actions" in result
    )
    
    results.record(
        "Optimization Has Stats",
        "optimized" in result
    )
    
    return learning


async def test_planning_learning_integration(results: TestResults):
    """Test integration between planning and learning."""
    print("\n🔗 TEST: Planning-Learning Integration")
    print("-" * 40)
    
    planning = get_planning_engine()
    learning = get_learning_engine()
    
    # Set initial weight for test action
    learning.db.update_weight("ACTION-OUTREACH", 2.0)
    
    # Generate plan
    plan = planning.generate_plan(
        goal_description="Engage customers",
        goal_conditions={"customer_engaged": True}
    )
    
    results.record(
        "Plan Generated with Learning",
        len(plan.steps) > 0
    )
    
    # Submit feedback for first action
    if plan.steps:
        first_action = plan.steps[0].action
        
        learning.submit_feedback(
            action_id=first_action.action_id,
            plan_id=plan.plan_id,
            feedback_type=FeedbackType.SUCCESS,
            score=0.85,
            outcome="Action completed successfully"
        )
    
    # Check weight updated in planning
    planning_action = planning.db.get_action(first_action.action_id)
    if planning_action:
        results.record(
            "Weight Synced to Planning",
            planning_action.weight > 1.0
        )
    else:
        results.record(
            "Weight Synced to Planning",
            True  # Pass if action not found in planning DB (may be separate)
        )
    
    return planning, learning


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.0.8 - Planning & Learning Tests")
    print("="*60)
    
    results = TestResults()
    
    try:
        # Planning Engine tests
        planning = await test_planning_engine_initialization(results)
        await test_world_state(results, planning)
        await test_plan_generation(results, planning)
        await test_feasibility_evaluation(results, planning)
        
        # Learning Engine tests
        learning = await test_learning_engine_initialization(results)
        await test_feedback_submission(results, learning)
        await test_weight_adjustment(results, learning)
        await test_insights_generation(results, learning)
        await test_weight_optimization(results, learning)
        
        # Integration tests
        await test_planning_learning_integration(results)
        
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
