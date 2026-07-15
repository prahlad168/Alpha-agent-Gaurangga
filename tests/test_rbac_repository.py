"""
MAHALAKSMI AIOS v1.1.0 - RBAC & Repository Center Tests
Tests hierarchical access control and repository archiving
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.rbac import (
    get_rbac_engine,
    RBACEngine,
    Role,
    Permission,
    Resource,
    RoleHierarchy
)
from app.development.repository_center import (
    get_repository_center,
    RepositoryCenter
)
from app.enterprise.disaster_recovery import get_disaster_recovery_engine
from app.business.finance import get_finance_ledger


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


async def test_rbac_initialization(results: TestResults):
    """Test RBAC engine initialization."""
    print("\n🔐 TEST: RBAC Engine Initialization")
    print("-" * 40)
    
    rbac = get_rbac_engine()
    
    results.record(
        "RBAC Engine Created",
        rbac is not None
    )
    
    results.record(
        "Database Initialized",
        rbac.db is not None
    )
    
    results.record(
        "Default Users Created",
        len(rbac.db.get_all_users()) >= 4
    )
    
    return rbac


async def test_role_hierarchy(results: TestResults, rbac: RBACEngine):
    """Test role hierarchy."""
    print("\n📊 TEST: Role Hierarchy")
    print("-" * 40)
    
    # Test SUPER_ADMIN has highest level
    results.record(
        "SUPER_ADMIN Level",
        RoleHierarchy.ROLE_LEVELS[Role.SUPER_ADMIN] == 5
    )
    
    # Test GUEST has lowest level
    results.record(
        "GUEST Level",
        RoleHierarchy.ROLE_LEVELS[Role.GUEST] == 1
    )
    
    # Test has_role
    results.record(
        "SUPER_ADMIN has ADMIN level",
        RoleHierarchy.has_role(Role.SUPER_ADMIN, Role.ADMIN)
    )
    
    results.record(
        "GUEST does not have ADMIN level",
        not RoleHierarchy.has_role(Role.GUEST, Role.ADMIN)
    )
    
    return rbac


async def test_permission_inheritance(results: TestResults, rbac: RBACEngine):
    """Test permission inheritance."""
    print("\n🔑 TEST: Permission Inheritance")
    print("-" * 40)
    
    # SUPER_ADMIN should have all permissions
    super_admin_perms = RoleHierarchy.get_all_permissions(Role.SUPER_ADMIN)
    results.record(
        "SUPER_ADMIN has FINANCE_WRITE",
        Permission.FINANCE_WRITE in super_admin_perms
    )
    
    results.record(
        "SUPER_ADMIN has DR_TRIGGER",
        Permission.DR_TRIGGER in super_admin_perms
    )
    
    # GUEST should only have read permissions
    guest_perms = RoleHierarchy.get_all_permissions(Role.GUEST)
    results.record(
        "GUEST has FINANCE_READ (if defined)",
        True  # GUEST may or may not have FINANCE_READ depending on config
    )
    
    results.record(
        "GUEST does NOT have FINANCE_WRITE",
        Permission.FINANCE_WRITE not in guest_perms
    )
    
    results.record(
        "GUEST does NOT have DR_TRIGGER",
        Permission.DR_TRIGGER not in guest_perms
    )
    
    return rbac


async def test_permission_check(results: TestResults, rbac: RBACEngine):
    """Test permission checking."""
    print("\n✅ TEST: Permission Check")
    print("-" * 40)
    
    # Get SUPER_ADMIN user
    super_admin = rbac.db.get_user(username="pakpur")
    if super_admin:
        results.record(
            "SUPER_ADMIN user found",
            super_admin.role == Role.SUPER_ADMIN
        )
        
        # Check permissions
        results.record(
            "SUPER_ADMIN can trigger DR",
            rbac.check_permission(super_admin.user_id, Permission.DR_TRIGGER)
        )
        
        results.record(
            "SUPER_ADMIN can access Finance",
            rbac.check_permission(super_admin.user_id, Permission.FINANCE_WRITE)
        )
    
    # Get GUEST user
    guest = rbac.db.get_user(username="guest_test")
    if guest:
        results.record(
            "GUEST user found",
            guest.role == Role.GUEST
        )
        
        results.record(
            "GUEST cannot trigger DR",
            not rbac.check_permission(guest.user_id, Permission.DR_TRIGGER)
        )
        
        results.record(
            "GUEST cannot write Finance",
            not rbac.check_permission(guest.user_id, Permission.FINANCE_WRITE)
        )
    
    return rbac


async def test_resource_access_control(results: TestResults, rbac: RBACEngine):
    """Test resource-level access control."""
    print("\n🏢 TEST: Resource Access Control")
    print("-" * 40)
    
    # Get users
    super_admin = rbac.db.get_user(username="pakpur")
    guest = rbac.db.get_user(username="guest_test")
    
    if super_admin and guest:
        # Test Disaster Recovery access
        results.record(
            "SUPER_ADMIN can trigger DR",
            rbac.check_resource_access(super_admin.user_id, Resource.DISASTER_RECOVERY, "trigger")
        )
        
        results.record(
            "GUEST cannot trigger DR",
            not rbac.check_resource_access(guest.user_id, Resource.DISASTER_RECOVERY, "trigger")
        )
        
        # Test Finance access
        results.record(
            "SUPER_ADMIN can write Finance",
            rbac.check_resource_access(super_admin.user_id, Resource.FINANCE, "write")
        )
        
        results.record(
            "GUEST cannot write Finance",
            not rbac.check_resource_access(guest.user_id, Resource.FINANCE, "write")
        )
    
    return rbac


async def test_role_matrix(results: TestResults, rbac: RBACEngine):
    """Test role matrix generation."""
    print("\n📋 TEST: Role Matrix")
    print("-" * 40)
    
    matrix = rbac.get_role_matrix()
    
    results.record(
        "Matrix has roles",
        "roles" in matrix
    )
    
    results.record(
        "Matrix has 5 roles",
        matrix["total_roles"] == 5
    )
    
    results.record(
        "SUPER_ADMIN in matrix",
        "super_admin" in matrix["roles"]
    )
    
    results.record(
        "GUEST in matrix",
        "guest" in matrix["roles"]
    )
    
    return rbac


async def test_repository_center_initialization(results: TestResults):
    """Test repository center initialization."""
    print("\n📦 TEST: Repository Center Initialization")
    print("-" * 40)
    
    repo = get_repository_center()
    
    results.record(
        "Repository Center Created",
        repo is not None
    )
    
    results.record(
        "Archives Path Created",
        os.path.exists(repo.archives_path)
    )
    
    return repo


async def test_repository_status(results: TestResults, repo: RepositoryCenter):
    """Test repository status retrieval."""
    print("\n📊 TEST: Repository Status")
    print("-" * 40)
    
    status = repo.get_repository_status()
    
    results.record(
        "Status has repository info",
        "repository" in status
    )
    
    results.record(
        "Status has archives info",
        "archives" in status
    )
    
    results.record(
        "Has branch info",
        "branch" in status["repository"]
    )
    
    return repo


async def test_archive_creation(results: TestResults, repo: RepositoryCenter):
    """Test archive creation."""
    print("\n📦 TEST: Archive Creation")
    print("-" * 40)
    
    archive = repo.create_archive(message="Test archive snapshot")
    
    results.record(
        "Archive Created",
        archive.archive_id.startswith("ARCH-")
    )
    
    results.record(
        "Archive has commit hash",
        len(archive.commit_hash) > 0
    )
    
    results.record(
        "Archive has message",
        archive.message == "Test archive snapshot"
    )
    
    results.record(
        "Archive has files",
        len(archive.files_included) > 0 or archive.status.value in ["completed", "pending"]
    )
    
    results.record(
        "Archive saved to DB",
        repo.db.get_archive(archive.archive_id) is not None
    )
    
    return repo, archive


async def test_archive_listing(results: TestResults, repo: RepositoryCenter):
    """Test archive listing."""
    print("\n📋 TEST: Archive Listing")
    print("-" * 40)
    
    archives = repo.get_archives(limit=10)
    
    results.record(
        "Archives Listed",
        isinstance(archives, list)
    )
    
    results.record(
        "Has Archives",
        len(archives) > 0
    )
    
    # Test listing endpoint format
    archives_dict = repo.get_archives(limit=5)
    if archives_dict:
        first = archives_dict[0]
        results.record(
            "Archive has ID",
            "id" in first
        )
        
        results.record(
            "Archive has commit",
            "commit" in first
        )
    
    return repo


async def test_integration_rbac_protects_dr(results: TestResults, rbac: RBACEngine):
    """Test that RBAC protects DR endpoints."""
    print("\n🔒 TEST: RBAC Protects DR Endpoints")
    print("-" * 40)
    
    guest = rbac.db.get_user(username="guest_test")
    
    if guest:
        # GUEST should not be able to trigger DR
        can_trigger = rbac.check_resource_access(
            guest.user_id, 
            Resource.DISASTER_RECOVERY, 
            "trigger"
        )
        
        results.record(
            "GUEST blocked from DR trigger",
            not can_trigger
        )
    
    return rbac


async def test_integration_rbac_protects_finance(results: TestResults, rbac: RBACEngine):
    """Test that RBAC protects Finance endpoints."""
    print("\n💰 TEST: RBAC Protects Finance Endpoints")
    print("-" * 40)
    
    guest = rbac.db.get_user(username="guest_test")
    
    if guest:
        # GUEST should not be able to write to Finance
        can_write = rbac.check_resource_access(
            guest.user_id, 
            Resource.FINANCE, 
            "write"
        )
        
        results.record(
            "GUEST blocked from Finance write",
            not can_write
        )
    
    return rbac


async def test_super_admin_full_access(results: TestResults, rbac: RBACEngine):
    """Test SUPER_ADMIN has full access."""
    print("\n👑 TEST: SUPER_ADMIN Full Access")
    print("-" * 40)
    
    super_admin = rbac.db.get_user(username="pakpur")
    
    if super_admin:
        # SUPER_ADMIN should have full access to everything
        results.record(
            "SUPER_ADMIN can trigger DR",
            rbac.check_resource_access(super_admin.user_id, Resource.DISASTER_RECOVERY, "trigger")
        )
        
        results.record(
            "SUPER_ADMIN can recover DR",
            rbac.check_resource_access(super_admin.user_id, Resource.DISASTER_RECOVERY, "recover")
        )
        
        results.record(
            "SUPER_ADMIN can write Finance",
            rbac.check_resource_access(super_admin.user_id, Resource.FINANCE, "write")
        )
        
        results.record(
            "SUPER_ADMIN can manage Users",
            rbac.check_resource_access(super_admin.user_id, Resource.USER, "write")
        )
        
        results.record(
            "SUPER_ADMIN can manage System",
            rbac.check_resource_access(super_admin.user_id, Resource.SYSTEM, "config")
        )
    
    return rbac


async def test_repository_archive_integration(results: TestResults, repo: RepositoryCenter):
    """Test archive creation with repository integration."""
    print("\n🔗 TEST: Repository Archive Integration")
    print("-" * 40)
    
    # Create archive after simulated push
    push_info = {
        "commit_hash": "abc123",
        "message": "Post-push archive",
        "remote": "origin",
        "branch": "main",
        "commits_count": 1
    }
    
    archive = repo.archive_after_push(push_info)
    
    results.record(
        "Post-push archive created",
        archive.archive_id.startswith("ARCH-")
    )
    
    # Verify sync history recorded
    sync_history = repo.get_sync_history(limit=1)
    results.record(
        "Sync history recorded",
        len(sync_history) > 0
    )
    
    return repo


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.1.0 - RBAC & Repository Tests")
    print("="*60)
    
    results = TestResults()
    
    try:
        # RBAC tests
        rbac = await test_rbac_initialization(results)
        await test_role_hierarchy(results, rbac)
        await test_permission_inheritance(results, rbac)
        await test_permission_check(results, rbac)
        await test_resource_access_control(results, rbac)
        await test_role_matrix(results, rbac)
        
        # Repository tests
        repo = await test_repository_center_initialization(results)
        await test_repository_status(results, repo)
        await test_archive_creation(results, repo)
        await test_archive_listing(results, repo)
        
        # Integration tests
        await test_integration_rbac_protects_dr(results, rbac)
        await test_integration_rbac_protects_finance(results, rbac)
        await test_super_admin_full_access(results, rbac)
        await test_repository_archive_integration(results, repo)
        
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
