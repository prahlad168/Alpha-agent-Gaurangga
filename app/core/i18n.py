"""
MAHALAKSMI AIOS v1.0 - Volume I Chapter 3: Multilingual Interface System
Dynamic localization and translation capabilities
"""
import os
import sys
import logging
from typing import Dict, Optional, Any, Callable, List
from functools import wraps
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# TRANSLATION DICTIONARIES
# ============================================================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Indonesian (Bahasa Indonesia)
    "id": {
        # System
        "system.name": "MAHALAKSMI AIOS",
        "system.version": "Versi",
        "system.ready": "Sistem siap",
        "system.error": "Kesalahan sistem",
        
        # Auth
        "auth.login.success": "Login berhasil",
        "auth.login.failed": "Login gagal",
        "auth.logout.success": "Logout berhasil",
        "auth.token.invalid": "Token tidak valid",
        "auth.token.expired": "Token kedaluwarsa",
        "auth.access.denied": "Akses ditolak",
        "auth.forbidden": "Anda tidak memiliki izin untuk mengakses resource ini",
        "auth.unauthorized": "Autentikasi diperlukan",
        
        # Payment
        "payment.success": "Pembayaran berhasil",
        "payment.pending": "Pembayaran menunggu",
        "payment.failed": "Pembayaran gagal",
        "payment.cancelled": "Pembayaran dibatalkan",
        "payment.expired": "Pembayaran kedaluwarsa",
        "payment.settlement": "Pembayaran telah disettle",
        "payment.processing": "Pembayaran sedang diproses",
        "payment.refund": "Refund berhasil",
        "payment.qris": "QRIS",
        "payment.bca_va": "Virtual Account BCA",
        "payment.credit_card": "Kartu Kredit",
        
        # Revenue
        "revenue.recorded": "Revenue berhasil dicatat",
        "revenue.split.ceo": "Bagian CEO (60%)",
        "revenue.split.ops": "Bagian Operasional (40%)",
        "revenue.disbursement.requested": "Permintaan pencairan diminta",
        "revenue.disbursement.completed": "Pencairan selesai",
        
        # Customer
        "customer.created": "Pelanggan berhasil dibuat",
        "customer.updated": "Pelanggan berhasil diperbarui",
        "customer.deleted": "Pelanggan berhasil dihapus",
        "customer.not_found": "Pelanggan tidak ditemukan",
        
        # Ticket
        "ticket.created": "Tiket berhasil dibuat",
        "ticket.resolved": "Tiket resolved",
        "ticket.open": "Tiket terbuka",
        "ticket.closed": "Tiket ditutup",
        
        # Workflow
        "workflow.started": "Workflow dimulai",
        "workflow.completed": "Workflow selesai",
        "workflow.failed": "Workflow gagal",
        "workflow.cancelled": "Workflow dibatalkan",
        
        # Disaster Recovery
        "dr.healthy": "Sistem sehat",
        "dr.degraded": "Sistem degraded",
        "dr.failover.initiated": "Failover dimulai",
        "dr.recovery.initiated": "Recovery dimulai",
        "dr.recovery.completed": "Recovery selesai",
        "dr.state.normal": "Status normal",
        
        # RBAC
        "rbac.role.assigned": "Role berhasil ditetapkan",
        "rbac.permission.denied": "Izin ditolak",
        "rbac.user.created": "User berhasil dibuat",
        "rbac.user.deleted": "User berhasil dihapus",
        
        # General
        "success": "Berhasil",
        "error": "Kesalahan",
        "warning": "Peringatan",
        "info": "Informasi",
        "loading": "Memuat...",
        "save": "Simpan",
        "cancel": "Batal",
        "delete": "Hapus",
        "update": "Perbarui",
        "create": "Buat",
        "submit": "Kirim",
        "confirm": "Konfirmasi",
        "yes": "Ya",
        "no": "Tidak",
        "ok": "OK",
        "close": "Tutup",
        "back": "Kembali",
        "next": "Lanjut",
        "previous": "Sebelumnya",
        "search": "Cari",
        "filter": "Filter",
        "sort": "Urutkan",
        "page": "Halaman",
        "of": "dari",
        "showing": "Menampilkan",
        "results": "hasil",
        "no_results": "Tidak ada hasil",
        "loading_error": "Gagal memuat data",
        "save_error": "Gagal menyimpan",
        "delete_error": "Gagal menghapus",
        "update_error": "Gagal memperbarui",
        "create_error": "Gagal membuat",
        "validation_error": "Kesalahan validasi",
        "invalid_input": "Input tidak valid",
        "required_field": "Field ini wajib diisi",
        "server_error": "Kesalahan server",
        "network_error": "Kesalahan jaringan",
        "timeout": "Waktu habis",
        "try_again": "Coba lagi",
        "contact_support": "Hubungi support",
        "unknown_error": "Kesalahan tidak diketahui",
        
        # Date/Time
        "date.today": "Hari ini",
        "date.yesterday": "Kemarin",
        "date.tomorrow": "Besok",
        "time.now": "Sekarang",
        
        # Finance
        "finance.recorded": "Transaksi keuangan tercatat",
        "finance.balance": "Saldo",
        "finance.income": "Pemasukan",
        "finance.expense": "Pengeluaran",
        "finance.transfer": "Transfer",
        
        # Repository
        "repo.archived": "Arsip dibuat",
        "repo.sync.success": "Sinkronisasi berhasil",
        "repo.sync.failed": "Sinkronisasi gagal",
    },
    
    # English
    "en": {
        # System
        "system.name": "MAHALAKSMI AIOS",
        "system.version": "Version",
        "system.ready": "System ready",
        "system.error": "System error",
        
        # Auth
        "auth.login.success": "Login successful",
        "auth.login.failed": "Login failed",
        "auth.logout.success": "Logout successful",
        "auth.token.invalid": "Invalid token",
        "auth.token.expired": "Token expired",
        "auth.access.denied": "Access denied",
        "auth.forbidden": "You do not have permission to access this resource",
        "auth.unauthorized": "Authentication required",
        
        # Payment
        "payment.success": "Payment successful",
        "payment.pending": "Payment pending",
        "payment.failed": "Payment failed",
        "payment.cancelled": "Payment cancelled",
        "payment.expired": "Payment expired",
        "payment.settlement": "Payment settled",
        "payment.processing": "Payment processing",
        "payment.refund": "Refund successful",
        "payment.qris": "QRIS",
        "payment.bca_va": "BCA Virtual Account",
        "payment.credit_card": "Credit Card",
        
        # Revenue
        "revenue.recorded": "Revenue recorded successfully",
        "revenue.split.ceo": "CEO Share (60%)",
        "revenue.split.ops": "Operations Share (40%)",
        "revenue.disbursement.requested": "Disbursement requested",
        "revenue.disbursement.completed": "Disbursement completed",
        
        # Customer
        "customer.created": "Customer created successfully",
        "customer.updated": "Customer updated successfully",
        "customer.deleted": "Customer deleted successfully",
        "customer.not_found": "Customer not found",
        
        # Ticket
        "ticket.created": "Ticket created successfully",
        "ticket.resolved": "Ticket resolved",
        "ticket.open": "Ticket open",
        "ticket.closed": "Ticket closed",
        
        # Workflow
        "workflow.started": "Workflow started",
        "workflow.completed": "Workflow completed",
        "workflow.failed": "Workflow failed",
        "workflow.cancelled": "Workflow cancelled",
        
        # Disaster Recovery
        "dr.healthy": "System healthy",
        "dr.degraded": "System degraded",
        "dr.failover.initiated": "Failover initiated",
        "dr.recovery.initiated": "Recovery initiated",
        "dr.recovery.completed": "Recovery completed",
        "dr.state.normal": "Status normal",
        
        # RBAC
        "rbac.role.assigned": "Role assigned successfully",
        "rbac.permission.denied": "Permission denied",
        "rbac.user.created": "User created successfully",
        "rbac.user.deleted": "User deleted successfully",
        
        # General
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "loading": "Loading...",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "update": "Update",
        "create": "Create",
        "submit": "Submit",
        "confirm": "Confirm",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "close": "Close",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "search": "Search",
        "filter": "Filter",
        "sort": "Sort",
        "page": "Page",
        "of": "of",
        "showing": "Showing",
        "results": "results",
        "no_results": "No results found",
        "loading_error": "Failed to load data",
        "save_error": "Failed to save",
        "delete_error": "Failed to delete",
        "update_error": "Failed to update",
        "create_error": "Failed to create",
        "validation_error": "Validation error",
        "invalid_input": "Invalid input",
        "required_field": "This field is required",
        "server_error": "Server error",
        "network_error": "Network error",
        "timeout": "Timeout",
        "try_again": "Try again",
        "contact_support": "Contact support",
        "unknown_error": "Unknown error occurred",
        
        # Date/Time
        "date.today": "Today",
        "date.yesterday": "Yesterday",
        "date.tomorrow": "Tomorrow",
        "time.now": "Now",
        
        # Finance
        "finance.recorded": "Financial transaction recorded",
        "finance.balance": "Balance",
        "finance.income": "Income",
        "finance.expense": "Expense",
        "finance.transfer": "Transfer",
        
        # Repository
        "repo.archived": "Archive created",
        "repo.sync.success": "Sync successful",
        "repo.sync.failed": "Sync failed",
    }
}


# ============================================================================
# SUPPORTED LOCALES
# ============================================================================

SUPPORTED_LOCALES = {
    "id": {
        "code": "id",
        "name": "Bahasa Indonesia",
        "native_name": "Bahasa Indonesia",
        "direction": "ltr",
        "status": "active"
    },
    "en": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "direction": "ltr",
        "status": "active"
    }
}

DEFAULT_LOCALE = "en"
FALLBACK_LOCALE = "en"


# ============================================================================
# I18N ENGINE
# ============================================================================

class I18nEngine:
    """
    Internationalization Engine.
    Handles translation retrieval and language detection.
    """
    
    def __init__(self):
        self.translations = TRANSLATIONS
        self.supported_locales = SUPPORTED_LOCALES
        self.default_locale = DEFAULT_LOCALE
        self.fallback_locale = FALLBACK_LOCALE
        logger.info(f"I18nEngine initialized with {len(self.translations)} locales")
    
    def get_translation(self, key: str, locale: str = None) -> str:
        """
        Get translation for a key.
        
        Args:
            key: Translation key (e.g., 'payment.success')
            locale: Language code (e.g., 'id', 'en')
        
        Returns:
            Translated string, or key itself if not found
        """
        # Use default locale if not specified
        if locale is None:
            locale = self.default_locale
        
        # Try specified locale
        if locale in self.translations:
            translations = self.translations[locale]
            if key in translations:
                return translations[key]
        
        # Fallback to default locale
        if locale != self.fallback_locale:
            if self.fallback_locale in self.translations:
                translations = self.translations[self.fallback_locale]
                if key in translations:
                    return translations[key]
        
        # Return key itself if not found
        return key
    
    def t(self, key: str, locale: str = None) -> str:
        """Alias for get_translation."""
        return self.get_translation(key, locale)
    
    def get_locale(self, key: str, locale: str = None) -> Dict[str, str]:
        """
        Get a localized response object.
        
        Args:
            key: Translation key
            locale: Language code
        
        Returns:
            Dict with key, locale, and translation
        """
        translation = self.get_translation(key, locale)
        return {
            "key": key,
            "locale": locale or self.default_locale,
            "translation": translation
        }
    
    def get_messages(self, keys: list, locale: str = None) -> Dict[str, str]:
        """
        Get multiple translations at once.
        
        Args:
            keys: List of translation keys
            locale: Language code
        
        Returns:
            Dict mapping keys to translations
        """
        return {key: self.get_translation(key, locale) for key in keys}
    
    def get_all_keys(self, locale: str = None) -> List[str]:
        """Get all available translation keys."""
        if locale and locale in self.translations:
            return list(self.translations[locale].keys())
        return list(self.translations.get(self.default_locale, {}).keys())
    
    def get_locales(self) -> List[Dict]:
        """Get list of supported locales."""
        return [
            {
                **info,
                "translation_count": len(self.translations.get(code, {}))
            }
            for code, info in self.supported_locales.items()
        ]
    
    def is_locale_supported(self, locale: str) -> bool:
        """Check if locale is supported."""
        return locale in self.supported_locales


# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

def detect_locale_from_request(request) -> str:
    """
    Detect locale from HTTP request.
    
    Priority:
    1. Query parameter 'lang'
    2. Header 'Accept-Language'
    3. Default locale
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Detected locale code
    """
    # 1. Check query parameter
    lang_param = request.query_params.get("lang") or request.query_params.get("locale")
    if lang_param:
        # Normalize to 2-letter code
        lang_code = lang_param.lower()[:2]
        if lang_code in SUPPORTED_LOCALES:
            return lang_code
    
    # 2. Check Accept-Language header
    accept_language = request.headers.get("accept-language", "")
    if accept_language:
        # Parse Accept-Language header
        # Format: "en-US,en;q=0.9,id;q=0.8"
        languages = []
        for part in accept_language.split(","):
            part = part.strip()
            if part:
                if ";" in part:
                    lang, q = part.split(";", 1)
                    lang = lang.strip()
                else:
                    lang = part
                    q = 1.0
                
                # Normalize to 2-letter code
                lang_code = lang.lower()[:2]
                if lang_code in SUPPORTED_LOCALES:
                    return lang_code
    
    # 3. Return default
    return DEFAULT_LOCALE


def detect_locale(lang_param: str = None, accept_language: str = None) -> str:
    """
    Detect locale from parameters (for non-request contexts).
    
    Args:
        lang_param: Language parameter from query string
        accept_language: Accept-Language header value
    
    Returns:
        Detected locale code
    """
    # 1. Check lang_param
    if lang_param:
        lang_code = lang_param.lower()[:2]
        if lang_code in SUPPORTED_LOCALES:
            return lang_code
    
    # 2. Check accept_language
    if accept_language:
        for part in accept_language.split(","):
            part = part.strip()
            if part:
                lang = part.split(";")[0].strip()
                lang_code = lang.lower()[:2]
                if lang_code in SUPPORTED_LOCALES:
                    return lang_code
    
    # 3. Return default
    return DEFAULT_LOCALE


# ============================================================================
# LOCALIZED RESPONSE HELPERS
# ============================================================================

def localized_response(
    data: Any,
    message_key: str = None,
    locale: str = None
) -> Dict:
    """
    Create a localized API response.
    
    Args:
        data: Response data
        message_key: Translation key for message
        locale: Language code
    
    Returns:
        Localized response dict
    """
    engine = get_i18n_engine()
    
    response = {"data": data}
    
    if message_key:
        response["message"] = engine.get_translation(message_key, locale)
        response["locale"] = locale or engine.default_locale
    
    return response


def localized_error(
    error_key: str,
    locale: str = None,
    details: Dict = None
) -> Dict:
    """
    Create a localized error response.
    
    Args:
        error_key: Translation key for error
        locale: Language code
        details: Additional error details
    
    Returns:
        Localized error dict
    """
    engine = get_i18n_engine()
    
    response = {
        "error": engine.get_translation(error_key, locale),
        "locale": locale or engine.default_locale
    }
    
    if details:
        response["details"] = details
    
    return response


# ============================================================================
# DECORATOR FOR LOCALIZATION
# ============================================================================

def localized(locale_param: str = "lang"):
    """
    Decorator to automatically detect and inject locale into functions.
    
    Usage:
        @localized()
        async def my_endpoint(locale: str = "en"):
            return localized_response({"key": "value"}, "success", locale)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args if available
            request = None
            for arg in args:
                if hasattr(arg, "query_params"):
                    request = arg
                    break
            
            # Detect locale
            if request:
                locale = detect_locale_from_request(request)
            elif locale_param in kwargs:
                locale = kwargs.pop(locale_param)
            else:
                locale = DEFAULT_LOCALE
            
            # Add locale to kwargs
            kwargs["locale"] = locale
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_i18n_engine: Optional[I18nEngine] = None


def get_i18n_engine() -> I18nEngine:
    """Get or create global I18n engine."""
    global _i18n_engine
    if _i18n_engine is None:
        _i18n_engine = I18nEngine()
    return _i18n_engine


def t(key: str, locale: str = None) -> str:
    """Quick translation function."""
    return get_i18n_engine().get_translation(key, locale)


def locale_detect(**kwargs) -> str:
    """Quick locale detection."""
    return detect_locale(**kwargs)
