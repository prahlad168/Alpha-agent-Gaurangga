"""
MAHALAKSMI AIOS v1.0 - Midtrans Payment Gateway Client
Production-ready integration with Midtrans Snap API and Core API
"""
import os
import sys
import json
import hashlib
import hmac
import logging
import time
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class PaymentMethod(Enum):
    """Available payment methods."""
    CREDIT_CARD = "credit_card"
    BCA_VA = "bca_va"
    PERMATA_VA = "permata_va"
    OTHER_VA = "other_va"
    QRIS = "qris"
    E_CHANNEL = "e_channel"
    CELLPONE = "cellee"
    INDOMARET = "indomaret"
    Alfamart = "alfamart"
    BANK_TRANSFER = "bank_transfer"


class TransactionStatus(Enum):
    """Midtrans transaction status."""
    PENDING = "pending"
    SETTLEMENT = "settlement"
    CAPTURE = "capture"
    DENY = "deny"
    EXPIRE = "expire"
    CANCEL = "cancel"
    REFUND = "refund"
    PARTIAL_REFUND = "partial_refund"
    CHARGEBACK = "chargeback"
    PARTIAL_CHARGEBACK = "partial_chargeback"


@dataclass
class CustomerDetails:
    """Customer details for payment."""
    customer_id: str
    first_name: str
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = "Indonesia"


@dataclass
class ItemDetail:
    """Item detail for payment."""
    item_id: str
    name: str
    price: int  # in cents/rupiah
    quantity: int = 1
    brand: str = ""
    category: str = ""
    url: str = ""


@dataclass
class TransactionResult:
    """Result from Midtrans API."""
    success: bool
    transaction_id: str = ""
    order_id: str = ""
    snap_token: str = ""
    snap_redirect_url: str = ""
    status_code: str = ""
    status_message: str = ""
    error_message: str = ""
    raw_response: Dict = None


@dataclass
class PaymentNotification:
    """Parsed payment notification from Midtrans."""
    transaction_id: str
    order_id: str
    payment_type: str
    transaction_status: TransactionStatus
    gross_amount: int
    signature_key: str
    status_code: str
    transaction_time: str
    fraud_status: str = ""


# ============================================================================
# MIDTRANS CLIENT
# ============================================================================

class MidtransClient:
    """
    Midtrans Payment Gateway Client.
    Handles Snap API and Core API integration with proper signature verification.
    """
    
    # API Endpoints
    SNAP_BASE_URL = "https://app.midtrans.com/snap/v1"
    CORE_BASE_URL = "https://api.midtrans.com/v2"
    SANDBOX_SNAP_URL = "https://app.sandbox.midtrans.com/snap/v1"
    SANDBOX_CORE_URL = "https://api.sandbox.midtrans.com/v2"
    
    def __init__(self):
        # Load credentials from environment
        self.server_key = os.environ.get("MIDTRANS_SERVER_KEY", "")
        self.client_key = os.environ.get("MIDTRANS_CLIENT_KEY", "")
        self.is_production = os.environ.get("MIDTRANS_IS_PRODUCTION", "false").lower() == "true"
        
        # Set base URLs
        if self.is_production:
            self.snap_url = self.SNAP_BASE_URL
            self.core_url = self.CORE_BASE_URL
        else:
            self.snap_url = self.SANDBOX_SNAP_URL
            self.core_url = self.SANDBOX_CORE_URL
        
        # Validate credentials
        if not self.server_key:
            logger.warning("MIDTRANS_SERVER_KEY not set - running in demo mode")
        
        logger.info(f"MidtransClient initialized (production={self.is_production})")
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header."""
        auth_string = f"{self.server_key}:"
        import base64
        return "Basic " + base64.b64encode(auth_string.encode()).decode()
    
    def _generate_signature_key(
        self,
        order_id: str,
        gross_amount: int,
        server_key: str
    ) -> str:
        """
        Generate signature key for notification verification.
        SHA512(order_id + gross_amount + server_key)
        """
        # Hash: SHA512(order_id + gross_amount + server_key)
        signature_raw = f"{order_id}{gross_amount}{server_key}"
        signature = hashlib.sha512(signature_raw.encode()).hexdigest()
        return signature
    
    def _verify_notification_signature(
        self,
        order_id: str,
        gross_amount: int,
        status_code: str,
        signature_key: str
    ) -> bool:
        """
        Verify Midtrans notification signature.
        
        Signature is calculated as:
        SHA512(status_code + order_id + gross_amount + server_key)
        """
        if not self.server_key:
            logger.warning("Cannot verify signature - server key not set")
            return True  # Allow in demo mode
        
        # Build the string to hash
        signature_raw = f"{status_code}{order_id}{gross_amount}{self.server_key}"
        expected_signature = hashlib.sha512(signature_raw.encode()).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(signature_key, expected_signature)
    
    def create_snap_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer_details: Dict,
        item_details: List[Dict],
        callback_url: str = "",
        expiry_minutes: int = 60
    ) -> TransactionResult:
        """
        Create a Snap payment transaction.
        
        Args:
            order_id: Unique order ID
            gross_amount: Total amount in IDR (integer)
            customer_details: Customer information dict
            item_details: List of item dicts
            callback_url: URL to redirect after payment
            expiry_minutes: Transaction expiry time
        
        Returns:
            TransactionResult with snap token and redirect URL
        """
        if not self.server_key:
            # Demo mode - return mock response
            return TransactionResult(
                success=True,
                order_id=order_id,
                transaction_id=f"TRANSACTION-{order_id}",
                snap_token="DEMO_TOKEN_" + order_id,
                snap_redirect_url=f"https://demo.midtrans.com/{order_id}",
                status_code="201",
                status_message="Success (Demo mode)",
                raw_response={"demo": True}
            )
        
        # Build request body
        transaction_details = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": gross_amount
            },
            "customer_details": customer_details,
            "item_details": item_details,
            "expiry": {
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S +0700"),
                "unit": "minutes",
                "duration": expiry_minutes
            }
        }
        
        if callback_url:
            transaction_details["callbacks"] = {
                "finish": callback_url
            }
        
        # Make API request
        return self._send_snap_request(transaction_details)
    
    def _send_snap_request(self, payload: Dict) -> TransactionResult:
        """Send request to Snap API."""
        try:
            data = json.dumps(payload).encode()
            req = urllib.request.Request(
                f"{self.snap_url}/transactions",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self._get_auth_header()
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                
                return TransactionResult(
                    success=True,
                    transaction_id=result.get("transaction_id", ""),
                    order_id=result.get("order_id", ""),
                    snap_token=result.get("token", ""),
                    snap_redirect_url=result.get("redirect_url", ""),
                    status_code=str(response.status),
                    status_message=result.get("status_message", "Success"),
                    raw_response=result
                )
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            logger.error(f"Midtrans API error: {e.code} - {error_body}")
            
            return TransactionResult(
                success=False,
                order_id=payload.get("transaction_details", {}).get("order_id", ""),
                status_code=str(e.code),
                error_message=error_body
            )
        
        except Exception as e:
            logger.error(f"Midtrans request failed: {e}")
            return TransactionResult(
                success=False,
                error_message=str(e)
            )
    
    def get_transaction_status(self, order_id: str) -> Optional[Dict]:
        """Get transaction status from Core API."""
        if not self.server_key:
            return {"status": "demo", "order_id": order_id}
        
        try:
            url = f"{self.core_url}/{order_id}/status"
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": self._get_auth_header()
                },
                method="GET"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        
        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            return None
    
    def handle_notification(self, notification_payload: Dict) -> PaymentNotification:
        """
        Handle and verify Midtrans webhook notification.
        
        This method:
        1. Verifies the signature key
        2. Parses the notification
        3. Returns a validated PaymentNotification object
        """
        # Extract fields
        transaction_id = notification_payload.get("transaction_id", "")
        order_id = notification_payload.get("order_id", "")
        payment_type = notification_payload.get("payment_type", "")
        status_code = notification_payload.get("status_code", "")
        signature_key = notification_payload.get("signature_key", "")
        gross_amount_str = notification_payload.get("gross_amount", "0")
        transaction_status = notification_payload.get("transaction_status", "pending")
        transaction_time = notification_payload.get("transaction_time", "")
        fraud_status = notification_payload.get("fraud_status", "")
        
        # Convert gross_amount to int
        try:
            gross_amount = int(float(gross_amount_str))
        except (ValueError, TypeError):
            gross_amount = 0
        
        # Verify signature
        is_valid = self._verify_notification_signature(
            order_id=order_id,
            gross_amount=gross_amount,
            status_code=status_code,
            signature_key=signature_key
        )
        
        if not is_valid:
            logger.warning(f"Invalid signature for order {order_id}")
            raise ValueError("Invalid notification signature")
        
        # Parse transaction status
        try:
            tx_status = TransactionStatus(transaction_status)
        except ValueError:
            tx_status = TransactionStatus.PENDING
            logger.warning(f"Unknown transaction status: {transaction_status}")
        
        return PaymentNotification(
            transaction_id=transaction_id,
            order_id=order_id,
            payment_type=payment_type,
            transaction_status=tx_status,
            gross_amount=gross_amount,
            signature_key=signature_key,
            status_code=status_code,
            transaction_time=transaction_time,
            fraud_status=fraud_status
        )
    
    def is_settlement(self, notification: PaymentNotification) -> bool:
        """Check if notification indicates successful settlement."""
        return notification.transaction_status == TransactionStatus.SETTLEMENT
    
    def is_authorized(self, notification: PaymentNotification) -> bool:
        """Check if notification indicates authorized transaction."""
        return notification.transaction_status == TransactionStatus.CAPTURE
    
    def is_pending(self, notification: PaymentNotification) -> bool:
        """Check if transaction is still pending."""
        return notification.transaction_status == TransactionStatus.PENDING
    
    def is_failed(self, notification: PaymentNotification) -> bool:
        """Check if transaction failed."""
        return notification in [
            TransactionStatus.DENY,
            TransactionStatus.EXPIRE,
            TransactionStatus.CANCEL
        ]


# ============================================================================
# PAYMENT QUEUE (Async Handler)
# ============================================================================

class PaymentQueue:
    """
    Queue for processing payment notifications.
    Integrates with Revenue Engine for automatic 60/40 split.
    """
    
    def __init__(self):
        self.pending_payments: Dict[str, PaymentNotification] = {}
        self.processed_payments: Dict[str, PaymentNotification] = {}
    
    def enqueue(self, notification: PaymentNotification):
        """Add notification to queue."""
        self.pending_payments[notification.order_id] = notification
        logger.info(f"Payment enqueued: {notification.order_id}")
    
    def dequeue(self, order_id: str) -> Optional[PaymentNotification]:
        """Remove and return notification from queue."""
        notification = self.pending_payments.pop(order_id, None)
        if notification:
            self.processed_payments[order_id] = notification
        return notification
    
    def get_status(self, order_id: str) -> Optional[PaymentNotification]:
        """Get payment status."""
        return (
            self.pending_payments.get(order_id) or
            self.processed_payments.get(order_id)
        )


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_midtrans_client: Optional[MidtransClient] = None
_payment_queue: Optional[PaymentQueue] = None


def get_midtrans_client() -> MidtransClient:
    """Get or create global Midtrans client."""
    global _midtrans_client
    if _midtrans_client is None:
        _midtrans_client = MidtransClient()
    return _midtrans_client


def get_payment_queue() -> PaymentQueue:
    """Get or create global payment queue."""
    global _payment_queue
    if _payment_queue is None:
        _payment_queue = PaymentQueue()
    return _payment_queue
