#!/usr/bin/env python3
"""
ML-EAOS v12.0 - Knowledge Management System
Phase 26: Architecture, SOP, documentation, troubleshooting, procedures

Usage:
    python knowledge_management.py
    python knowledge_management.py --search "query"
    python knowledge_management.py --update
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class KnowledgeArticle:
    id: str
    title: str
    category: str
    tags: List[str]
    content: str
    author: str
    created: str
    updated: str
    version: str
    status: str  # draft, published, archived

class KnowledgeManagementSystem:
    """
    Knowledge Management System for MAHA LAKSHMI CORP
    
    Maintains structured knowledge base:
    - Architecture
    - SOP
    - Documentation
    - Troubleshooting
    - Procedures
    - Product standards
    - Decision history
    """
    
    def __init__(self):
        self.kb_dir = "ml-eaos-data/knowledge-base"
        self.articles_file = f"{self.kb_dir}/articles.json"
        self._ensure_directories()
        self.articles = self._load_articles()
    
    def _ensure_directories(self):
        os.makedirs(self.kb_dir, exist_ok=True)
    
    def _load_articles(self) -> List[Dict]:
        if os.path.exists(self.articles_file):
            with open(self.articles_file) as f:
                return json.load(f)
        return []
    
    def _save_articles(self):
        with open(self.articles_file, 'w') as f:
            json.dump(self.articles, f, indent=2)
    
    def create_architecture_kb(self) -> KnowledgeArticle:
        """Create architecture knowledge base article."""
        return KnowledgeArticle(
            id="KB-ARCH-001",
            title="System Architecture Overview",
            category="Architecture",
            tags=["architecture", "system", "overview"],
            content="""
# System Architecture Overview

## Components

### Product Factory
- Location: product-factory/
- Purpose: Generate digital products
- Output: Ebooks, templates, prompts, printables

### Commerce Platform
- Location: commerce/
- Purpose: Order processing
- Integrations: Midtrans, Stripe, PayPal

### Marketplace Hub
- Location: marketplaces/
- Purpose: Multi-platform selling
- Supported: Etsy, Gumroad, Tokopedia

### Finance Engine
- Location: finance/
- Purpose: Revenue tracking, CEO payouts
- CEO Share: 80% of NET PROFIT
- Wallet: 0xc157ee1aa61f9ca5672061cdff9f8be20a283114

## Data Flow

1. Product Created → Product Factory
2. Product Published → Marketplace Hub
3. Sale Made → Commerce Platform
4. Payment Received → Finance Engine
5. Revenue Calculated → CEO Payout Triggered
6. Validation Passed → Transfer to CEO Wallet
""",
            author="AI Engineering Team",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            version="1.0",
            status="published"
        )
    
    def create_sop_kb(self, name: str, steps: List[str]) -> KnowledgeArticle:
        """Create SOP knowledge base article."""
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        
        return KnowledgeArticle(
            id=f"KB-SOP-{datetime.now().strftime('%Y%m%d')}",
            title=f"Standard Operating Procedure: {name}",
            category="SOP",
            tags=["sop", name.lower().replace(" ", "-")],
            content=f"# SOP: {name}\n\n## Steps\n\n{steps_text}",
            author="Operations Team",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            version="1.0",
            status="published"
        )
    
    def create_troubleshooting_kb(self, problem: str, solution: str, category: str) -> KnowledgeArticle:
        """Create troubleshooting knowledge base article."""
        return KnowledgeArticle(
            id=f"KB-TS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title=f"Troubleshooting: {problem}",
            category="Troubleshooting",
            tags=["troubleshooting", category.lower(), problem.lower().replace(" ", "-")[:20]],
            content=f"# Problem\n\n{problem}\n\n# Solution\n\n{solution}",
            author="Support Team",
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            version="1.0",
            status="published"
        )
    
    def search(self, query: str) -> List[Dict]:
        """Search knowledge base."""
        query_lower = query.lower()
        results = []
        
        for article in self.articles:
            if (query_lower in article['title'].lower() or
                query_lower in article['content'].lower() or
                any(query_lower in tag.lower() for tag in article['tags'])):
                results.append(article)
        
        return results
    
    def get_category_tree(self) -> Dict:
        """Get knowledge base category tree."""
        categories = {}
        
        for article in self.articles:
            cat = article['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                'id': article['id'],
                'title': article['title'],
                'status': article['status']
            })
        
        return categories
    
    def generate_report(self) -> Dict:
        """Generate knowledge base status report."""
        total = len(self.articles)
        by_category = {}
        by_status = {}
        
        for article in self.articles:
            cat = article['category']
            status = article['status']
            
            by_category[cat] = by_category.get(cat, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_articles": total,
            "by_category": by_category,
            "by_status": by_status,
            "recent_articles": self.articles[-5:] if len(self.articles) >= 5 else self.articles
        }
    
    def initialize_default_articles(self):
        """Initialize with default knowledge base articles."""
        if self.articles:
            return
        
        # Architecture
        self.articles.append(asdict(self.create_architecture_kb()))
        
        # SOPs
        self.articles.append(asdict(self.create_sop_kb(
            "Product Launch",
            [
                "Generate product using Product Factory",
                "QA review the output",
                "Create metadata and SEO",
                "Publish to Marketplace Hub",
                "Announce on social media",
                "Monitor sales and feedback"
            ]
        )))
        
        self.articles.append(asdict(self.create_sop_kb(
            "CEO Payout",
            [
                "Verify all transactions are settled",
                "Check no pending refunds",
                "Confirm balance sufficient",
                "Validate wallet address",
                "Execute payout via blockchain",
                "Log transaction in audit trail"
            ]
        )))
        
        # Troubleshooting
        self.articles.append(asdict(self.create_troubleshooting_kb(
            "Download not working",
            "1. Clear browser cache\n2. Try different browser\n3. Disable VPN\n4. Contact support if persists",
            "Technical"
        )))
        
        self._save_articles()
    
    def print_report(self, report: Dict):
        """Print report summary."""
        print("\n" + "="*70)
        print("📚 KNOWLEDGE MANAGEMENT REPORT")
        print("="*70)
        print(f"Generated: {report['timestamp']}\n")
        
        print(f"Total Articles: {report['total_articles']}\n")
        
        print("By Category:")
        for cat, count in report['by_category'].items():
            print(f"  📁 {cat}: {count}")
        
        print("\nBy Status:")
        for status, count in report['by_status'].items():
            print(f"  {'✅' if status == 'published' else '📝'} {status}: {count}")
        
        print("\nRecent Articles:")
        for article in report['recent_articles'][-5:]:
            print(f"  • {article['title']} ({article['category']})")

def main():
    print("\n" + "="*70)
    print("  ML-EAOS v12.0 - KNOWLEDGE MANAGEMENT SYSTEM")
    print("  Phase 26: Structured Knowledge Base")
    print("="*70 + "\n")
    
    kms = KnowledgeManagementSystem()
    kms.initialize_default_articles()
    
    report = kms.generate_report()
    kms.print_report(report)
    
    # Demo search
    print("\n\n🔍 Search Demo:")
    results = kms.search("payout")
    print(f"  Found {len(results)} articles for 'payout'")

if __name__ == "__main__":
    main()
