"""
MAHALAKSMI AIOS v1.0 - Volume III Chapter 28: Testing Center
Automated diagnostic orchestration with test discovery and health checks
"""
import os
import sys
import asyncio
import logging
import subprocess
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import importlib.util
import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class TestStatus(Enum):
    """Test status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class HealthStatus(Enum):
    """System health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class DiscoveredTest:
    """Discovered test file."""
    file_path: str
    test_name: str
    module_name: str
    class_name: Optional[str] = None
    function_name: str = ""


@dataclass
class TestResult:
    """Single test result."""
    test_name: str
    status: TestStatus
    duration_ms: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None


@dataclass
class DiagnosticResult:
    """Diagnostic run result."""
    run_id: str
    started_at: str
    completed_at: str
    duration_seconds: float
    health_status: HealthStatus
    
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    
    test_results: List[TestResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SystemHealth:
    """System health check result."""
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: str = ""


# ============================================================================
# TEST DISCOVERY
# ============================================================================

class TestDiscovery:
    """Discovers test files in the tests directory."""
    
    def __init__(self, tests_dir: str = None):
        if tests_dir is None:
            # Default to project tests directory
            self.tests_dir = Path(__file__).parent.parent.parent / "tests"
        else:
            self.tests_dir = Path(tests_dir)
    
    def discover(self) -> List[DiscoveredTest]:
        """Discover all test files."""
        tests = []
        
        if not self.tests_dir.exists():
            logger.warning(f"Tests directory not found: {self.tests_dir}")
            return tests
        
        for test_file in self.tests_dir.glob("test_*.py"):
            discovered = self._parse_test_file(test_file)
            tests.extend(discovered)
        
        logger.info(f"Discovered {len(tests)} tests in {self.tests_dir}")
        return tests
    
    def _parse_test_file(self, file_path: Path) -> List[DiscoveredTest]:
        """Parse test file to find test functions/classes."""
        tests = []
        
        try:
            module_name = file_path.stem
            
            # Load module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return tests
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find test classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.startswith("Test"):
                    # Find test methods
                    for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                        if method_name.startswith("test_"):
                            tests.append(DiscoveredTest(
                                file_path=str(file_path),
                                test_name=f"{name}.{method_name}",
                                module_name=module_name,
                                class_name=name,
                                function_name=method_name
                            ))
            
            # Find standalone test functions
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if name.startswith("test_") and not name.startswith("Test"):
                    tests.append(DiscoveredTest(
                        file_path=str(file_path),
                        test_name=name,
                        module_name=module_name,
                        function_name=name
                    ))
        
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
        
        return tests


# ============================================================================
# PYTEST ORCHESTRATION
# ============================================================================

class PytestOrchestrator:
    """Orchestrates pytest execution."""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.tests_dir = self.project_root / "tests"
    
    async def run_tests(
        self,
        test_path: str = None,
        markers: List[str] = None,
        verbose: bool = True
    ) -> Tuple[int, int, int, str]:
        """
        Run pytest programmatically.
        Returns: (passed, failed, errors, output)
        """
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir if test_path is None else test_path),
            "-v" if verbose else "-q",
            "--tb=short",
            "--no-header",
            "-o", "json_report=/tmp/pytest_report.json"
        ]
        
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            output = result.stdout + "\n" + result.stderr
            
            # Parse results
            passed = len(re.findall(r"PASSED", output))
            failed = len(re.findall(r"FAILED", output))
            errors = len(re.findall(r"ERROR", output))
            skipped = len(re.findall(r"SKIPPED", output))
            
            # Try to read JSON report
            try:
                with open("/tmp/pytest_report.json", "r") as f:
                    report = json.load(f)
                    passed = report.get("summary", {}).get("passed", passed)
                    failed = report.get("summary", {}).get("failed", failed)
                    errors = report.get("summary", {}).get("error", errors)
            except:
                pass
            
            return passed, failed, errors, output
        
        except subprocess.TimeoutExpired:
            return 0, 0, 1, "Test execution timed out after 5 minutes"
        except Exception as e:
            return 0, 0, 1, f"Test execution failed: {str(e)}"


# ============================================================================
# HEALTH CHECKS
# ============================================================================

class HealthChecker:
    """System health checker."""
    
    def __init__(self):
        self.checks = {
            "api": self._check_api,
            "database": self._check_database,
            "memory": self._check_memory_system,
            "revenue": self._check_revenue_system,
            "analytics": self._check_analytics_system
        }
    
    async def run_all_checks(self) -> List[SystemHealth]:
        """Run all health checks."""
        results = []
        
        for component, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                results.append(result)
            except Exception as e:
                results.append(SystemHealth(
                    component=component,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(e)}",
                    checked_at=datetime.now().isoformat()
                ))
        
        return results
    
    def _check_api(self) -> SystemHealth:
        """Check API health."""
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            
            if response.status_code == 200:
                return SystemHealth(
                    component="api",
                    status=HealthStatus.HEALTHY,
                    message="API is responding",
                    details=response.json(),
                    checked_at=datetime.now().isoformat()
                )
            else:
                return SystemHealth(
                    component="api",
                    status=HealthStatus.DEGRADED,
                    message=f"API returned status {response.status_code}",
                    checked_at=datetime.now().isoformat()
                )
        except ImportError:
            return SystemHealth(
                component="api",
                status=HealthStatus.DEGRADED,
                message="requests library not available",
                checked_at=datetime.now().isoformat()
            )
        except Exception as e:
            return SystemHealth(
                component="api",
                status=HealthStatus.UNHEALTHY,
                message=f"API unreachable: {str(e)}",
                checked_at=datetime.now().isoformat()
            )
    
    def _check_database(self) -> SystemHealth:
        """Check database connectivity."""
        try:
            db_paths = [
                self._get_db_path("data/memory.db"),
                self._get_db_path("data/products.db"),
                self._get_db_path("data/notifications.db")
            ]
            
            healthy_dbs = []
            for path in db_paths:
                if os.path.exists(path):
                    healthy_dbs.append(os.path.basename(path))
            
            return SystemHealth(
                component="database",
                status=HealthStatus.HEALTHY if healthy_dbs else HealthStatus.DEGRADED,
                message=f"{len(healthy_dbs)} database(s) accessible",
                details={"databases": healthy_dbs},
                checked_at=datetime.now().isoformat()
            )
        except Exception as e:
            return SystemHealth(
                component="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                checked_at=datetime.now().isoformat()
            )
    
    def _check_memory_system(self) -> SystemHealth:
        """Check memory system."""
        try:
            from app.intelligence.memory import get_memory
            memory = get_memory()
            stats = memory.get_stats()
            
            return SystemHealth(
                component="memory",
                status=HealthStatus.HEALTHY,
                message=f"{stats.get('total_entries', 0)} entries stored",
                details=stats,
                checked_at=datetime.now().isoformat()
            )
        except Exception as e:
            return SystemHealth(
                component="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory system error: {str(e)}",
                checked_at=datetime.now().isoformat()
            )
    
    def _check_revenue_system(self) -> SystemHealth:
        """Check revenue system."""
        try:
            from app.business.revenue import get_revenue_manager
            revenue = get_revenue_manager()
            summary = revenue.get_summary()
            
            return SystemHealth(
                component="revenue",
                status=HealthStatus.HEALTHY,
                message=f"Total revenue: Rp {summary.get('total_revenue', 0):,.0f}",
                details={
                    "total_revenue": summary.get("total_revenue", 0),
                    "transactions": summary.get("total_transactions", 0)
                },
                checked_at=datetime.now().isoformat()
            )
        except Exception as e:
            return SystemHealth(
                component="revenue",
                status=HealthStatus.UNHEALTHY,
                message=f"Revenue system error: {str(e)}",
                checked_at=datetime.now().isoformat()
            )
    
    def _check_analytics_system(self) -> SystemHealth:
        """Check analytics system."""
        try:
            from app.business.analytics import get_analytics
            analytics = get_analytics()
            summary = analytics.generate_summary()
            
            return SystemHealth(
                component="analytics",
                status=HealthStatus.HEALTHY,
                message="Analytics system operational",
                details={
                    "revenue_metrics": summary.revenue.total_gross_revenue > 0,
                    "has_distribution": hasattr(summary, 'distribution')
                },
                checked_at=datetime.now().isoformat()
            )
        except Exception as e:
            return SystemHealth(
                component="analytics",
                status=HealthStatus.UNHEALTHY,
                message=f"Analytics system error: {str(e)}",
                checked_at=datetime.now().isoformat()
            )
    
    def _get_db_path(self, relative_path: str) -> str:
        """Get absolute path for database."""
        return str(Path(__file__).parent.parent.parent / relative_path)


# ============================================================================
# TESTING CENTER
# ============================================================================

class TestingCenter:
    """
    Diagnostic orchestration center.
    Auto-discovers tests, runs pytest, and returns health status.
    """
    
    def __init__(self):
        self.discovery = TestDiscovery()
        self.orchestrator = PytestOrchestrator()
        self.health_checker = HealthChecker()
        
        self.last_diagnostic: Optional[DiagnosticResult] = None
        
        logger.info("TestingCenter initialized")
    
    def discover_tests(self) -> List[DiscoveredTest]:
        """Discover all available tests."""
        return self.discovery.discover()
    
    async def run_diagnostics(self, include_health: bool = True) -> DiagnosticResult:
        """
        Run full diagnostic suite.
        Returns formatted JSON summary.
        """
        import hashlib
        
        started_at = datetime.now()
        run_id = hashlib.md5(started_at.isoformat().encode()).hexdigest()[:12]
        
        result = DiagnosticResult(
            run_id=run_id,
            started_at=started_at.isoformat(),
            completed_at="",
            duration_seconds=0,
            health_status=HealthStatus.HEALTHY,
            total_tests=0,
            passed=0,
            failed=0,
            skipped=0,
            errors=0
        )
        
        # Run health checks
        if include_health:
            health_results = await self.health_checker.run_all_checks()
            
            # Determine overall health
            unhealthy_count = sum(
                1 for h in health_results 
                if h.status == HealthStatus.UNHEALTHY
            )
            degraded_count = sum(
                1 for h in health_results 
                if h.status == HealthStatus.DEGRADED
            )
            
            if unhealthy_count > 0:
                result.health_status = HealthStatus.UNHEALTHY
            elif degraded_count > 0:
                result.health_status = HealthStatus.DEGRADED
        
        # Run pytest
        passed, failed, errors, output = await self.orchestrator.run_tests()
        
        result.total_tests = passed + failed + errors
        result.passed = passed
        result.failed = failed
        result.errors = errors
        
        # Update health based on tests
        if failed > 0 or errors > 0:
            result.health_status = HealthStatus.DEGRADED
        if errors > result.total_tests * 0.5:
            result.health_status = HealthStatus.UNHEALTHY
        
        # Complete
        completed_at = datetime.now()
        result.completed_at = completed_at.isoformat()
        result.duration_seconds = (completed_at - started_at).total_seconds()
        
        # Extract errors/warnings from output
        result.errors = self._parse_errors(output)
        
        self.last_diagnostic = result
        logger.info(f"Diagnostic complete: {result.health_status.value} ({result.passed}/{result.total_tests} passed)")
        
        return result
    
    def _parse_errors(self, output: str) -> List[str]:
        """Parse error messages from pytest output."""
        errors = []
        
        # Extract FAILED lines
        for line in output.split("\n"):
            if "FAILED" in line:
                errors.append(line.strip())
        
        return errors[:10]  # Limit to 10 errors
    
    def get_summary(self) -> Dict[str, Any]:
        """Get diagnostic summary as JSON."""
        if not self.last_diagnostic:
            return {"message": "No diagnostics run yet"}
        
        d = self.last_diagnostic
        
        return {
            "run_id": d.run_id,
            "timestamp": d.completed_at,
            "duration_seconds": round(d.duration_seconds, 2),
            "health_status": d.health_status.value,
            
            "tests": {
                "total": d.total_tests,
                "passed": d.passed,
                "failed": d.failed,
                "errors": d.errors,
                "skipped": d.skipped,
                "success_rate": (
                    d.passed / max(d.total_tests, 1) * 100
                )
            },
            
            "errors": d.errors[:5],
            "warnings": d.warnings
        }
    
    def run_quick_health(self) -> Dict[str, Any]:
        """Quick health check without full test run."""
        health_results = asyncio.run(self.health_checker.run_all_checks())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "checks": [
                {
                    "component": h.component,
                    "status": h.status.value,
                    "message": h.message
                }
                for h in health_results
            ],
            "overall_status": (
                HealthStatus.HEALTHY.value 
                if all(h.status == HealthStatus.HEALTHY for h in health_results)
                else HealthStatus.DEGRADED.value
            )
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_testing_center: Optional[TestingCenter] = None


def get_testing_center() -> TestingCenter:
    """Get or create global testing center."""
    global _testing_center
    if _testing_center is None:
        _testing_center = TestingCenter()
    return _testing_center
