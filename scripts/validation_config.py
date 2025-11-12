"""
DealZen Validation Configuration
Industry-standard quality thresholds and scoring weights.
"""

# ============================================
# QUALITY THRESHOLDS (Auto-Accept Criteria)
# ============================================

QUALITY_THRESHOLDS = {
    # Deal count thresholds
    'min_deals_per_page': 8,       # Below this = likely extraction failure
    'max_deals_per_page': 60,      # Above this = possible duplicates/multi-page
    'optimal_deal_range': (15, 35), # Typical flyer page
    
    # Data quality thresholds
    'min_sku_coverage': 20,        # % - Nice to have, not critical
    'max_price': 10000,            # Flag if exceeded (appliances can be high)
    'min_price': 0.10,             # Allow low prices (cards, candy)
    
    # Extraction quality thresholds
    'max_category_concentration': 0.85,  # 85% in one category = extraction bias
    'max_duplicate_rate': 0.05,          # 5% duplicates acceptable
    'max_price_outliers': 0.15,          # 15% of deals can be outliers
    
    # Quality score thresholds (0-100)
    'excellent_threshold': 85,     # Auto-accept, no logging
    'good_threshold': 70,          # Auto-accept, log for audit
    'retry_threshold': 50,         # Retry extraction once
    'reject_threshold': 50,        # Below this = reject
}

# ============================================
# QUALITY SCORING WEIGHTS
# ============================================

SCORING_WEIGHTS = {
    'deal_count': {
        'weight': 25,              # 25 points for good deal count
        'deduction_per_missing': 3, # -3 for each deal below minimum
        'deduction_per_excess': 2,  # -2 for each deal above maximum
    },
    'required_fields': {
        'weight': 30,              # 30 points for complete data
        'deduction_per_missing': 10, # -10 for each missing required field
    },
    'price_quality': {
        'weight': 15,              # 15 points for reasonable prices
        'deduction_per_outlier': 2, # -2 for each suspicious price
    },
    'category_diversity': {
        'weight': 15,              # 15 points for diverse categories
        'deduction_for_bias': 20,  # -20 if extraction bias detected
    },
    'data_completeness': {
        'weight': 10,              # 10 points for SKUs, dates, etc.
        'deduction_for_low_sku': 5, # -5 if SKU coverage < 30%
    },
    'duplicate_check': {
        'weight': 5,               # 5 points for no duplicates
        'deduction_per_duplicate': 1, # -1 per duplicate deal
    }
}

# ============================================
# AUTO-FIX STRATEGIES
# ============================================

AUTO_FIX = {
    'missing_sku': 'set_to_null',          # Don't block, just set null
    'low_sku_coverage': 'accept',          # It's optional
    'price_outlier_low': 'flag_but_accept', # Keep but note
    'price_outlier_high': 'flag_but_accept', # Keep but note
    'date_format': 'auto_correct',         # Fix RFC3339 issues
    'minor_duplicates': 'keep_first',      # If <5% duplicates, keep first occurrence
}

# ============================================
# CRITICAL VALIDATION RULES
# ============================================

CRITICAL_FIELDS = ['product_name', 'price', 'store']

VALIDATION_RULES = {
    'block_on_zero_deals': True,           # Block if 0 deals extracted
    'block_on_missing_critical_fields': True, # Block if missing required fields
    'block_on_extraction_bias': True,      # Block if 85%+ in one category
    'block_on_high_duplicates': True,      # Block if >10% duplicates
    'allow_low_sku_coverage': True,        # Don't block on low SKUs
    'allow_price_outliers': True,          # Don't block on price anomalies
}

# ============================================
# LOGGING CONFIGURATION
# ============================================

LOGGING = {
    'log_excellent_quality': False,        # Don't log scores 85+
    'log_good_quality': True,              # Log scores 70-84
    'log_retries': True,                   # Log all retry attempts
    'log_rejections': True,                # Always log rejections
    'log_file': 'logs/validation_log.txt',
}

