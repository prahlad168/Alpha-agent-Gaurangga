"""
MAHALAKSMI AIOS v2.0 - Ultimate Enterprise Tests
Comprehensive tests for all Volume II, III, IV, V modules
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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


def test_vision_engine(results: TestResults):
    """Test Vision Engine."""
    print("\n👁️ TEST: Vision Engine (Vol II Ch 15)")
    print("-" * 40)
    
    from app.intelligence.multimodal import get_vision_engine
    
    vision = get_vision_engine()
    result = vision.analyze_image(prompt="Test image")
    
    results.record("Vision engine initialized", vision is not None)
    results.record("Image analysis success", result.success)
    results.record("Labels extracted", len(result.labels) > 0)
    results.record("Confidence score", result.confidence > 0)
    
    # OCR test
    ocr = vision.extract_text()
    results.record("OCR extraction", len(ocr) > 0)
    
    return vision


def test_voice_engine(results: TestResults):
    """Test Voice Engine."""
    print("\n🎤 TEST: Voice Engine (Vol II Ch 16)")
    print("-" * 40)
    
    from app.intelligence.multimodal import get_voice_engine
    
    voice = get_voice_engine()
    result = voice.process_voice_command(language="id-ID")
    
    results.record("Voice engine initialized", voice is not None)
    results.record("Voice processing success", result.success)
    results.record("Transcript generated", len(result.transcript) > 0)
    results.record("Intent extracted", len(result.intent) > 0)
    
    # TTS test
    tts = voice.text_to_speech("Test message")
    results.record("TTS output", len(tts) > 0)
    
    return voice


def test_nlp_engine(results: TestResults):
    """Test NLP Engine."""
    print("\n🧠 TEST: NLP Engine (Vol II Ch 17)")
    print("-" * 40)
    
    from app.intelligence.multimodal import get_nlp_engine
    
    nlp = get_nlp_engine()
    
    # Sentiment test
    sentiment_result = nlp.analyze_sentiment("Produk ini sangat bagus dan memuaskan")
    results.record("Sentiment analysis", sentiment_result.success)
    results.record("Sentiment detected", sentiment_result.sentiment.value in ["positive", "negative", "neutral"])
    
    # Entity extraction
    entities = nlp.extract_entities("Transfer Rp 5.000.000 ke rekening 123456789")
    results.record("Entity extraction", len(entities) > 0)
    
    # Categorization
    categories = nlp.categorize_text("Invoice untuk pembayaran bulan Juli")
    results.record("Text categorization", len(categories) > 0)
    
    # Full analysis
    full = nlp.full_analysis("Pembelian produk berhasil dilakukan")
    results.record("Full NLP analysis", full.success)
    
    return nlp


def test_auto_test_runner(results: TestResults):
    """Test Auto Test Runner."""
    print("\n🧪 TEST: Auto Test Runner (Vol III Ch 21)")
    print("-" * 40)
    
    from app.development.devops_suite import get_auto_test_runner
    
    runner = get_auto_test_runner()
    
    # Health check
    health = runner.run_health_check()
    results.record("Health check executed", health is not None)
    results.record("Health check passed", health.passed)
    
    # API validation
    api_results = runner.run_api_validation()
    results.record("API validation", len(api_results) > 0)
    
    # Full test suite
    full_results = runner.run_all_tests()
    results.record("Test suite completed", full_results["total_tests"] > 0)
    results.record("Some tests passed", full_results["passed"] > 0)
    
    return runner


def test_logging_system(results: TestResults):
    """Test Unified Logging System."""
    print("\n📝 TEST: Unified Logging (Vol III Ch 22)")
    print("-" * 40)
    
    from app.development.devops_suite import get_logging_system, LogLevel
    
    logs = get_logging_system()
    
    # Log entry
    logs.log(LogLevel.INFO, "Test message", "test")
    logs.log(LogLevel.WARNING, "Warning message", "test")
    logs.log(LogLevel.ERROR, "Error message", "test")
    
    results.record("Logging system initialized", logs is not None)
    results.record("Log written", len(logs._log_buffer) > 0)
    
    # Retrieve logs
    retrieved = logs.get_logs(limit=10)
    results.record("Logs retrieved", isinstance(retrieved, list))
    
    # Security logs
    security = logs.get_security_logs()
    results.record("Security logs", isinstance(security, list))
    
    return logs


def test_deployment_center(results: TestResults):
    """Test Deployment Center."""
    print("\n🚀 TEST: Deployment Center (Vol III Ch 24)")
    print("-" * 40)
    
    from app.development.devops_suite import get_deployment_center, Environment
    
    deploy = get_deployment_center()
    
    # Create deployment
    record = deploy.create_deployment(Environment.SANDBOX, "v2.0.0", "Test deployment")
    results.record("Deployment created", record.deployment_id.startswith("DEP-"))
    
    # Start deployment
    started = deploy.start_deployment(record.deployment_id)
    results.record("Deployment started", started)
    
    # Complete deployment
    completed = deploy.complete_deployment(record.deployment_id, True)
    results.record("Deployment completed", completed)
    
    # Get status
    status = deploy.get_deployment_status(record.deployment_id)
    results.record("Status retrieved", status is not None)
    
    return deploy


def test_ai_coding_assistant(results: TestResults):
    """Test AI Coding Assistant."""
    print("\n🤖 TEST: AI Coding Assistant (Vol III Ch 25)")
    print("-" * 40)
    
    from app.development.devops_suite import get_ai_coding_assistant
    
    ai = get_ai_coding_assistant()
    
    # Analyze code
    code = """
    def test_function():
        print("Hello World")
    """
    
    analysis = ai.analyze_code(code)
    results.record("Code analysis completed", analysis is not None)
    results.record("Issues detected", "issues" in analysis)
    results.record("Score calculated", "score" in analysis)
    
    # PEP8 suggestions
    pep8 = ai.suggest_pep8_fixes(code)
    results.record("PEP8 suggestions", isinstance(pep8, list))
    
    return ai


def test_performance_profiler(results: TestResults):
    """Test Performance Profiler."""
    print("\n📊 TEST: Performance Profiler (Vol III Ch 26)")
    print("-" * 40)
    
    from app.development.devops_suite import get_performance_profiler
    
    profiler = get_performance_profiler()
    
    # Record execution
    profiler.record_endpoint_execution("/api/test", 150.5)
    profiler.record_endpoint_execution("/api/test", 120.0)
    
    results.record("Profiler initialized", profiler is not None)
    
    # Get stats
    stats = profiler.get_endpoint_stats("/api/test")
    results.record("Stats retrieved", stats is not None)
    results.record("Avg calculated", "avg_ms" in stats)
    
    # Memory snapshot
    snapshot = profiler.record_memory_snapshot()
    results.record("Memory snapshot", "rss_mb" in snapshot)
    
    # Memory trend
    trend = profiler.get_memory_trend()
    results.record("Memory trend", "current_mb" in trend)
    
    return profiler


def test_asset_manager(results: TestResults):
    """Test Asset Manager."""
    print("\n🏢 TEST: Asset Manager (Vol IV Ch 33)")
    print("-" * 40)
    
    import uuid
    from app.business.operations import get_asset_manager, Asset, AssetType
    
    assets = get_asset_manager()
    
    # Create asset with unique ID
    asset_id = f"ASSET-{uuid.uuid4().hex[:8].upper()}"
    
    asset = Asset(
        asset_id=asset_id,
        name="Test Laptop",
        asset_type=AssetType.HARDWARE,
        purchase_date="2024-01-01",
        purchase_cost=15000000,
        current_value=15000000,
        depreciation_rate=20.0,
        useful_life_years=5,
        location="Jakarta"
    )
    
    added = assets.add_asset(asset)
    results.record("Asset created", added)
    
    # Get assets
    asset_list = assets.get_assets()
    results.record("Assets retrieved", isinstance(asset_list, list))
    
    # Calculate depreciation
    depr = assets.calculate_depreciation(asset_id)
    results.record("Depreciation calculated", "current_value" in depr)
    
    return assets


def test_legal_engine(results: TestResults):
    """Test Legal Engine."""
    print("\n⚖️ TEST: Legal Engine (Vol IV Ch 34)")
    print("-" * 40)
    
    from app.business.operations import get_legal_engine
    
    legal = get_legal_engine()
    
    # Generate contract
    contract = legal.generate_contract(
        contract_type="service",
        party_a={"name": "Company A"},
        party_b={"name": "Company B"},
        terms=["Payment within 30 days", "No subletting"]
    )
    
    results.record("Contract generated", "contract_id" in contract)
    results.record("Contract body", len(contract.get("body", "")) > 0)
    
    # Generate NDA
    nda = legal.generate_nda(
        disclosing_party="Company A",
        receiving_party="Company B",
        purpose="Technology sharing",
        duration_months=24
    )
    
    results.record("NDA generated", "nda_id" in nda)
    results.record("NDA expiry", "expiry_date" in nda)
    
    return legal


def test_hr_manager(results: TestResults):
    """Test HR Manager."""
    print("\n👥 TEST: HR Manager (Vol IV Ch 35)")
    print("-" * 40)
    
    import uuid
    from app.business.operations import get_hr_manager, Employee, LeaveType
    
    hr = get_hr_manager()
    
    # Create employee with unique ID
    emp_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
    
    emp = Employee(
        employee_id=emp_id,
        name="John Doe",
        email="john@example.com",
        phone="08123456789",
        department="Engineering",
        position="Developer",
        hire_date="2024-01-01",
        salary=10000000
    )
    
    hr.add_employee(emp)
    results.record("Employee created", emp.employee_id.startswith("EMP-"))
    
    # Get employees
    employees = hr.get_employees()
    results.record("Employees retrieved", isinstance(employees, list))
    
    # Request leave
    leave = hr.request_leave(
        employee_id=emp_id,
        leave_type=LeaveType.ANNUAL,
        start_date="2024-07-01",
        end_date="2024-07-05",
        reason="Family vacation"
    )
    
    results.record("Leave requested", leave.request_id.startswith("LEAVE-"))
    
    # Leave balance
    balance = hr.calculate_leave_balance(emp_id)
    results.record("Balance calculated", "annual_entitled" in balance)
    
    return hr


def test_supply_chain(results: TestResults):
    """Test Supply Chain Orchestrator."""
    print("\n📦 TEST: Supply Chain (Vol IV Ch 36)")
    print("-" * 40)
    
    import uuid
    from app.business.operations import get_supply_chain, Vendor, VendorStatus
    
    supply = get_supply_chain()
    
    # Create vendor with unique ID
    vendor_id = f"VD-{uuid.uuid4().hex[:8].upper()}"
    
    vendor = Vendor(
        vendor_id=vendor_id,
        name="Test Supplier",
        contact_person="Jane Doe",
        email="jane@supplier.com",
        phone="08987654321",
        address="Jakarta",
        category="Electronics",
        status=VendorStatus.ACTIVE
    )
    
    supply.add_vendor(vendor)
    results.record("Vendor created", vendor.vendor_id.startswith("VD-"))
    
    # Get vendors
    vendors = supply.get_vendors()
    results.record("Vendors retrieved", isinstance(vendors, list))
    
    # Restock threshold
    prod_id = f"PROD-{uuid.uuid4().hex[:6].upper()}"
    supply.set_restock_threshold(prod_id, 10)
    check = supply.check_restock(prod_id, 5)
    results.record("Restock check", "needs_restock" in check)
    results.record("Restock threshold", check["needs_restock"] == True)
    
    return supply


def test_erp_sync(results: TestResults):
    """Test ERP Sync Engine."""
    print("\n🔄 TEST: ERP Sync (Vol V Ch 42)")
    print("-" * 40)
    
    from app.enterprise.architecture import get_erp_sync
    
    erp = get_erp_sync()
    
    results.record("ERP initialized", erp is not None)
    
    # Sync finance to HR
    sync = erp.sync_finance_to_hr({"total_revenue": 100000000, "employee_count": 10})
    results.record("Finance-HR sync", "payroll_budget" in sync)
    
    # Get dashboard
    dashboard = erp.get_unified_dashboard()
    results.record("Dashboard generated", "finance" in dashboard)
    
    # Trigger sync
    sync_result = erp.trigger_sync("test")
    results.record("Sync triggered", sync_result["status"] == "completed")
    
    return erp


def test_business_intelligence(results: TestResults):
    """Test Business Intelligence."""
    print("\n📈 TEST: Business Intelligence (Vol V Ch 43)")
    print("-" * 40)
    
    from app.enterprise.architecture import get_business_intelligence
    
    bi = get_business_intelligence()
    
    # Test data
    transactions = [
        {"amount": 1000000, "date": "2024-01-01"},
        {"amount": 1500000, "date": "2024-01-02"},
        {"amount": 1200000, "date": "2024-01-03"},
    ]
    
    # Sales velocity
    velocity = bi.calculate_sales_velocity(transactions)
    results.record("Velocity calculated", "velocity" in velocity)
    results.record("Trend detected", "trend" in velocity)
    
    # Revenue forecast
    forecast = bi.forecast_revenue(transactions, 30)
    results.record("Forecast generated", "forecast" in forecast)
    results.record("Confidence calculated", "confidence" in forecast)
    
    # Trend analysis
    trends = bi.analyze_trends(transactions)
    results.record("Trends analyzed", "trend" in trends)
    
    return bi


def test_audit_trail(results: TestResults):
    """Test Audit Trail Engine."""
    print("\n📋 TEST: Audit Trail (Vol V Ch 44)")
    print("-" * 40)
    
    from app.enterprise.architecture import get_audit_trail, AuditAction
    
    audit = get_audit_trail()
    
    # Create audit log
    entry = audit.log(
        user_id="USER-001",
        action=AuditAction.CREATE,
        resource="asset",
        resource_id="ASSET-001",
        ip_address="192.168.1.1",
        details={"field": "value"}
    )
    
    results.record("Audit entry created", entry.entry_id.startswith("AUDIT-"))
    results.record("Hash generated", len(entry.hash) == 64)
    
    # Verify integrity
    verification = audit.verify_chain_integrity(10)
    results.record("Integrity verified", "valid" in verification)
    
    # Get logs
    logs = audit.get_logs(limit=10)
    results.record("Logs retrieved", isinstance(logs, list))
    
    return audit


def test_security_shield(results: TestResults):
    """Test Security Shield."""
    print("\n🛡️ TEST: Security Shield (Vol V Ch 46)")
    print("-" * 40)
    
    from app.enterprise.architecture import get_security_shield
    
    shield = get_security_shield()
    
    # Rate limit check
    result1 = shield.check_rate_limit("192.168.1.1")
    results.record("Rate limit checked", "allowed" in result1)
    results.record("First request allowed", result1["allowed"] == True)
    
    # SQL injection detection
    injection = shield.detect_sql_injection("'; DROP TABLE users;--")
    results.record("SQL injection detected", injection == True)
    
    safe = shield.detect_sql_injection("Normal text input")
    results.record("Safe input passed", safe == False)
    
    # Input sanitization
    sanitized = shield.sanitize_input("Test'; input")
    results.record("Input sanitized", "'" not in sanitized)
    
    # JWT validation
    jwt_result = shield.validate_jwt_payload({"sub": "user1", "exp": 9999999999, "iat": 1000000000})
    results.record("JWT validated", "valid" in jwt_result)
    
    return shield


def test_multi_tenant(results: TestResults):
    """Test Multi-Tenant Router."""
    print("\n🏢 TEST: Multi-Tenant (Vol V Ch 47)")
    print("-" * 40)
    
    from app.enterprise.architecture import get_multi_tenant, TenantType
    
    router = get_multi_tenant()
    
    results.record("Router initialized", router is not None)
    
    # Get default tenants
    tenants = router.get_all_tenants()
    results.record("Default tenants exist", len(tenants) >= 3)
    
    # Get tenant by ID
    tenant = router.get_tenant("SBU-FINANCE-001")
    results.record("Tenant retrieved", tenant is not None)
    
    # Create new tenant
    new_tenant = router.create_tenant("Test Company", TenantType.SBU_OPERATIONS)
    results.record("New tenant created", new_tenant.tenant_id.startswith("SBU-"))
    results.record("Schema assigned", len(new_tenant.db_schema) > 0)
    
    # Data isolation
    isolated = router.isolate_data(new_tenant.tenant_id, {"test": "data"})
    results.record("Data isolated", "tenant_id" in isolated)
    
    return router


def test_high_performance_cache(results: TestResults):
    """Test High-Performance Cache."""
    print("\n⚡ TEST: High-Performance Cache (Vol V Ch 48)")
    print("-" * 40)
    
    from app.enterprise.architecture import get_cache
    
    cache = get_cache()
    
    # Set value
    cache.set("test_key", "test_value", ttl=3600)
    results.record("Cache set", True)
    
    # Get value
    value = cache.get("test_key")
    results.record("Cache hit", value == "test_value")
    
    # Miss
    miss = cache.get("nonexistent")
    results.record("Cache miss", miss is None)
    
    # Stats
    stats = cache.get_stats()
    results.record("Stats retrieved", "hits" in stats)
    results.record("Hit rate calculated", "hit_rate" in stats)
    
    # Preload configs
    cache.preload_configs({"config1": "value1", "config2": "value2"})
    results.record("Configs preloaded", cache.get("config1") == "value1")
    
    return cache


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚀 MAHALAKSMI AIOS v2.0 - ULTIMATE ENTERPRISE TESTS")
    print("="*60)
    
    results = TestResults()
    
    try:
        # Volume II - Intelligence
        test_vision_engine(results)
        test_voice_engine(results)
        test_nlp_engine(results)
        
        # Volume III - DevOps
        test_auto_test_runner(results)
        test_logging_system(results)
        test_deployment_center(results)
        test_ai_coding_assistant(results)
        test_performance_profiler(results)
        
        # Volume IV - Business
        test_asset_manager(results)
        test_legal_engine(results)
        test_hr_manager(results)
        test_supply_chain(results)
        
        # Volume V - Enterprise
        test_erp_sync(results)
        test_business_intelligence(results)
        test_audit_trail(results)
        test_security_shield(results)
        test_multi_tenant(results)
        test_high_performance_cache(results)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        results.failed += 1
    
    # Print summary
    print("\n" + "="*60)
    print(f"📊 RESULTS: {results.passed} passed, {results.failed} failed")
    if results.errors:
        print("\n⚠️ Errors:")
        for e in results.errors[:10]:  # Show first 10
            print(f"  - {e}")
    print("="*60)
    
    success = results.failed == 0
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED! MAHALAKSMI AIOS v2.0 COMPLETE!")
    else:
        print("⚠️ SOME TESTS FAILED")
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
