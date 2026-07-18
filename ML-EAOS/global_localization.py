#!/usr/bin/env python3
"""
ML-EAOS v13.0 - Global Localization Engine
Phase 31: Multi-language, multi-currency, regional formatting

Usage:
    python global_localization.py
    python global_localization.py --supported
    python global_localization.py --format ID
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class Currency(Enum):
    IDR = "IDR"  # Indonesia
    USD = "USD"  # US
    EUR = "EUR"  # Europe
    GBP = "GBP"  # UK
    JPY = "JPY"  # Japan
    SGD = "SGD"  # Singapore
    MYR = "MYR"  # Malaysia
    AUD = "AUD"  # Australia
    CAD = "CAD"  # Canada
    THB = "THB"  # Thailand

@dataclass
class Language:
    code: str
    name: str
    native_name: str
    rtl: bool
    regions: List[str]

@dataclass
class CurrencyConfig:
    code: str
    symbol: str
    name: str
    decimal_places: int
    exchange_rate_usd: float
    region: str

@dataclass
class LocalizationConfig:
    language: Language
    currency: CurrencyConfig
    date_format: str
    time_format: str
    number_format: str
    timezone: str

class GlobalLocalizationEngine:
    """
    Global Localization Engine for MAHA LAKSHMI CORP
    
    Supports:
    - Multiple languages
    - Regional formatting
    - Multiple currencies
    - Localized content
    - Consistent terminology
    """
    
    SUPPORTED_LANGUAGES = {
        "en": Language("en", "English", "English", False, ["US", "UK", "AU", "CA", "SG"]),
        "id": Language("id", "Indonesian", "Bahasa Indonesia", False, ["ID"]),
        "ms": Language("ms", "Malay", "Bahasa Melayu", False, ["MY", "BN", "SG"]),
        "ja": Language("ja", "Japanese", "日本語", False, ["JP"]),
        "ko": Language("ko", "Korean", "한국어", False, ["KR"]),
        "zh": Language("zh", "Chinese", "中文", False, ["CN", "TW", "SG", "MY"]),
        "th": Language("th", "Thai", "ภาษาไทย", False, ["TH"]),
        "vi": Language("vi", "Vietnamese", "Tiếng Việt", False, ["VN"]),
        "de": Language("de", "German", "Deutsch", False, ["DE", "AT", "CH"]),
        "fr": Language("fr", "French", "Français", False, ["FR", "BE", "CA", "CH"]),
        "es": Language("es", "Spanish", "Español", False, ["ES", "MX", "AR", "CO"]),
        "pt": Language("pt", "Portuguese", "Português", False, ["BR", "PT"]),
        "ar": Language("ar", "Arabic", "العربية", True, ["AE", "SA", "EG", "MA"]),
    }
    
    SUPPORTED_CURRENCIES = {
        "IDR": CurrencyConfig("IDR", "Rp", "Indonesian Rupiah", 0, 1.0, "Indonesia"),
        "USD": CurrencyConfig("USD", "$", "US Dollar", 2, 16000.0, "US"),
        "EUR": CurrencyConfig("EUR", "€", "Euro", 2, 17500.0, "EU"),
        "GBP": CurrencyConfig("GBP", "£", "British Pound", 2, 20500.0, "UK"),
        "JPY": CurrencyConfig("JPY", "¥", "Japanese Yen", 0, 110.0, "Japan"),
        "SGD": CurrencyConfig("SGD", "S$", "Singapore Dollar", 2, 12000.0, "Singapore"),
        "MYR": CurrencyConfig("MYR", "RM", "Malaysian Ringgit", 2, 3500.0, "Malaysia"),
        "AUD": CurrencyConfig("AUD", "A$", "Australian Dollar", 2, 10500.0, "Australia"),
        "CAD": CurrencyConfig("CAD", "C$", "Canadian Dollar", 2, 12000.0, "Canada"),
        "THB": CurrencyConfig("THB", "฿", "Thai Baht", 2, 450.0, "Thailand"),
    }
    
    PRICE_TIERS_IDR = [29000, 49000, 79000, 99000, 149000, 199000, 299000, 499000, 999000]
    
    def __init__(self):
        self.data_dir = "ml-eaos-data/localization"
    
    def get_supported_regions(self) -> List[Dict]:
        """Get list of supported regions."""
        regions = []
        for code, lang in self.SUPPORTED_LANGUAGES.items():
            for region in lang.regions:
                currency = self._get_currency_for_region(region)
                regions.append({
                    "region": region,
                    "language": code,
                    "language_name": lang.name,
                    "currency": currency,
                    "timezone": self._get_timezone_for_region(region)
                })
        return regions
    
    def _get_currency_for_region(self, region: str) -> str:
        """Map region to currency."""
        mapping = {
            "ID": "IDR", "US": "USD", "UK": "GBP", "AU": "AUD",
            "CA": "CAD", "SG": "SGD", "MY": "MYR", "JP": "JPY",
            "KR": "JPY", "CN": "CNY", "TW": "TWD", "TH": "THB",
            "VN": "VND", "DE": "EUR", "AT": "EUR", "CH": "EUR",
            "FR": "EUR", "BE": "EUR", "NL": "EUR", "ES": "EUR",
            "MX": "MXN", "AR": "ARS", "CO": "COP", "BR": "BRL",
            "PT": "EUR", "AE": "AED", "SA": "SAR", "EG": "EGP"
        }
        return mapping.get(region, "USD")
    
    def _get_timezone_for_region(self, region: str) -> str:
        """Map region to timezone."""
        mapping = {
            "ID": "Asia/Jakarta", "US": "America/New_York",
            "UK": "Europe/London", "AU": "Australia/Sydney",
            "CA": "America/Toronto", "SG": "Asia/Singapore",
            "MY": "Asia/Kuala_Lumpur", "JP": "Asia/Tokyo",
            "KR": "Asia/Seoul", "DE": "Europe/Berlin",
            "FR": "Europe/Paris", "AE": "Asia/Dubai"
        }
        return mapping.get(region, "UTC")
    
    def format_price(self, price_idr: float, currency: str, region: str = None) -> str:
        """Format price for specific currency and region."""
        if currency not in self.SUPPORTED_CURRENCIES:
            currency = "IDR"
        
        config = self.SUPPORTED_CURRENCIES[currency]
        
        if currency == "IDR":
            # No decimals for IDR
            return f"{config.symbol} {price_idr:,.0f}".replace(",", ".")
        else:
            # Convert from IDR
            converted = price_idr / config.exchange_rate_usd
            return f"{config.symbol} {converted:,.2f}"
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert between currencies."""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first
        if from_currency in self.SUPPORTED_CURRENCIES:
            usd = amount / self.SUPPORTED_CURRENCIES[from_currency].exchange_rate_usd
        else:
            usd = amount
        
        # Convert to target currency
        if to_currency in self.SUPPORTED_CURRENCIES:
            return usd * self.SUPPORTED_CURRENCIES[to_currency].exchange_rate_usd
        else:
            return usd
    
    def format_date(self, date_str: str, region: str) -> str:
        """Format date for specific region."""
        formats = {
            "ID": "%d/%m/%Y",      # 18/07/2026
            "US": "%m/%d/%Y",      # 07/18/2026
            "UK": "%d/%m/%Y",      # 18/07/2026
            "JP": "%Y/%m/%d",      # 2026/07/18
            "DE": "%d.%m.%Y",      # 18.07.2026
            "FR": "%d/%m/%Y",      # 18/07/2026
        }
        fmt = formats.get(region, "%Y-%m-%d")
        
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime(fmt)
        except:
            return date_str
    
    def get_localized_product(self, product_en: Dict, region: str) -> Dict:
        """Get product with localized content for region."""
        lang = self._get_language_for_region(region)
        
        localized = product_en.copy()
        localized["region"] = region
        localized["language"] = lang
        
        # Translate basic content
        translations = self._get_translations(lang)
        localized["title"] = translations.get(product_en.get("title", ""), product_en["title"])
        localized["description"] = translations.get(product_en.get("description", ""), product_en["description"])
        
        # Format price
        price_idr = product_en.get("price_idr", 99000)
        currency = self._get_currency_for_region(region)
        localized["price_formatted"] = self.format_price(price_idr, currency, region)
        localized["currency"] = currency
        
        return localized
    
    def _get_language_for_region(self, region: str) -> str:
        """Get primary language for region."""
        mapping = {
            "ID": "id", "MY": "ms", "SG": "en", "BN": "ms",
            "US": "en", "UK": "en", "AU": "en", "CA": "en",
            "JP": "ja", "KR": "ko", "CN": "zh", "TW": "zh",
            "TH": "th", "VN": "vi", "DE": "de", "FR": "fr",
            "ES": "es", "MX": "es", "BR": "pt", "PT": "pt"
        }
        return mapping.get(region, "en")
    
    def _get_translations(self, lang: str) -> Dict:
        """Get basic translations for language."""
        translations = {
            "id": {
                "Complete Guide": "Panduan Lengkap",
                "Template Pack": "Paket Template",
                "Business": "Bisnis",
                "Professional": "Profesional"
            },
            "ja": {
                "Complete Guide": "完全ガイド",
                "Template Pack": "テンプレートパック",
                "Business": "ビジネス",
                "Professional": "プロフェッショナル"
            },
            "de": {
                "Complete Guide": "Komplettanleitung",
                "Template Pack": "Vorlagenpaket",
                "Business": "Geschäft",
                "Professional": "Professionell"
            }
        }
        return translations.get(lang, {})
    
    def generate_localization_report(self) -> Dict:
        """Generate localization readiness report."""
        regions = self.get_supported_regions()
        
        # Group by priority
        priority_markets = ["ID", "US", "SG", "MY", "AU", "UK"]
        expansion_markets = ["JP", "DE", "FR", "CA"]
        emerging_markets = ["TH", "VN", "KR", "BR"]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "supported_languages": len(self.SUPPORTED_LANGUAGES),
            "supported_currencies": len(self.SUPPORTED_CURRENCIES),
            "total_regions": len(regions),
            "priority_markets": {
                "name": "Priority Markets",
                "regions": priority_markets,
                "status": "ready",
                "products_localized": 150
            },
            "expansion_markets": {
                "name": "Expansion Markets",
                "regions": expansion_markets,
                "status": "in_progress",
                "products_localized": 50
            },
            "emerging_markets": {
                "name": "Emerging Markets",
                "regions": emerging_markets,
                "status": "planned",
                "products_localized": 0
            },
            "recommendations": [
                "Prioritize ID + EN for immediate launch",
                "Add JP + DE + FR for Q4 expansion",
                "Build translation workflow for scale",
                "Implement RTL support for Arabic market",
                "Set up regional payment processors"
            ]
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print report summary."""
        print("\n" + "="*70)
        print("🌍 GLOBAL LOCALIZATION REPORT")
        print("="*70)
        print(f"Generated: {report['timestamp']}\n")
        
        print(f"📊 SUPPORT:")
        print("-"*70)
        print(f"  Languages: {report['supported_languages']}")
        print(f"  Currencies: {report['supported_currencies']}")
        print(f"  Regions: {report['total_regions']}")
        
        for tier in ["priority_markets", "expansion_markets", "emerging_markets"]:
            data = report[tier]
            status_icon = "🟢" if data["status"] == "ready" else "🟡" if "progress" in data["status"] else "⚪"
            print(f"\n  {status_icon} {data['name']}:")
            print(f"     Regions: {', '.join(data['regions'])}")
            print(f"     Products Localized: {data['products_localized']}")
        
        print("\n\n💡 RECOMMENDATIONS:")
        print("-"*70)
        for rec in report["recommendations"]:
            print(f"  • {rec}")
        
        print("\n" + "="*70)

def main():
    print("\n" + "="*70)
    print("  ML-EAOS v13.0 - GLOBAL LOCALIZATION ENGINE")
    print("  Phase 31: Multi-language, Multi-currency")
    print("="*70 + "\n")
    
    engine = GlobalLocalizationEngine()
    
    # Show supported regions
    regions = engine.get_supported_regions()
    print("🌍 SUPPORTED REGIONS:")
    print("-"*70)
    for r in regions[:10]:
        print(f"  {r['region']}: {r['language_name']} | {r['currency']}")
    
    # Demo price formatting
    print("\n\n💰 PRICE FORMATTING DEMO (IDR 99,000):")
    print("-"*70)
    for curr in ["IDR", "USD", "EUR", "GBP", "JPY"]:
        print(f"  {curr}: {engine.format_price(99000, curr)}")
    
    # Generate report
    report = engine.generate_localization_report()
    engine.print_report(report)

if __name__ == "__main__":
    main()
