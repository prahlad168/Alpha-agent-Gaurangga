"""
MAHALAKSMI AIOS v1.0.3 - Security & Product Integration Tests
End-to-end test: Purchase → License Generation → Access Validation
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security_ext import (
    CryptoManager, JWTManager, LicenseKeyGenerator
)
from app.business.product import (
    get_product_center, ProductType, PricingModel, Product
)
from app.business.revenue import get_revenue_manager


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
    
    def summary(self):
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nErrors:")
            for e in self.errors:
                print(f"  - {e}")
        print("="*60)
        return self.failed == 0


def test_crypto_encryption(results: TestResults):
    """Test Fernet encryption."""
    print("\n🔐 TEST: Fernet Encryption")
    print("-" * 40)
    
    crypto = CryptoManager()
    
    # Test encryption/decryption
    original = "Secret license data"
    encrypted = crypto.encrypt(original)
    
    results.record(
        "Encryption Returns String",
        isinstance(encrypted, str),
        f"Got {type(encrypted)}"
    )
    
    decrypted = crypto.decrypt(encrypted)
    results.record(
        "Decryption Matches Original",
        decrypted == original,
        f"{decrypted} != {original}"
    )
    
    # Test dict encryption
    data = {"key": "value", "number": 123}
    encrypted_dict = crypto.encrypt_dict(data)
    decrypted_dict = crypto.decrypt_dict(encrypted_dict)
    
    results.record(
        "Dict Encryption Works",
        decrypted_dict == data,
        f"{decrypted_dict} != {data}"
    )
    
    # Test password hashing
    password = "test_password_123"
    hashed = CryptoManager.hash_password(password)
    results.record(
        "Password Hash Generated",
        "$" in hashed,
        "No salt separator in hash"
    )
    
    verified = CryptoManager.verify_password(password, hashed)
    results.record(
        "Password Verification",
        verified,
        "Password verification failed"
    )
    
    # Test secure token generation
    token1 = CryptoManager.generate_token()
    token2 = CryptoManager.generate_token()
    
    results.record(
        "Token Generation",
        token1 != token2,
        "Tokens should be unique"
    )
    
    results.record(
        "Token Length",
        len(token1) >= 32,
        f"Token too short: {len(token1)}"
    )
    
    return crypto


def test_jwt_manager(results: TestResults):
    """Test JWT token management."""
    print("\n🎫 TEST: JWT Token Manager")
    print("-" * 40)
    
    jwt = JWTManager()
    
    # Create token
    payload = {"user_id": "test123", "role": "admin"}
    token = jwt.create_token(payload)
    
    results.record(
        "Token Created",
        isinstance(token, str) and len(token) > 0,
        "Token not created"
    )
    
    # Verify token
    verified = jwt.verify_token(token)
    results.record(
        "Token Verified",
        verified is not None,
        "Token verification failed"
    )
    
    results.record(
        "Payload Preserved",
        verified.get("user_id") == "test123",
        f"Wrong user_id: {verified}"
    )
    
    # Decode without verification
    decoded = jwt.decode_optional(token)
    results.record(
        "Optional Decode Works",
        decoded is not None,
        "Optional decode failed"
    )
    
    return jwt


def test_license_generator(results: TestResults):
    """Test license key generation."""
    print("\n🔑 TEST: License Key Generation")
    print("-" * 40)
    
    license_gen = LicenseKeyGenerator()
    
    # Generate key
    result = license_gen.generate_key(
        product_id="TEST-PRODUCT-001",
        customer_id="CUST-001",
        expires_days=30
    )
    
    results.record(
        "License Key Generated",
        "license_key" in result,
        "No license key in result"
    )
    
    results.record(
        "License Key Format",
        result["license_key"].startswith("MLK-"),
        f"Wrong format: {result['license_key']}"
    )
    
    results.record(
        "Encrypted Data Created",
        "license_data" in result,
        "No encrypted data"
    )
    
    results.record(
        "Expiration Set",
        "expires_at" in result,
        "No expiration date"
    )
    
    # Validate key
    validation = license_gen.validate_key(
        result["license_key"],
        result["license_data"]
    )
    
    results.record(
        "License Validation",
        validation["valid"],
        f"Validation failed: {validation}"
    )
    
    return license_gen


async def test_product_center(results: TestResults):
    """Test product center."""
    print("\n🏪 TEST: Product Center")
    print("-" * 40)
    
    product_center = get_product_center()
    
    # List products
    products = product_center.list_products()
    results.record(
        "Products Listed",
        len(products) > 0,
        f"No products: {len(products)}"
    )
    
    # Get first product
    if products:
        first_product = products[0]
        product_id = first_product["product_id"]
        results.record(
            "Product Has ID",
            "product_id" in first_product,
            "Missing product_id"
        )
        
        # Get product details
        product = product_center.get_product(product_id)
        results.record(
            "Product Details Retrieved",
            product is not None,
            "Product not found"
        )
    
    # Create custom product
    new_product = product_center.create_product(
        name="Test Software",
        description="A test product",
        product_type=ProductType.SOFTWARE,
        pricing_model=PricingModel.ONE_TIME,
        price=100000
    )
    
    results.record(
        "Product Created",
        new_product.product_id is not None,
        "Product ID missing"
    )
    
    return product_center


async def test_purchase_flow(results: TestResults):
    """Test complete purchase → license flow."""
    print("\n💳 TEST: Purchase → License Flow")
    print("-" * 40)
    
    product_center = get_product_center()
    revenue = get_revenue_manager()
    
    # Get initial revenue count
    initial_summary = revenue.get_summary()
    initial_txn_count = initial_summary["total_transactions"]
    
    # First create a test product
    test_product = product_center.create_product(
        name="Test Software Product",
        description="A test product for purchase flow",
        product_type=ProductType.SOFTWARE,
        pricing_model=PricingModel.ONE_TIME,
        price=100000
    )
    
    # Purchase the product we just created
    purchase_result = await product_center.purchase_and_activate(
        product_id=test_product.product_id,
        customer_id="CUST-TEST-001",
        customer_name="Test Customer",
        customer_email="test@example.com",
        payment_amount=100000
    )
    
    results.record(
        "Purchase Successful",
        purchase_result["success"],
        f"Purchase failed: {purchase_result}"
    )
    
    results.record(
        "License Key Generated",
        "license_key" in purchase_result,
        "No license key"
    )
    
    results.record(
        "License Key Format Valid",
        purchase_result["license_key"].startswith("MLK-"),
        f"Wrong format: {purchase_result['license_key']}"
    )
    
    results.record(
        "Revenue Recorded",
        purchase_result.get("revenue_transaction_id") is not None,
        "No revenue transaction"
    )
    
    # Validate the license
    validation = product_center.validate_license(purchase_result["license_key"])
    
    results.record(
        "License Valid",
        validation["valid"],
        f"License invalid: {validation}"
    )
    
    results.record(
        "Activations Tracked",
        "activations" in validation,
        "No activation count"
    )
    
    # Verify revenue increased
    new_summary = revenue.get_summary()
    results.record(
        "Revenue Increased",
        new_summary["total_transactions"] > initial_txn_count,
        "Revenue not recorded"
    )
    
    return purchase_result


async def test_customer_portal(results: TestResults):
    """Test customer portal."""
    print("\n👤 TEST: Customer Portal")
    print("-" * 40)
    
    product_center = get_product_center()
    
    # Get portal for test customer
    portal = product_center.get_customer_portal("CUST-TEST-001")
    
    results.record(
        "Portal Returns Data",
        "customer_id" in portal,
        "No customer_id"
    )
    
    results.record(
        "Has Licenses List",
        "licenses" in portal,
        "No licenses list"
    )
    
    results.record(
        "Has Total Count",
        "total_licenses" in portal,
        "No total count"
    )
    
    return portal


def test_product_stats(results: TestResults):
    """Test product statistics."""
    print("\n📊 TEST: Product Statistics")
    print("-" * 40)
    
    product_center = get_product_center()
    stats = product_center.get_catalog_stats()
    
    results.record(
        "Stats Returned",
        "total_products" in stats,
        "Missing stats"
    )
    
    results.record(
        "Products Counted",
        stats["total_products"] > 0,
        f"No products: {stats['total_products']}"
    )
    
    results.record(
        "Type Breakdown",
        "products_by_type" in stats,
        "No type breakdown"
    )
    
    return stats


async def run_all_tests():
    """Run all security and product tests."""
    print("\n" + "="*60)
    print("🤖 MAHALAKSMI AIOS v1.0.3 - Security & Product Tests")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    results = TestResults()
    
    try:
        # Security tests
        test_crypto_encryption(results)
        test_jwt_manager(results)
        test_license_generator(results)
        
        # Product tests
        await test_product_center(results)
        await test_purchase_flow(results)
        await test_customer_portal(results)
        test_product_stats(results)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        results.failed += 1
    
    success = results.summary()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED - Security & Product Center Ready!")
    else:
        print("⚠️ SOME TESTS FAILED - Review above")
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
