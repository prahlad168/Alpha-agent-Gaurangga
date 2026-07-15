"""
MAHALAKSMI AIOS v1.0 - Volume IV: Finance & Ledger System
Automated bookkeeping routines tracking runtime costs vs revenue
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Transaction types."""
    REVENUE = "revenue"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    FEE = "fee"


class Category(Enum):
    """Finance categories."""
    DIGITAL_PRODUCTS = "digital_products"
    SERVICES = "services"
    OPERATIONS = "operations"
    INFRASTRUCTURE = "infrastructure"
    MARKETING = "marketing"
    PAYOUT = "payout"


@dataclass
class LedgerEntry:
    """Ledger entry record."""
    entry_id: str
    transaction_type: TransactionType
    category: Category
    amount: float
    description: str
    currency: str = "IDR"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    balance_after: float = 0


@dataclass
class CostRecord:
    """Runtime cost record."""
    cost_id: str
    service: str
    amount: float
    period: str  # e.g., "2026-07"
    currency: str = "IDR"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FinanceLedger:
    """
    Automated ledger bookkeeping system.
    Tracks all financial transactions and runtime costs.
    """
    
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.costs: List[CostRecord] = []
        self._balance = 0.0
        self._entry_counter = 0
        
        # Initialize with current period
        self.current_period = datetime.now().strftime("%Y-%m")
        
        logger.info("Finance Ledger initialized")
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID."""
        self._entry_counter += 1
        return f"LED-{datetime.now().strftime('%Y%m%d')}-{self._entry_counter:04d}"
    
    def add_entry(
        self,
        transaction_type: TransactionType,
        category: Category,
        amount: float,
        description: str,
        metadata: Dict = None
    ) -> LedgerEntry:
        """Add ledger entry."""
        # Update balance
        if transaction_type in [TransactionType.REVENUE, TransactionType.TRANSFER]:
            self._balance += amount
        else:
            self._balance -= amount
        
        entry = LedgerEntry(
            entry_id=self._generate_entry_id(),
            transaction_type=transaction_type,
            category=category,
            amount=amount,
            description=description,
            metadata=metadata or {},
            balance_after=self._balance
        )
        
        self.entries.append(entry)
        logger.info(f"Ledger entry: {entry.entry_id} - {transaction_type.value} - {amount}")
        
        return entry
    
    def record_cost(
        self,
        service: str,
        amount: float,
        period: str = None,
        metadata: Dict = None
    ) -> CostRecord:
        """Record runtime cost."""
        if period is None:
            period = self.current_period
        
        cost = CostRecord(
            cost_id=f"COST-{len(self.costs) + 1:04d}",
            service=service,
            amount=amount,
            period=period,
            metadata=metadata or {}
        )
        
        self.costs.append(cost)
        
        # Also add to ledger as expense
        self.add_entry(
            TransactionType.EXPENSE,
            Category.INFRASTRUCTURE,
            amount,
            f"Runtime cost: {service}",
            {"cost_id": cost.cost_id}
        )
        
        return cost
    
    def get_balance(self) -> float:
        """Get current balance."""
        return self._balance
    
    def get_summary(self, period: str = None) -> Dict[str, Any]:
        """Get financial summary."""
        if period is None:
            period = self.current_period
        
        # Filter entries by period
        period_entries = [
            e for e in self.entries
            if e.timestamp.strftime("%Y-%m") == period
        ]
        
        # Calculate totals by category
        by_category = defaultdict(float)
        for entry in period_entries:
            if entry.transaction_type == TransactionType.REVENUE:
                by_category[entry.category.value] += entry.amount
            elif entry.transaction_type == TransactionType.EXPENSE:
                by_category[entry.category.value] -= entry.amount
        
        # Calculate totals
        total_revenue = sum(
            e.amount for e in period_entries
            if e.transaction_type == TransactionType.REVENUE
        )
        total_expenses = sum(
            e.amount for e in period_entries
            if e.transaction_type == TransactionType.EXPENSE
        )
        
        # Get period costs
        period_costs = [c for c in self.costs if c.period == period]
        total_costs = sum(c.amount for c in period_costs)
        
        return {
            "period": period,
            "balance": self._balance,
            "income": {
                "total": total_revenue,
                "by_category": dict(by_category)
            },
            "expenses": {
                "total": total_expenses,
                "runtime_costs": total_costs
            },
            "profit": total_revenue - total_expenses,
            "profit_margin": ((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0,
            "transaction_count": len(period_entries),
            "recent_entries": [
                {
                    "id": e.entry_id,
                    "type": e.transaction_type.value,
                    "category": e.category.value,
                    "amount": e.amount,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in period_entries[-10:]
            ]
        }
    
    def get_ledger_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Generate detailed ledger report."""
        entries = self.entries
        
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]
        
        return {
            "report_period": {
                "start": start_date.isoformat() if start_date else self.entries[0].timestamp.isoformat() if self.entries else None,
                "end": end_date.isoformat() if end_date else datetime.now().isoformat()
            },
            "entries": [
                {
                    "id": e.entry_id,
                    "type": e.transaction_type.value,
                    "category": e.category.value,
                    "amount": e.amount,
                    "balance_after": e.balance_after,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in entries
            ],
            "summary": {
                "total_entries": len(entries),
                "opening_balance": entries[0].balance_after - entries[0].amount if entries else 0,
                "closing_balance": entries[-1].balance_after if entries else 0
            }
        }


# Global finance ledger
_finance_ledger: Optional[FinanceLedger] = None


def get_finance_ledger() -> FinanceLedger:
    """Get or create global finance ledger."""
    global _finance_ledger
    if _finance_ledger is None:
        _finance_ledger = FinanceLedger()
    return _finance_ledger
