"""
MAHALAKSMI AIOS v1.1.2 - Multilingual Interface System Tests
Tests localization switching, fallback, and API endpoints
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.i18n import (
    get_i18n_engine,
    I18nEngine,
    detect_locale,
    localized_response,
    localized_error,
    SUPPORTED_LOCALES,
    DEFAULT_LOCALE
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


def test_i18n_initialization(results: TestResults):
    """Test I18n engine initialization."""
    print("\n🌐 TEST: I18n Engine Initialization")
    print("-" * 40)
    
    i18n = get_i18n_engine()
    
    results.record(
        "I18n Engine Created",
        i18n is not None
    )
    
    results.record(
        "Has Indonesian Translations",
        "id" in i18n.translations
    )
    
    results.record(
        "Has English Translations",
        "en" in i18n.translations
    )
    
    results.record(
        "Default Locale Set",
        i18n.default_locale == "en"
    )
    
    return i18n


def test_indonesian_translations(results: TestResults, i18n: I18nEngine):
    """Test Indonesian translations."""
    print("\n🇮🇩 TEST: Indonesian Translations")
    print("-" * 40)
    
    # Test payment messages
    results.record(
        "payment.success (ID)",
        i18n.get_translation("payment.success", "id") == "Pembayaran berhasil"
    )
    
    results.record(
        "payment.pending (ID)",
        i18n.get_translation("payment.pending", "id") == "Pembayaran menunggu"
    )
    
    results.record(
        "payment.failed (ID)",
        i18n.get_translation("payment.failed", "id") == "Pembayaran gagal"
    )
    
    # Test auth messages
    results.record(
        "auth.login.success (ID)",
        i18n.get_translation("auth.login.success", "id") == "Login berhasil"
    )
    
    results.record(
        "auth.access.denied (ID)",
        i18n.get_translation("auth.access.denied", "id") == "Akses ditolak"
    )
    
    # Test general messages
    results.record(
        "success (ID)",
        i18n.get_translation("success", "id") == "Berhasil"
    )
    
    results.record(
        "error (ID)",
        i18n.get_translation("error", "id") == "Kesalahan"
    )
    
    return i18n


def test_english_translations(results: TestResults, i18n: I18nEngine):
    """Test English translations."""
    print("\n🇬🇧 TEST: English Translations")
    print("-" * 40)
    
    # Test payment messages
    results.record(
        "payment.success (EN)",
        i18n.get_translation("payment.success", "en") == "Payment successful"
    )
    
    results.record(
        "payment.pending (EN)",
        i18n.get_translation("payment.pending", "en") == "Payment pending"
    )
    
    results.record(
        "payment.failed (EN)",
        i18n.get_translation("payment.failed", "en") == "Payment failed"
    )
    
    # Test auth messages
    results.record(
        "auth.login.success (EN)",
        i18n.get_translation("auth.login.success", "en") == "Login successful"
    )
    
    results.record(
        "auth.access.denied (EN)",
        i18n.get_translation("auth.access.denied", "en") == "Access denied"
    )
    
    return i18n


def test_locale_switching(results: TestResults, i18n: I18nEngine):
    """Test switching between locales."""
    print("\n🔄 TEST: Locale Switching")
    print("-" * 40)
    
    # Same key, different locales
    id_translation = i18n.get_translation("payment.success", "id")
    en_translation = i18n.get_translation("payment.success", "en")
    
    results.record(
        "Different locales = Different translations",
        id_translation != en_translation
    )
    
    results.record(
        "ID has Indonesian text",
        "berhasil" in id_translation
    )
    
    results.record(
        "EN has English text",
        "successful" in en_translation
    )
    
    return i18n


def test_fallback_mechanism(results: TestResults, i18n: I18nEngine):
    """Test fallback to default locale."""
    print("\n🔁 TEST: Fallback Mechanism")
    print("-" * 40)
    
    # Non-existent key should return key itself
    fallback = i18n.get_translation("nonexistent.key", "id")
    results.record(
        "Non-existent key returns key",
        fallback == "nonexistent.key"
    )
    
    # Invalid locale should fallback
    fallback = i18n.get_translation("payment.success", "invalid")
    results.record(
        "Invalid locale fallback to EN",
        fallback == "Payment successful"
    )
    
    return i18n


def test_locale_detection(results: TestResults):
    """Test locale detection from parameters."""
    print("\n🔍 TEST: Locale Detection")
    print("-" * 40)
    
    # Test with lang param
    locale = detect_locale(lang_param="id")
    results.record(
        "lang=id detected",
        locale == "id"
    )
    
    locale = detect_locale(lang_param="en")
    results.record(
        "lang=en detected",
        locale == "en"
    )
    
    # Test with Accept-Language header
    locale = detect_locale(accept_language="id-ID,id;q=0.9,en;q=0.8")
    results.record(
        "Accept-Language ID detected",
        locale == "id"
    )
    
    locale = detect_locale(accept_language="en-US,en;q=0.9")
    results.record(
        "Accept-Language EN detected",
        locale == "en"
    )
    
    # Test priority (lang_param over accept_language)
    locale = detect_locale(lang_param="id", accept_language="en-US")
    results.record(
        "lang_param priority",
        locale == "id"
    )
    
    # Test default
    locale = detect_locale()
    results.record(
        "Default locale fallback",
        locale == "en"
    )
    
    return None


def test_supported_locales(results: TestResults, i18n: I18nEngine):
    """Test supported locales listing."""
    print("\n📋 TEST: Supported Locales")
    print("-" * 40)
    
    locales = i18n.get_locales()
    
    results.record(
        "Locales list returned",
        isinstance(locales, list)
    )
    
    results.record(
        "Has 2 locales",
        len(locales) == 2
    )
    
    # Check Indonesian
    id_locale = next((l for l in locales if l["code"] == "id"), None)
    results.record(
        "Indonesian locale info",
        id_locale is not None
    )
    if id_locale:
        results.record(
            "Indonesian name correct",
            id_locale["name"] == "Bahasa Indonesia"
        )
    
    # Check English
    en_locale = next((l for l in locales if l["code"] == "en"), None)
    results.record(
        "English locale info",
        en_locale is not None
    )
    if en_locale:
        results.record(
            "English name correct",
            en_locale["name"] == "English"
        )
    
    return i18n


def test_translation_keys(results: TestResults, i18n: I18nEngine):
    """Test translation keys listing."""
    print("\n🔑 TEST: Translation Keys")
    print("-" * 40)
    
    keys = i18n.get_all_keys("en")
    
    results.record(
        "Keys list returned",
        isinstance(keys, list)
    )
    
    results.record(
        "Has translation keys",
        len(keys) > 0
    )
    
    results.record(
        "Contains payment.success",
        "payment.success" in keys
    )
    
    results.record(
        "Contains auth.login.success",
        "auth.login.success" in keys
    )
    
    return i18n


def test_batch_translations(results: TestResults, i18n: I18nEngine):
    """Test batch translation retrieval."""
    print("\n📦 TEST: Batch Translations")
    print("-" * 40)
    
    keys = ["payment.success", "payment.failed", "auth.login.success"]
    
    translations = i18n.get_messages(keys, "id")
    
    results.record(
        "Batch translations returned",
        isinstance(translations, dict)
    )
    
    results.record(
        "Correct number of translations",
        len(translations) == 3
    )
    
    results.record(
        "payment.success translated (ID)",
        "berhasil" in translations["payment.success"]
    )
    
    return i18n


def test_localized_response(results: TestResults, i18n: I18nEngine):
    """Test localized response helper."""
    print("\n📨 TEST: Localized Response Helper")
    print("-" * 40)
    
    response = localized_response(
        data={"id": 1},
        message_key="success",
        locale="id"
    )
    
    results.record(
        "Response has data",
        "data" in response
    )
    
    results.record(
        "Response has message",
        "message" in response
    )
    
    results.record(
        "Message translated to ID",
        response["message"] == "Berhasil"
    )
    
    results.record(
        "Response has locale",
        "locale" in response
    )
    
    return i18n


def test_localized_error(results: TestResults, i18n: I18nEngine):
    """Test localized error helper."""
    print("\n⚠️ TEST: Localized Error Helper")
    print("-" * 40)
    
    error = localized_error(
        error_key="error",
        locale="en"
    )
    
    results.record(
        "Error has error key",
        "error" in error
    )
    
    results.record(
        "Error message translated",
        error["error"] == "Error"
    )
    
    error_id = localized_error(
        error_key="error",
        locale="id"
    )
    
    results.record(
        "Error message translated (ID)",
        error_id["error"] == "Kesalahan"
    )
    
    return i18n


def test_payment_specific_translations(results: TestResults, i18n: I18nEngine):
    """Test payment-specific translations."""
    print("\n💳 TEST: Payment Translations")
    print("-" * 40)
    
    # QRIS
    results.record(
        "payment.qris (ID)",
        i18n.get_translation("payment.qris", "id") == "QRIS"
    )
    
    results.record(
        "payment.qris (EN)",
        i18n.get_translation("payment.qris", "en") == "QRIS"
    )
    
    # Settlement
    results.record(
        "payment.settlement (ID)",
        i18n.get_translation("payment.settlement", "id") == "Pembayaran telah disettle"
    )
    
    results.record(
        "payment.settlement (EN)",
        i18n.get_translation("payment.settlement", "en") == "Payment settled"
    )
    
    # Refund
    results.record(
        "payment.refund (ID)",
        i18n.get_translation("payment.refund", "id") == "Refund berhasil"
    )
    
    return i18n


def test_revenue_translations(results: TestResults, i18n: I18nEngine):
    """Test revenue-specific translations."""
    print("\n💰 TEST: Revenue Translations")
    print("-" * 40)
    
    # CEO Split
    results.record(
        "revenue.split.ceo (ID)",
        i18n.get_translation("revenue.split.ceo", "id") == "Bagian CEO (60%)"
    )
    
    results.record(
        "revenue.split.ceo (EN)",
        i18n.get_translation("revenue.split.ceo", "en") == "CEO Share (60%)"
    )
    
    # Ops Split
    results.record(
        "revenue.split.ops (ID)",
        i18n.get_translation("revenue.split.ops", "id") == "Bagian Operasional (40%)"
    )
    
    results.record(
        "revenue.split.ops (EN)",
        i18n.get_translation("revenue.split.ops", "en") == "Operations Share (40%)"
    )
    
    return i18n


def test_rbac_translations(results: TestResults, i18n: I18nEngine):
    """Test RBAC-specific translations."""
    print("\n🔐 TEST: RBAC Translations")
    print("-" * 40)
    
    results.record(
        "auth.forbidden (ID)",
        i18n.get_translation("auth.forbidden", "id") == "Anda tidak memiliki izin untuk mengakses resource ini"
    )
    
    results.record(
        "auth.forbidden (EN)",
        i18n.get_translation("auth.forbidden", "en") == "You do not have permission to access this resource"
    )
    
    results.record(
        "rbac.permission.denied (ID)",
        i18n.get_translation("rbac.permission.denied", "id") == "Izin ditolak"
    )
    
    return i18n


def test_quick_translation_function(results: TestResults):
    """Test quick translation function."""
    print("\n⚡ TEST: Quick Translation Function")
    print("-" * 40)
    
    from app.core.i18n import t
    
    results.record(
        "t() function works (EN)",
        t("success", "en") == "Success"
    )
    
    results.record(
        "t() function works (ID)",
        t("success", "id") == "Berhasil"
    )
    
    return None


def test_locale_helper_method(results: TestResults, i18n: I18nEngine):
    """Test t() alias method."""
    print("\n🔧 TEST: t() Alias Method")
    print("-" * 40)
    
    results.record(
        "t() alias works",
        i18n.t("error") == "Error"
    )
    
    results.record(
        "t() with locale works",
        i18n.t("error", "id") == "Kesalahan"
    )
    
    return i18n


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🌐 MAHALAKSMI AIOS v1.1.2 - Multilingual Tests")
    print("="*60)
    
    results = TestResults()
    
    try:
        # Basic tests
        i18n = test_i18n_initialization(results)
        
        # Language-specific tests
        test_indonesian_translations(results, i18n)
        test_english_translations(results, i18n)
        
        # Switching and fallback
        test_locale_switching(results, i18n)
        test_fallback_mechanism(results, i18n)
        
        # Detection
        test_locale_detection(results)
        
        # Listing
        test_supported_locales(results, i18n)
        test_translation_keys(results, i18n)
        
        # Batch
        test_batch_translations(results, i18n)
        
        # Helpers
        test_localized_response(results, i18n)
        test_localized_error(results, i18n)
        
        # Domain-specific
        test_payment_specific_translations(results, i18n)
        test_revenue_translations(results, i18n)
        test_rbac_translations(results, i18n)
        
        # Quick functions
        test_quick_translation_function(results)
        test_locale_helper_method(results, i18n)
        
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
    success = run_all_tests()
    sys.exit(0 if success else 1)
