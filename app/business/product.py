"""
MAHALAKSMI AIOS v1.0 - Volume IV Chapter 36: Product Center & Licensing
Digital asset management, license key generation, and automated activation
"""
import os
import sys
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.core.security_ext import get_license_generator, get_crypto
from app.business.revenue import get_revenue_manager

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class ProductType(Enum):
    """Product types."""
    SOFTWARE = "software"
    COURSE = "course"
    TEMPLATE = "template"
    SERVICE = "service"
    SUBSCRIPTION = "subscription"


class LicenseStatus(Enum):
    """License statuses."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class PricingModel(Enum):
    """Pricing models."""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    SUBSCRIPTION = "subscription"
    METERED = "metered"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Product:
    """Digital product."""
    product_id: str
    name: str
    description: str
    product_type: ProductType
    pricing_model: PricingModel
    price: float  # in IDR
    currency: str = "IDR"
    
    # License settings
    license_duration_days: int = 365
    max_activations: int = 1
    
    # Metadata
    version: str = "1.0.0"
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


@dataclass
class License:
    """Product license."""
    license_id: str
    license_key: str
    product_id: str
    customer_id: str
    encrypted_data: str  # Encrypted license data
    
    status: LicenseStatus = LicenseStatus.ACTIVE
    activations: int = 0
    max_activations: int = 1
    
    created_at: str = ""
    expires_at: str = ""
    last_used: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class Customer:
    """Customer record."""
    customer_id: str
    name: str
    email: str
    phone: str = ""
    created_at: str = ""
    
    # Stats
    total_purchases: int = 0
    active_licenses: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# ============================================================================
# PRODUCT DATABASE
# ============================================================================

class ProductDatabase:
    """SQLite database for products and licenses."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "products.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                product_type TEXT,
                pricing_model TEXT,
                price REAL,
                currency TEXT DEFAULT 'IDR',
                license_duration_days INTEGER DEFAULT 365,
                max_activations INTEGER DEFAULT 1,
                version TEXT DEFAULT '1.0.0',
                created_at TEXT,
                updated_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TEXT,
                total_purchases INTEGER DEFAULT 0,
                active_licenses INTEGER DEFAULT 0
            )
        """)
        
        # Licenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                license_id TEXT PRIMARY KEY,
                license_key TEXT UNIQUE,
                product_id TEXT,
                customer_id TEXT,
                encrypted_data TEXT,
                status TEXT DEFAULT 'active',
                activations INTEGER DEFAULT 0,
                max_activations INTEGER DEFAULT 1,
                created_at TEXT,
                expires_at TEXT,
                last_used TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Product database initialized: {self.db_path}")
    
    def save_product(self, product: Product) -> bool:
        """Save product to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO products 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.product_id,
                product.name,
                product.description,
                product.product_type.value,
                product.pricing_model.value,
                product.price,
                product.currency,
                product.license_duration_days,
                product.max_activations,
                product.version,
                product.created_at,
                product.updated_at,
                1 if product.is_active else 0
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save product: {e}")
            return False
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Product(
                product_id=row['product_id'],
                name=row['name'],
                description=row['description'],
                product_type=ProductType(row['product_type']),
                pricing_model=PricingModel(row['pricing_model']),
                price=row['price'],
                currency=row['currency'],
                license_duration_days=row['license_duration_days'],
                max_activations=row['max_activations'],
                version=row['version'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                is_active=bool(row['is_active'])
            )
        return None
    
    def list_products(self, active_only: bool = True) -> List[Product]:
        """List all products."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM products"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Product(
                product_id=row['product_id'],
                name=row['name'],
                description=row['description'],
                product_type=ProductType(row['product_type']),
                pricing_model=PricingModel(row['pricing_model']),
                price=row['price'],
                currency=row['currency'],
                license_duration_days=row['license_duration_days'],
                max_activations=row['max_activations'],
                version=row['version'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                is_active=bool(row['is_active'])
            )
            for row in rows
        ]
    
    def save_license(self, license: License) -> bool:
        """Save license to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO licenses 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                license.license_id,
                license.license_key,
                license.product_id,
                license.customer_id,
                license.encrypted_data,
                license.status.value,
                license.activations,
                license.max_activations,
                license.created_at,
                license.expires_at,
                license.last_used
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save license: {e}")
            return False
    
    def get_license(self, license_key: str = None, license_id: str = None) -> Optional[License]:
        """Get license by key or ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if license_key:
            cursor.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
        elif license_id:
            cursor.execute("SELECT * FROM licenses WHERE license_id = ?", (license_id,))
        else:
            return None
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return License(
                license_id=row['license_id'],
                license_key=row['license_key'],
                product_id=row['product_id'],
                customer_id=row['customer_id'],
                encrypted_data=row['encrypted_data'],
                status=LicenseStatus(row['status']),
                activations=row['activations'],
                max_activations=row['max_activations'],
                created_at=row['created_at'],
                expires_at=row['expires_at'],
                last_used=row['last_used']
            )
        return None
    
    def get_customer_licenses(self, customer_id: str) -> List[License]:
        """Get all licenses for a customer."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM licenses WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            License(
                license_id=row['license_id'],
                license_key=row['license_key'],
                product_id=row['product_id'],
                customer_id=row['customer_id'],
                encrypted_data=row['encrypted_data'],
                status=LicenseStatus(row['status']),
                activations=row['activations'],
                max_activations=row['max_activations'],
                created_at=row['created_at'],
                expires_at=row['expires_at'],
                last_used=row['last_used']
            )
            for row in rows
        ]
    
    def save_customer(self, customer: Customer) -> bool:
        """Save customer to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO customers 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                customer.customer_id,
                customer.name,
                customer.email,
                customer.phone,
                customer.created_at,
                customer.total_purchases,
                customer.active_licenses
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save customer: {e}")
            return False


# ============================================================================
# PRODUCT CENTER
# ============================================================================

class ProductCenter:
    """
    Digital Product Management & Licensing Center.
    Handles product catalog, license generation, and activation.
    """
    
    def __init__(self):
        self.db = ProductDatabase()
        self.license_gen = get_license_generator()
        self.crypto = get_crypto()
        self.revenue = get_revenue_manager()
        
        # Initialize with default products
        self._init_default_products()
        
        logger.info("ProductCenter initialized")
    
    def _init_default_products(self):
        """Initialize default product catalog."""
        default_products = [
            Product(
                product_id="MLK-SOFTWARE-001",
                name="GAURANGA AI Assistant",
                description="Enterprise AI assistant with multi-agent support",
                product_type=ProductType.SOFTWARE,
                pricing_model=PricingModel.SUBSCRIPTION,
                price=500000,
                license_duration_days=365
            ),
            Product(
                product_id="MLK-COURSE-001",
                name="AI Business Masterclass",
                description="Complete course on building AI-powered businesses",
                product_type=ProductType.COURSE,
                pricing_model=PricingModel.ONE_TIME,
                price=2500000
            ),
            Product(
                product_id="MLK-TEMPLATE-001",
                name="Business Dashboard Template",
                description="Professional dashboard template for business analytics",
                product_type=ProductType.TEMPLATE,
                pricing_model=PricingModel.ONE_TIME,
                price=500000
            ),
        ]
        
        for product in default_products:
            existing = self.db.get_product(product.product_id)
            if not existing:
                self.db.save_product(product)
                logger.info(f"Added default product: {product.name}")
    
    def create_product(
        self,
        name: str,
        description: str,
        product_type: ProductType,
        pricing_model: PricingModel,
        price: float,
        **kwargs
    ) -> Product:
        """Create a new product."""
        import hashlib
        product_id = f"MLK-{product_type.value.upper()}-{hashlib.md5(name.encode()).hexdigest()[:6].upper()}"
        
        product = Product(
            product_id=product_id,
            name=name,
            description=description,
            product_type=product_type,
            pricing_model=pricing_model,
            price=price,
            **kwargs
        )
        
        self.db.save_product(product)
        logger.info(f"Product created: {product_id}")
        return product
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return self.db.get_product(product_id)
    
    def list_products(self) -> List[Dict]:
        """List all products with pricing."""
        products = self.db.list_products()
        return [
            {
                "product_id": p.product_id,
                "name": p.name,
                "description": p.description,
                "type": p.product_type.value,
                "pricing_model": p.pricing_model.value,
                "price": p.price,
                "currency": p.currency,
                "license_duration_days": p.license_duration_days
            }
            for p in products
        ]
    
    async def purchase_and_activate(
        self,
        product_id: str,
        customer_id: str,
        customer_name: str,
        customer_email: str,
        payment_amount: float
    ) -> Dict:
        """
        Complete purchase flow: Record revenue + Generate license.
        Links payment to automatic license generation.
        """
        # Get product
        product = self.db.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Verify payment amount covers product price
        if payment_amount < product.price:
            raise ValueError(f"Insufficient payment: {payment_amount} < {product.price}")
        
        # Record revenue (links to Revenue Engine)
        import uuid
        revenue_txn = await self.revenue.record_digital_revenue(
            source=f"product_{product_id}",
            amount=payment_amount,
            payment_method="qris",
            metadata={
                "product_id": product_id,
                "customer_id": customer_id,
                "transaction_type": "product_purchase"
            }
        )
        
        # Generate license key
        license_result = self.license_gen.generate_key(
            product_id=product_id,
            customer_id=customer_id,
            expires_days=product.license_duration_days
        )
        
        # Create license record
        license = License(
            license_id=f"LIC-{uuid.uuid4().hex[:12].upper()}",
            license_key=license_result["license_key"],
            product_id=product_id,
            customer_id=customer_id,
            encrypted_data=license_result["license_data"],
            expires_at=license_result["expires_at"],
            max_activations=product.max_activations
        )
        
        self.db.save_license(license)
        
        # Ensure customer exists
        customer = Customer(
            customer_id=customer_id,
            name=customer_name,
            email=customer_email
        )
        self.db.save_customer(customer)
        
        logger.info(f"License generated: {license.license_key} for customer {customer_id}")
        
        return {
            "success": True,
            "license_key": license.license_key,
            "product_name": product.name,
            "expires_at": license.expires_at,
            "revenue_transaction_id": revenue_txn.transaction_id,
            "activations_remaining": license.max_activations
        }
    
    def validate_license(self, license_key: str) -> Dict:
        """Validate a license key."""
        license = self.db.get_license(license_key=license_key)
        if not license:
            return {"valid": False, "reason": "License not found"}
        
        # Validate using license generator
        validation = self.license_gen.validate_key(
            license.license_key,
            license.encrypted_data
        )
        
        # Check activations
        if validation["valid"] and license.activations >= license.max_activations:
            return {"valid": False, "reason": "Maximum activations reached"}
        
        # Update last used
        if validation["valid"]:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE licenses SET last_used = ?, activations = activations + 1 WHERE license_id = ?",
                (datetime.now().isoformat(), license.license_id)
            )
            conn.commit()
            conn.close()
            
            validation["activations"] = license.activations + 1
            validation["max_activations"] = license.max_activations
            validation["product_id"] = license.product_id
        
        return validation
    
    def get_customer_portal(self, customer_id: str) -> Dict:
        """Get customer dashboard data."""
        licenses = self.db.get_customer_licenses(customer_id)
        
        products = {}
        for lic in licenses:
            if lic.product_id not in products:
                product = self.db.get_product(lic.product_id)
                if product:
                    products[lic.product_id] = product
        
        return {
            "customer_id": customer_id,
            "total_licenses": len(licenses),
            "active_licenses": sum(1 for l in licenses if l.status == LicenseStatus.ACTIVE),
            "licenses": [
                {
                    "license_id": l.license_id,
                    "license_key": l.license_key[:20] + "...",
                    "product_name": products.get(l.product_id, Product("", "", "", ProductType.SOFTWARE, PricingModel.ONE_TIME, 0)).name,
                    "status": l.status.value,
                    "expires_at": l.expires_at,
                    "activations": l.activations,
                    "max_activations": l.max_activations
                }
                for l in licenses
            ]
        }
    
    def get_catalog_stats(self) -> Dict:
        """Get product catalog statistics."""
        products = self.db.list_products()
        licenses = self.db.list_products()  # Would need separate query
        
        return {
            "total_products": len(products),
            "active_products": sum(1 for p in products if p.is_active),
            "total_revenue_from_products": 0,  # Would calculate from revenue system
            "products_by_type": {
                pt.value: sum(1 for p in products if p.product_type == pt)
                for pt in ProductType
            }
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_product_center: Optional[ProductCenter] = None


def get_product_center() -> ProductCenter:
    """Get or create global product center instance."""
    global _product_center
    if _product_center is None:
        _product_center = ProductCenter()
    return _product_center
