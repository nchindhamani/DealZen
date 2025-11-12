"""
DealZen Automated Quality Validation System
Industry-standard quality scoring with automated decision-making.
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from validation_config import (
    QUALITY_THRESHOLDS, SCORING_WEIGHTS, VALIDATION_RULES, 
    CRITICAL_FIELDS, LOGGING
)


class QualityValidator:
    """
    Automated quality validation with scoring system.
    No manual intervention required for most cases.
    """
    
    def __init__(self, deals_file='scripts/deals.json'):
        self.deals_file = deals_file
        self.deals = []
        self.score = 0
        self.score_breakdown = {}
        self.errors = []
        self.warnings = []
        self.info = {}
        
    def load_deals(self):
        """Load and parse deals JSON"""
        try:
            with open(self.deals_file, 'r') as f:
                self.deals = json.load(f)
            return True
        except FileNotFoundError:
            self.errors.append(f"Deals file not found: {self.deals_file}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {str(e)}")
            return False
    
    def calculate_quality_score(self):
        """
        Calculate overall quality score (0-100).
        Industry-standard weighted scoring system.
        """
        if not self.deals:
            return 0
        
        total_score = 0
        
        # ========================================
        # 1. DEAL COUNT QUALITY (25 points)
        # ========================================
        deal_count_score = self._score_deal_count()
        self.score_breakdown['deal_count'] = deal_count_score
        total_score += deal_count_score
        
        # ========================================
        # 2. REQUIRED FIELDS (30 points)
        # ========================================
        required_fields_score = self._score_required_fields()
        self.score_breakdown['required_fields'] = required_fields_score
        total_score += required_fields_score
        
        # ========================================
        # 3. PRICE QUALITY (15 points)
        # ========================================
        price_score = self._score_price_quality()
        self.score_breakdown['price_quality'] = price_score
        total_score += price_score
        
        # ========================================
        # 4. CATEGORY DIVERSITY (15 points)
        # ========================================
        category_score = self._score_category_diversity()
        self.score_breakdown['category_diversity'] = category_score
        total_score += category_score
        
        # ========================================
        # 5. DATA COMPLETENESS (10 points)
        # ========================================
        completeness_score = self._score_data_completeness()
        self.score_breakdown['data_completeness'] = completeness_score
        total_score += completeness_score
        
        # ========================================
        # 6. DUPLICATE CHECK (5 points)
        # ========================================
        duplicate_score = self._score_duplicates()
        self.score_breakdown['duplicate_check'] = duplicate_score
        total_score += duplicate_score
        
        self.score = max(0, min(100, total_score))  # Clamp to 0-100
        return self.score
    
    def _score_deal_count(self):
        """Score based on deal count (25 points max)"""
        count = len(self.deals)
        weight = SCORING_WEIGHTS['deal_count']['weight']
        
        min_deals = QUALITY_THRESHOLDS['min_deals_per_page']
        max_deals = QUALITY_THRESHOLDS['max_deals_per_page']
        optimal_min, optimal_max = QUALITY_THRESHOLDS['optimal_deal_range']
        
        if count == 0:
            self.errors.append("CRITICAL: Zero deals extracted")
            return 0
        
        if optimal_min <= count <= optimal_max:
            return weight  # Perfect range
        
        if count < min_deals:
            deduction = (min_deals - count) * SCORING_WEIGHTS['deal_count']['deduction_per_missing']
            self.warnings.append(f"Low deal count: {count} (expected {optimal_min}-{optimal_max})")
            return max(0, weight - deduction)
        
        if count > max_deals:
            deduction = (count - max_deals) * SCORING_WEIGHTS['deal_count']['deduction_per_excess']
            self.warnings.append(f"Very high deal count: {count} (check for duplicates)")
            return max(0, weight - deduction)
        
        # Between min and optimal range
        return weight - 5
    
    def _score_required_fields(self):
        """Score based on required field completeness (30 points max)"""
        weight = SCORING_WEIGHTS['required_fields']['weight']
        deduction_per = SCORING_WEIGHTS['required_fields']['deduction_per_missing']
        
        missing_count = 0
        for i, deal in enumerate(self.deals):
            missing = [f for f in CRITICAL_FIELDS if not deal.get(f)]
            if missing:
                missing_count += len(missing)
                if len(self.errors) < 5:  # Cap error messages
                    self.errors.append(f"Deal #{i+1}: Missing required fields: {', '.join(missing)}")
        
        if missing_count > 0:
            self.errors.append(f"Total missing required fields: {missing_count}")
        
        return max(0, weight - (missing_count * deduction_per))
    
    def _score_price_quality(self):
        """Score based on price reasonableness (15 points max)"""
        weight = SCORING_WEIGHTS['price_quality']['weight']
        deduction_per = SCORING_WEIGHTS['price_quality']['deduction_per_outlier']
        
        prices = [d.get('price') for d in self.deals if isinstance(d.get('price'), (int, float))]
        if not prices:
            return weight  # No prices to check
        
        outlier_count = 0
        for i, deal in enumerate(self.deals):
            price = deal.get('price', 0)
            if isinstance(price, (int, float)):
                if price < QUALITY_THRESHOLDS['min_price']:
                    outlier_count += 1
                    if outlier_count <= 3:  # Limit warning messages
                        self.warnings.append(f"Deal #{i+1} ({deal.get('product_name', 'Unknown')}): Very low price ${price}")
                
                if price > QUALITY_THRESHOLDS['max_price']:
                    outlier_count += 1
                    if outlier_count <= 3:
                        self.warnings.append(f"Deal #{i+1} ({deal.get('product_name', 'Unknown')}): Very high price ${price}")
        
        outlier_rate = outlier_count / len(prices)
        if outlier_rate > QUALITY_THRESHOLDS['max_price_outliers']:
            deduction = int((outlier_rate - QUALITY_THRESHOLDS['max_price_outliers']) * 100)
            return max(0, weight - deduction)
        
        return max(0, weight - (outlier_count * deduction_per))
    
    def _score_category_diversity(self):
        """Score based on category distribution (15 points max)"""
        weight = SCORING_WEIGHTS['category_diversity']['weight']
        deduction = SCORING_WEIGHTS['category_diversity']['deduction_for_bias']
        
        categories = [d.get('product_category', 'Unknown').split(' > ')[0] for d in self.deals]
        category_counts = Counter(categories)
        
        if not category_counts:
            return weight
        
        top_category, top_count = category_counts.most_common(1)[0]
        concentration = top_count / len(self.deals)
        
        if concentration > QUALITY_THRESHOLDS['max_category_concentration']:
            self.errors.append(f"Extraction bias: {concentration*100:.0f}% of deals in '{top_category}' (likely missed other categories)")
            return max(0, weight - deduction)
        
        # More diverse = better score
        diversity_bonus = min(len(category_counts) - 1, 5)  # Up to 5 bonus points
        return min(weight, weight - 5 + diversity_bonus)
    
    def _score_data_completeness(self):
        """Score based on optional field completeness (10 points max)"""
        weight = SCORING_WEIGHTS['data_completeness']['weight']
        
        sku_count = sum(1 for d in self.deals if d.get('sku'))
        sku_coverage = (sku_count / len(self.deals)) * 100
        
        self.info['sku_coverage'] = f"{sku_coverage:.1f}%"
        
        if sku_coverage < QUALITY_THRESHOLDS['min_sku_coverage']:
            self.warnings.append(f"Low SKU coverage: {sku_coverage:.1f}% (optional, not critical)")
            return weight - SCORING_WEIGHTS['data_completeness']['deduction_for_low_sku']
        
        return weight
    
    def _score_duplicates(self):
        """Score based on duplicate detection (5 points max)"""
        weight = SCORING_WEIGHTS['duplicate_check']['weight']
        deduction_per = SCORING_WEIGHTS['duplicate_check']['deduction_per_duplicate']
        
        product_names = [d.get('product_name', '').lower().strip() for d in self.deals if d.get('product_name')]
        name_counts = Counter(product_names)
        duplicates = [name for name, count in name_counts.items() if count > 1]
        
        duplicate_count = sum(count - 1 for name, count in name_counts.items() if count > 1)
        duplicate_rate = duplicate_count / len(self.deals) if self.deals else 0
        
        self.info['duplicate_count'] = duplicate_count
        
        if duplicate_rate > QUALITY_THRESHOLDS['max_duplicate_rate']:
            self.errors.append(f"High duplicate rate: {duplicate_rate*100:.1f}% ({duplicate_count} duplicates)")
            return 0
        
        if duplicates:
            self.warnings.append(f"Found {len(duplicates)} duplicate product names (may be variants/choices)")
        
        return max(0, weight - (duplicate_count * deduction_per))
    
    def get_decision(self):
        """
        Automated decision based on quality score.
        Returns: ('ACCEPT' | 'RETRY' | 'REJECT', reason)
        """
        if self.errors and VALIDATION_RULES['block_on_missing_critical_fields']:
            return 'REJECT', f"Critical errors found: {len(self.errors)}"
        
        if self.score >= QUALITY_THRESHOLDS['excellent_threshold']:
            return 'ACCEPT', f"Excellent quality (score: {self.score})"
        
        if self.score >= QUALITY_THRESHOLDS['good_threshold']:
            return 'ACCEPT', f"Good quality (score: {self.score})"
        
        if self.score >= QUALITY_THRESHOLDS['retry_threshold']:
            return 'RETRY', f"Borderline quality (score: {self.score}) - suggest retry"
        
        return 'REJECT', f"Poor quality (score: {self.score})"
    
    def validate(self):
        """
        Main validation entry point.
        Returns validation report with automated decision.
        """
        if not self.load_deals():
            return {
                'decision': 'REJECT',
                'reason': 'Failed to load deals file',
                'score': 0,
                'errors': self.errors,
                'warnings': [],
                'info': {},
                'breakdown': {}
            }
        
        self.calculate_quality_score()
        decision, reason = self.get_decision()
        
        # Collect info stats
        if self.deals:
            prices = [d.get('price') for d in self.deals if isinstance(d.get('price'), (int, float))]
            if prices:
                self.info['price_stats'] = {
                    'average': round(sum(prices) / len(prices), 2),
                    'min': min(prices),
                    'max': max(prices)
                }
            
            categories = [d.get('product_category', 'Unknown').split(' > ')[0] for d in self.deals]
            self.info['top_categories'] = dict(Counter(categories).most_common(5))
            self.info['total_deals'] = len(self.deals)
        
        return {
            'decision': decision,
            'reason': reason,
            'score': self.score,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'breakdown': self.score_breakdown
        }


def print_validation_report(report):
    """Pretty print validation report"""
    print("\n" + "="*70)
    print("🎯 AUTOMATED QUALITY VALIDATION REPORT")
    print("="*70)
    
    # Decision banner
    decision = report['decision']
    score = report['score']
    
    if decision == 'ACCEPT':
        print(f"\n✅ DECISION: AUTO-ACCEPT")
        print(f"   Quality Score: {score}/100")
        print(f"   Reason: {report['reason']}")
    elif decision == 'RETRY':
        print(f"\n🔄 DECISION: RETRY RECOMMENDED")
        print(f"   Quality Score: {score}/100")
        print(f"   Reason: {report['reason']}")
    else:
        print(f"\n❌ DECISION: REJECT")
        print(f"   Quality Score: {score}/100")
        print(f"   Reason: {report['reason']}")
    
    # Score breakdown
    if report['breakdown']:
        print(f"\n📊 Score Breakdown:")
        print("-" * 70)
        for component, points in report['breakdown'].items():
            print(f"   {component.replace('_', ' ').title()}: {points:.1f} points")
    
    # Errors
    if report['errors']:
        print(f"\n❌ Errors ({len(report['errors'])}):")
        print("-" * 70)
        for error in report['errors'][:10]:
            print(f"   • {error}")
        if len(report['errors']) > 10:
            print(f"   ... and {len(report['errors']) - 10} more")
    
    # Warnings
    if report['warnings']:
        print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
        print("-" * 70)
        for warning in report['warnings'][:10]:
            print(f"   • {warning}")
        if len(report['warnings']) > 10:
            print(f"   ... and {len(report['warnings']) - 10} more")
    
    # Statistics
    if report['info']:
        print(f"\nℹ️  Statistics:")
        print("-" * 70)
        for key, value in report['info'].items():
            if isinstance(value, dict):
                print(f"   {key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    print(f"      {k}: {v}")
            else:
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    validator = QualityValidator()
    report = validator.validate()
    
    print_validation_report(report)
    
    # Exit codes for scripting
    if report['decision'] == 'ACCEPT':
        sys.exit(0)
    elif report['decision'] == 'RETRY':
        sys.exit(2)
    else:
        sys.exit(1)

