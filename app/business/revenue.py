"""
MAHALAKSMI AIOS v1.0 - Volume IV: Revenue Management System
Automated CEO Revenue Share Router & Secure Clearing House
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid

# Import settings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import settings

logger = logging.getLogger(__name__)


class RevenueStatus(Enum):
    """Revenue transaction status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    """Payment methods."""
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"
    QRIS = "qris"
    CRYPTO = "crypto"
    BITCOIN = "bitcoin"


@dataclass
class RevenueTransaction:
    """Revenue transaction record."""
    transaction_id: str
    source: str
    amount: float
    currency: str = "IDR"
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    status: RevenueStatus = RevenueStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Allocation
    gross_amount: float = 0
    ceo_share: float = 0
    operational_share: float = 0
    ceo_share_percentage: float = 60.0
    
    # Transfer details
    recipient_bank: Optional[str] = None
    recipient_account: Optional[str] = None
    recipient_name: Optional[str] = None
    
    # Clearing
    clearing_reference: Optional[str] = None
    cleared_at: Optional[datetime] = None


@dataclass
class DisbursementRequest:
    """CEO disbursement request."""
    request_id: str
    amount: float
    method: PaymentMethod
    recipient_bank: str
    recipient_account: str
    recipient_name: str
    status: str = "pending"
    transaction_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class ClearingHouse:
    """
    Simulated Secure Clearing House Service.
    Handles transaction clearing and settlement.
    """
    
    def __init__(self):
        self.settled_transactions: List[str] = []
        logger.info("Clearing House initialized")
    
    async def settle(self, transaction: RevenueTransaction) -> bool:
        """
        Settle a transaction through clearing house.
        Simulates clearing process.
        """
        await asyncio.sleep(0.1)  # Simulate processing
        
        transaction.clearing_reference = f"CLR-{uuid.uuid4().hex[:12].upper()}"
        transaction.cleared_at = datetime.now()
        transaction.status = RevenueStatus.COMPLETED
        
        self.settled_transactions.append(transaction.transaction_id)
        
        logger.info(f"Transaction settled: {transaction.transaction_id}")
        return True
    
    def get_settlement_report(self) -> Dict:
        """Get settlement report."""
        return {
            "total_settled": len(self.settled_transactions),
            "settlement_ids": self.settled_transactions[-10:]
        }


class RevenueManager:
    """
    Automated CEO Revenue Management Router.
    Handles revenue streams and CEO share distribution.
    """
    
    def __init__(self):
        self.transactions: Dict[str, RevenueTransaction] = {}
        self.disbursements: Dict[str, DisbursementRequest] = {}
        self.clearing_house = ClearingHouse()
        
        # Configuration
        self.ceo_share_percentage = settings.ceo_share_percentage
        self.operational_percentage = settings.operational_reserve_percentage
        
        # CEO Bank Details
        self.ceo_bank = {
            "bank_code": settings.ceo_bank_code,
            "account_number": settings.ceo_account_number,
            "account_holder": settings.ceo_account_holder,
            "bank_name": "Bank Central Asia"
        }
        
        logger.info(f"Revenue Manager initialized - CEO Share: {self.ceo_share_percentage}%")
    
    def calculate_allocation(self, gross_amount: float) -> Dict[str, float]:
        """Calculate revenue allocation."""
        ceo_share = gross_amount * (self.ceo_share_percentage / 100)
        operational = gross_amount * (self.operational_percentage / 100)
        
        return {
            "gross_amount": gross_amount,
            "ceo_share": ceo_share,
            "operational_share": operational,
            "ceo_percentage": self.ceo_share_percentage,
            "operational_percentage": self.operational_percentage
        }
    
    async def record_digital_revenue(
        self,
        source: str,
        amount: float,
        payment_method: str = "bank_transfer",
        metadata: Dict = None
    ) -> RevenueTransaction:
        """Record incoming digital revenue."""
        transaction_id = f"REV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Determine payment method
        pm = PaymentMethod.BANK_TRANSFER
        if payment_method.lower() in ["qris", "qris"]:
            pm = PaymentMethod.QRIS
        elif payment_method.lower() in ["ewallet", "e-wallet"]:
            pm = PaymentMethod.E_WALLET
        elif payment_method.lower() in ["crypto", "bitcoin", "btc"]:
            pm = PaymentMethod.BITCOIN
        
        # Calculate allocation
        allocation = self.calculate_allocation(amount)
        
        transaction = RevenueTransaction(
            transaction_id=transaction_id,
            source=source,
            amount=amount,
            payment_method=pm,
            gross_amount=allocation["gross_amount"],
            ceo_share=allocation["ceo_share"],
            operational_share=allocation["operational_share"],
            ceo_share_percentage=allocation["ceo_percentage"],
            recipient_bank=self.ceo_bank["bank_code"],
            recipient_account=self.ceo_bank["account_number"],
            recipient_name=self.ceo_bank["account_holder"],
            metadata=metadata or {}
        )
        
        self.transactions[transaction_id] = transaction
        
        # Auto-settle through clearing house
        await self.clearing_house.settle(transaction)
        
        logger.info(f"Revenue recorded: {transaction_id} - Rp {amount:,.0f}")
        return transaction
    
    async def request_ceo_disbursement(
        self,
        amount: float,
        method: str = "bank_transfer"
    ) -> DisbursementRequest:
        """Request CEO disbursement transfer."""
        request_id = f"DIS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Validate amount against available CEO share
        available = self.get_available_ceo_share()
        if amount > available:
            logger.warning(f"Disbursement exceeds available: {amount} > {available}")
        
        pm = PaymentMethod.BANK_TRANSFER
        if method.lower() == "bitcoin":
            pm = PaymentMethod.BITCOIN
        
        request = DisbursementRequest(
            request_id=request_id,
            amount=amount,
            method=pm,
            recipient_bank=self.ceo_bank["bank_code"],
            recipient_account=self.ceo_bank["account_number"],
            recipient_name=self.ceo_bank["account_holder"]
        )
        
        self.disbursements[request_id] = request
        
        # Simulate disbursement processing
        await self._process_disbursement(request)
        
        logger.info(f"Disbursement requested: {request_id} - Rp {amount:,.0f}")
        return request
    
    async def _process_disbursement(self, request: DisbursementRequest) -> None:
        """Process disbursement through clearing."""
        await asyncio.sleep(0.2)  # Simulate API call
        
        request.status = "completed"
        request.completed_at = datetime.now()
        request.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        logger.info(f"Disbursement completed: {request.request_id}")
    
    def get_available_ceo_share(self) -> float:
        """Get available CEO share balance."""
        total_ceo = sum(t.ceo_share for t in self.transactions.values() if t.status == RevenueStatus.COMPLETED)
        disbursed = sum(d.amount for d in self.disbursements.values() if d.status == "completed")
        return total_ceo - disbursed
    
    def get_total_revenue(self) -> float:
        """Get total recorded revenue."""
        return sum(t.amount for t in self.transactions.values())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get revenue summary."""
        total_revenue = self.get_total_revenue()
        allocation = self.calculate_allocation(total_revenue)
        available_ceo = self.get_available_ceo_share()
        
        completed_disbursements = [d for d in self.disbursements.values() if d.status == "completed"]
        
        return {
            "total_revenue": total_revenue,
            "total_transactions": len(self.transactions),
            "allocation": allocation,
            "ceo_account": {
                "bank": self.ceo_bank["bank_name"],
                "account": self.ceo_bank["account_number"],
                "holder": self.ceo_bank["account_holder"]
            },
            "disbursement": {
                "available": available_ceo,
                "total_disbursed": sum(d.amount for d in completed_disbursements),
                "pending_requests": sum(1 for d in self.disbursements.values() if d.status == "pending")
            },
            "recent_transactions": [
                {
                    "id": t.transaction_id,
                    "source": t.source,
                    "amount": t.amount,
                    "status": t.status.value,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in list(self.transactions.values())[-5:]
            ]
        }

    # =========================================================================
    # MIDTRANS PAYMENT INTEGRATION
    # =========================================================================

    async def create_payment_order(
        self,
        order_id: str,
        gross_amount: float,
        customer_details: Dict,
        item_details: List[Dict],
        source: str = "midtrans"
    ) -> Dict[str, Any]:
        """
        Create a Midtrans payment order.
        
        Args:
            order_id: Unique order ID
            gross_amount: Total amount in IDR
            customer_details: Customer information
            item_details: List of items
            source: Revenue source
        
        Returns:
            Dict with snap_token and redirect_url
        """
        from app.business.midtrans_client import get_midtrans_client
        
        midtrans = get_midtrans_client()
        
        # Create Snap transaction
        result = midtrans.create_snap_transaction(
            order_id=order_id,
            gross_amount=int(gross_amount),
            customer_details=customer_details,
            item_details=item_details
        )
        
        if result.success:
            # Create pending transaction
            transaction_id = f"REV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            allocation = self.calculate_allocation(gross_amount)
            
            transaction = RevenueTransaction(
                transaction_id=transaction_id,
                source=source,
                amount=gross_amount,
                payment_method=PaymentMethod.QRIS,
                status=RevenueStatus.PENDING,
                gross_amount=allocation["gross_amount"],
                ceo_share=allocation["ceo_share"],
                operational_share=allocation["operational_share"],
                ceo_share_percentage=allocation["ceo_percentage"],
                recipient_bank=self.ceo_bank["bank_code"],
                recipient_account=self.ceo_bank["account_number"],
                recipient_name=self.ceo_bank["account_holder"],
                metadata={
                    "order_id": order_id,
                    "midtrans_transaction_id": result.transaction_id,
                    "snap_token": result.snap_token
                }
            )
            
            self.transactions[transaction_id] = transaction
            
            logger.info(f"Payment order created: {order_id} - Rp {gross_amount:,.0f}")
            
            return {
                "success": True,
                "order_id": order_id,
                "transaction_id": transaction_id,
                "snap_token": result.snap_token,
                "redirect_url": result.snap_redirect_url,
                "status": "pending"
            }
        
        return {
            "success": False,
            "order_id": order_id,
            "error": result.error_message
        }

    async def handle_payment_settlement(
        self,
        order_id: str,
        gross_amount: float,
        transaction_id: str,
        payment_type: str,
        transaction_time: str = ""
    ) -> RevenueTransaction:
        """
        Handle successful payment settlement from Midtrans.
        
        This method:
        1. Updates transaction status to COMPLETED
        2. Records the 60/40 CEO split in ledger
        3. Logs the transaction
        
        Args:
            order_id: Midtrans order ID
            gross_amount: Settled amount
            transaction_id: Midtrans transaction ID
            payment_type: Payment method used
            transaction_time: Transaction timestamp
        
        Returns:
            Updated RevenueTransaction
        """
        # Find transaction by order_id
        transaction = None
        for t in self.transactions.values():
            if t.metadata.get("order_id") == order_id:
                transaction = t
                break
        
        if not transaction:
            # Create new transaction if not found
            transaction_id_new = f"REV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            allocation = self.calculate_allocation(gross_amount)
            
            transaction = RevenueTransaction(
                transaction_id=transaction_id_new,
                source="midtrans",
                amount=gross_amount,
                payment_method=PaymentMethod.QRIS if payment_type == "qris" else PaymentMethod.BANK_TRANSFER,
                status=RevenueStatus.PENDING,
                gross_amount=allocation["gross_amount"],
                ceo_share=allocation["ceo_share"],
                operational_share=allocation["operational_share"],
                ceo_share_percentage=allocation["ceo_percentage"],
                recipient_bank=self.ceo_bank["bank_code"],
                recipient_account=self.ceo_bank["account_number"],
                recipient_name=self.ceo_bank["account_holder"],
                metadata={
                    "order_id": order_id,
                    "midtrans_transaction_id": transaction_id,
                    "payment_type": payment_type,
                    "transaction_time": transaction_time
                }
            )
            
            self.transactions[transaction.transaction_id] = transaction
        
        # Update to completed
        transaction.status = RevenueStatus.COMPLETED
        transaction.cleared_at = datetime.now()
        
        # Auto-settle through clearing house
        await self.clearing_house.settle(transaction)
        
        logger.info(
            f"Payment settled: {order_id} - Rp {gross_amount:,.0f} "
            f"(CEO: Rp {transaction.ceo_share:,.0f} / Ops: Rp {transaction.operational_share:,.0f})"
        )
        
        return transaction

    def get_transaction_by_order_id(self, order_id: str) -> Optional[RevenueTransaction]:
        """Get transaction by Midtrans order ID."""
        for t in self.transactions.values():
            if t.metadata.get("order_id") == order_id:
                return t
        return None

    def cancel_pending_payment(self, order_id: str) -> bool:
        """Cancel a pending payment order."""
        transaction = self.get_transaction_by_order_id(order_id)
        if transaction and transaction.status == RevenueStatus.PENDING:
            transaction.status = RevenueStatus.CANCELLED
            logger.info(f"Payment cancelled: {order_id}")
            return True
        return False


# Global revenue manager
_revenue_manager: Optional[RevenueManager] = None


def get_revenue_manager() -> RevenueManager:
    """Get or create global revenue manager."""
    global _revenue_manager
    if _revenue_manager is None:
        _revenue_manager = RevenueManager()
    return _revenue_manager
