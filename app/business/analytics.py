"""
MAHALAKSMI AIOS v1.0 - Volume IV Chapter 40: Analytics Center
Business intelligence and metrics aggregation from Finance Ledger
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

# Import finance components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.business.finance import get_finance_ledger, TransactionType, Category
from app.business.revenue import get_revenue_manager

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RevenueMetrics:
    """Revenue analytics metrics."""
    total_gross_revenue: float = 0.0
    total_net_revenue: float = 0.0
    total_expenses: float = 0.0
    net_profit: float = 0.0
    profit_margin: float = 0.0
    transaction_count: int = 0
    
    # CEO vs Operational
    ceo_share_total: float = 0.0
    operational_share_total: float = 0.0
    ceo_share_percentage: float = 60.0
    operational_share_percentage: float = 40.0


@dataclass
class GrowthMetrics:
    """Growth velocity analytics."""
    period_over_period_growth: float = 0.0  # percentage
    monthly_recurring_revenue: float = 0.0
    average_transaction_value: float = 0.0
    growth_velocity: float = 0.0  # monthly growth rate
    
    # Projections
    projected_revenue_30d: float = 0.0
    projected_revenue_90d: float = 0.0


@dataclass
class BurnRateMetrics:
    """Burn rate and runway analytics."""
    monthly_burn_rate: float = 0.0
    monthly_revenue_run_rate: float = 0.0
    runway_months: float = 0.0
    operational_costs: float = 0.0
    infrastructure_costs: float = 0.0
    marketing_costs: float = 0.0
    
    # Projections
    projected_burn_30d: float = 0.0
    projected_burn_90d: float = 0.0


@dataclass
class DistributionBreakdown:
    """60/40 Distribution breakdown."""
    total_revenue: float = 0.0
    ceo_share: float = 0.0
    ceo_share_percentage: float = 60.0
    ceo_bank: str = "BCA"
    ceo_account: str = "6485086645"
    ceo_holder: str = "I Made Purna Ananda"
    
    operational_reserve: float = 0.0
    operational_percentage: float = 40.0
    
    # Allocation details
    reinvestment_allocated: float = 0.0
    team_bonus_allocated: float = 0.0
    csr_allocated: float = 0.0


@dataclass
class AnalyticsSummary:
    """Complete analytics summary."""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    period_start: str = ""
    period_end: str = ""
    
    revenue: RevenueMetrics = field(default_factory=RevenueMetrics)
    growth: GrowthMetrics = field(default_factory=GrowthMetrics)
    burn_rate: BurnRateMetrics = field(default_factory=BurnRateMetrics)
    distribution: DistributionBreakdown = field(default_factory=DistributionBreakdown)
    
    recent_transactions: List[Dict] = field(default_factory=list)
    top_revenue_sources: List[Dict] = field(default_factory=list)


# ============================================================================
# ANALYTICS ENGINE
# ============================================================================

class AnalyticsCenter:
    """
    Business Analytics Center for MAHALAKSMI AIOS.
    Aggregates financial data and generates operational metrics.
    """
    
    def __init__(self):
        self.finance = get_finance_ledger()
        self.revenue = get_revenue_manager()
        
        # Configuration
        self.ceo_share_pct = 60.0
        self.operational_pct = 40.0
        
        # Operational allocation breakdown (40%)
        self.reinvestment_pct = 25.0  # 10% of total
        self.team_bonus_pct = 10.0    # 4% of total
        self.csr_pct = 5.0           # 2% of total
        
        logger.info("Analytics Center initialized")
    
    def calculate_revenue_metrics(self) -> RevenueMetrics:
        """Calculate comprehensive revenue metrics."""
        summary = self.finance.get_summary()
        revenue_summary = self.revenue.get_summary()
        
        metrics = RevenueMetrics(
            total_gross_revenue=revenue_summary.get("total_revenue", 0),
            total_net_revenue=summary.get("income", {}).get("total", 0),
            total_expenses=abs(summary.get("expenses", {}).get("total", 0)),
            net_profit=summary.get("profit", 0),
            profit_margin=summary.get("profit_margin", 0),
            transaction_count=revenue_summary.get("total_transactions", 0),
            ceo_share_total=revenue_summary.get("allocation", {}).get("ceo_share", 0),
            operational_share_total=revenue_summary.get("allocation", {}).get("operational_share", 0),
            ceo_share_percentage=self.ceo_share_pct,
            operational_share_percentage=self.operational_pct
        )
        
        return metrics
    
    def calculate_growth_metrics(self, history_days: int = 30) -> GrowthMetrics:
        """Calculate growth velocity and projections."""
        # Get recent transactions
        recent_entries = self.finance.entries[-100:] if self.finance.entries else []
        
        if not recent_entries:
            return GrowthMetrics()
        
        # Calculate average transaction value
        revenue_entries = [
            e for e in recent_entries 
            if e.transaction_type == TransactionType.REVENUE
        ]
        
        total_revenue = sum(e.amount for e in revenue_entries)
        avg_transaction = total_revenue / max(len(revenue_entries), 1)
        
        # Calculate daily revenue rate
        days_with_data = 1
        if len(revenue_entries) >= 2:
            first_date = datetime.fromisoformat(revenue_entries[0].timestamp.isoformat())
            last_date = datetime.fromisoformat(revenue_entries[-1].timestamp.isoformat())
            days_with_data = max((last_date - first_date).days, 1)
        
        daily_rate = total_revenue / days_with_data
        
        # Growth velocity (monthly projected)
        monthly_run_rate = daily_rate * 30
        
        # Simple projection based on current rate
        projected_30d = daily_rate * 30
        projected_90d = daily_rate * 90
        
        # Period-over-period growth (simplified)
        half_point = len(revenue_entries) // 2
        if half_point > 0:
            first_half = sum(e.amount for e in revenue_entries[:half_point])
            second_half = sum(e.amount for e in revenue_entries[half_point:])
            
            if first_half > 0:
                pop_growth = ((second_half - first_half) / first_half) * 100
            else:
                pop_growth = 0.0
        else:
            pop_growth = 0.0
        
        return GrowthMetrics(
            period_over_period_growth=pop_growth,
            monthly_recurring_revenue=monthly_run_rate,
            average_transaction_value=avg_transaction,
            growth_velocity=pop_growth / max(days_with_data / 30, 1),
            projected_revenue_30d=projected_30d,
            projected_revenue_90d=projected_90d
        )
    
    def calculate_burn_rate(self) -> BurnRateMetrics:
        """Calculate burn rate and runway."""
        summary = self.finance.get_summary()
        
        # Get expense breakdown by category
        expenses_by_category = summary.get("income", {}).get("by_category", {})
        
        operational_costs = abs(expenses_by_category.get("operations", 0))
        infrastructure_costs = abs(expenses_by_category.get("infrastructure", 0))
        marketing_costs = abs(expenses_by_category.get("marketing", 0))
        
        total_burn = operational_costs + infrastructure_costs + marketing_costs
        
        # Monthly revenue rate
        total_revenue = summary.get("income", {}).get("total", 0)
        monthly_revenue = total_revenue  # Simplified
        
        # Runway calculation
        if total_burn > 0:
            runway = total_revenue / total_burn if total_revenue > 0 else float('inf')
        else:
            runway = float('inf')
        
        return BurnRateMetrics(
            monthly_burn_rate=total_burn,
            monthly_revenue_run_rate=monthly_revenue,
            runway_months=min(runway, 999),
            operational_costs=operational_costs,
            infrastructure_costs=infrastructure_costs,
            marketing_costs=marketing_costs,
            projected_burn_30d=total_burn,
            projected_burn_90d=total_burn * 3
        )
    
    def calculate_distribution(self) -> DistributionBreakdown:
        """Calculate 60/40 CEO vs Operational distribution."""
        summary = self.revenue.get_summary()
        
        total = summary.get("total_revenue", 0)
        ceo_share = summary.get("allocation", {}).get("ceo_share", 0)
        operational = summary.get("allocation", {}).get("operational_share", 0)
        
        # Calculate sub-allocations from operational (40%)
        reinvestment = operational * (self.reinvestment_pct / 100)
        team_bonus = operational * (self.team_bonus_pct / 100)
        csr = operational * (self.csr_pct / 100)
        
        return DistributionBreakdown(
            total_revenue=total,
            ceo_share=ceo_share,
            ceo_share_percentage=self.ceo_share_pct,
            operational_reserve=operational,
            operational_percentage=self.operational_pct,
            reinvestment_allocated=reinvestment,
            team_bonus_allocated=team_bonus,
            csr_allocated=csr
        )
    
    def get_top_sources(self, limit: int = 5) -> List[Dict]:
        """Get top revenue sources."""
        summary = self.revenue.get_summary()
        transactions = summary.get("recent_transactions", [])
        
        # Aggregate by source
        source_totals = defaultdict(float)
        for txn in transactions:
            source = txn.get("source", "unknown")
            source_totals[source] += txn.get("amount", 0)
        
        # Sort and limit
        sorted_sources = sorted(
            source_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"source": source, "total": amount, "percentage": (amount / max(summary.get("total_revenue", 1), 1)) * 100}
            for source, amount in sorted_sources
        ]
    
    def generate_summary(self, period_days: int = 30) -> AnalyticsSummary:
        """Generate complete analytics summary."""
        logger.info("Generating analytics summary...")
        
        summary = AnalyticsSummary(
            period_start=(datetime.now() - timedelta(days=period_days)).isoformat(),
            period_end=datetime.now().isoformat()
        )
        
        # Calculate all metrics
        summary.revenue = self.calculate_revenue_metrics()
        summary.growth = self.calculate_growth_metrics(period_days)
        summary.burn_rate = self.calculate_burn_rate()
        summary.distribution = self.calculate_distribution()
        
        # Add recent transactions
        finance_summary = self.finance.get_summary()
        summary.recent_transactions = finance_summary.get("recent_entries", [])[:10]
        
        # Add top sources
        summary.top_revenue_sources = self.get_top_sources()
        
        logger.info(f"Analytics generated: Total Revenue Rp {summary.revenue.total_gross_revenue:,.0f}")
        
        return summary
    
    def get_summary_json(self) -> Dict[str, Any]:
        """Get summary as JSON-serializable dict."""
        summary = self.generate_summary()
        
        return {
            "generated_at": summary.generated_at,
            "period": {
                "start": summary.period_start,
                "end": summary.period_end
            },
            "revenue_metrics": {
                "total_gross_revenue": summary.revenue.total_gross_revenue,
                "total_expenses": summary.revenue.total_expenses,
                "net_profit": summary.revenue.net_profit,
                "profit_margin_percent": round(summary.revenue.profit_margin, 2),
                "transaction_count": summary.revenue.transaction_count
            },
            "growth_metrics": {
                "period_over_period_growth_percent": round(summary.growth.period_over_period_growth, 2),
                "monthly_recurring_revenue": summary.growth.monthly_recurring_revenue,
                "average_transaction_value": summary.growth.average_transaction_value,
                "projected_revenue_30d": summary.growth.projected_revenue_30d,
                "projected_revenue_90d": summary.growth.projected_revenue_90d
            },
            "burn_rate_metrics": {
                "monthly_burn_rate": summary.burn_rate.monthly_burn_rate,
                "monthly_revenue_run_rate": summary.burn_rate.monthly_revenue_run_rate,
                "runway_months": round(summary.burn_rate.runway_months, 1),
                "operational_costs": summary.burn_rate.operational_costs,
                "infrastructure_costs": summary.burn_rate.infrastructure_costs,
                "marketing_costs": summary.burn_rate.marketing_costs
            },
            "distribution_breakdown": {
                "total_revenue": summary.distribution.total_revenue,
                "ceo_share": {
                    "amount": summary.distribution.ceo_share,
                    "percentage": summary.distribution.ceo_share_percentage,
                    "bank": summary.distribution.ceo_bank,
                    "account": summary.distribution.ceo_account,
                    "holder": summary.distribution.ceo_holder
                },
                "operational_reserve": {
                    "amount": summary.distribution.operational_reserve,
                    "percentage": summary.distribution.operational_percentage,
                    "breakdown": {
                        "reinvestment": summary.distribution.reinvestment_allocated,
                        "team_bonus": summary.distribution.team_bonus_allocated,
                        "csr": summary.distribution.csr_allocated
                    }
                }
            },
            "top_revenue_sources": summary.top_revenue_sources,
            "recent_transactions": [
                {
                    "id": t.get("id"),
                    "type": t.get("type"),
                    "amount": t.get("amount"),
                    "description": t.get("description"),
                    "timestamp": t.get("timestamp")
                }
                for t in summary.recent_transactions
            ]
        }


# Global analytics instance
_analytics: Optional[AnalyticsCenter] = None


def get_analytics() -> AnalyticsCenter:
    """Get or create global analytics instance."""
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsCenter()
    return _analytics
