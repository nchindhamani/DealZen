"""
DealZen Retry Queue Management
Handles failed extractions for automatic retry with enhanced prompts.
"""

import json
import os
from datetime import datetime
from pathlib import Path

RETRY_QUEUE_FILE = 'logs/retry_queue.json'
PROCESSED_SUCCESSFULLY = 'logs/processed_successfully.json'


class RetryQueue:
    """
    Manages retry queue for failed extractions.
    
    Strategy:
    - Store METADATA (file paths, not images)
    - Track failure reasons and attempt count
    - Auto-retry with enhanced prompts
    - Move to success queue when passed
    """
    
    def __init__(self):
        self.retry_queue_path = RETRY_QUEUE_FILE
        self.success_queue_path = PROCESSED_SUCCESSFULLY
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create queue files if they don't exist"""
        os.makedirs('logs', exist_ok=True)
        
        for path in [self.retry_queue_path, self.success_queue_path]:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump([], f)
    
    def add_to_retry_queue(self, image_path, reason, score, extraction_data=None):
        """
        Add failed extraction to retry queue.
        
        IMPORTANT: We store IMAGE PATH, not the image itself.
        This saves disk space and allows re-extraction with fresh prompt.
        
        Args:
            image_path: Path to original flyer image
            reason: Why it failed (e.g., "Low quality score: 45")
            score: Quality score from validation
            extraction_data: Optional - the deals.json that failed (for debugging)
        """
        queue = self._load_queue(self.retry_queue_path)
        
        # Check if already in queue
        existing = next((item for item in queue if item['image_path'] == image_path), None)
        
        if existing:
            # Update attempt count
            existing['attempt_count'] += 1
            existing['last_attempt'] = datetime.now().isoformat()
            existing['last_score'] = score
            existing['last_reason'] = reason
        else:
            # Add new entry
            queue.append({
                'image_path': image_path,
                'image_name': os.path.basename(image_path),
                'first_failed': datetime.now().isoformat(),
                'last_attempt': datetime.now().isoformat(),
                'attempt_count': 1,
                'last_score': score,
                'last_reason': reason,
                'status': 'pending_retry',
                'extraction_data_path': self._save_failed_extraction(image_path, extraction_data) if extraction_data else None
            })
        
        self._save_queue(self.retry_queue_path, queue)
        
        print(f"📋 Added to retry queue: {os.path.basename(image_path)}")
        print(f"   Reason: {reason}")
        print(f"   Score: {score}/100")
        print(f"   Attempts: {existing['attempt_count'] if existing else 1}")
    
    def _save_failed_extraction(self, image_path, extraction_data):
        """
        Save failed extraction data for debugging.
        NOT the image - just the deals.json that failed validation.
        """
        failed_dir = 'logs/failed_extractions'
        os.makedirs(failed_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = Path(image_path).stem
        output_path = f"{failed_dir}/{base_name}_{timestamp}_failed.json"
        
        with open(output_path, 'w') as f:
            json.dump(extraction_data, f, indent=2)
        
        return output_path
    
    def mark_as_success(self, image_path, score, deals_count):
        """
        Move from retry queue to success queue after successful extraction.
        """
        # Remove from retry queue
        retry_queue = self._load_queue(self.retry_queue_path)
        retry_queue = [item for item in retry_queue if item['image_path'] != image_path]
        self._save_queue(self.retry_queue_path, retry_queue)
        
        # Add to success queue
        success_queue = self._load_queue(self.success_queue_path)
        success_queue.append({
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'processed_at': datetime.now().isoformat(),
            'quality_score': score,
            'deals_extracted': deals_count,
            'status': 'success'
        })
        self._save_queue(self.success_queue_path, success_queue)
        
        print(f"✅ Moved to success queue: {os.path.basename(image_path)}")
    
    def get_retry_candidates(self, max_attempts=3):
        """
        Get images that need retry (attempt_count < max_attempts).
        
        Returns list of image paths to retry.
        """
        queue = self._load_queue(self.retry_queue_path)
        
        candidates = [
            item for item in queue 
            if item['attempt_count'] < max_attempts and item['status'] == 'pending_retry'
        ]
        
        return candidates
    
    def get_permanent_failures(self, max_attempts=3):
        """
        Get images that failed all retry attempts.
        These need manual review.
        """
        queue = self._load_queue(self.retry_queue_path)
        
        failures = [
            item for item in queue 
            if item['attempt_count'] >= max_attempts
        ]
        
        return failures
    
    def print_summary(self):
        """Print summary of retry queue status"""
        retry_queue = self._load_queue(self.retry_queue_path)
        success_queue = self._load_queue(self.success_queue_path)
        
        retry_candidates = self.get_retry_candidates()
        permanent_failures = self.get_permanent_failures()
        
        print("\n" + "="*70)
        print("📊 RETRY QUEUE SUMMARY")
        print("="*70)
        print(f"\n✅ Successfully Processed: {len(success_queue)}")
        print(f"🔄 Pending Retry: {len(retry_candidates)}")
        print(f"❌ Permanent Failures: {len(permanent_failures)}")
        print(f"📋 Total in Retry Queue: {len(retry_queue)}")
        
        if retry_candidates:
            print(f"\n🔄 Retry Candidates:")
            for item in retry_candidates:
                print(f"   • {item['image_name']}")
                print(f"     Attempts: {item['attempt_count']}, Last Score: {item['last_score']}")
        
        if permanent_failures:
            print(f"\n❌ Permanent Failures (need manual review):")
            for item in permanent_failures:
                print(f"   • {item['image_name']}")
                print(f"     Attempts: {item['attempt_count']}, Last Score: {item['last_score']}")
                print(f"     Reason: {item['last_reason']}")
        
        print("="*70 + "\n")
    
    def _load_queue(self, path):
        """Load queue from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_queue(self, path, queue):
        """Save queue to JSON file"""
        with open(path, 'w') as f:
            json.dump(queue, f, indent=2)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    """
    Example workflow demonstrating retry queue management.
    """
    
    retry_queue = RetryQueue()
    
    # Example 1: First extraction fails
    print("="*70)
    print("EXAMPLE 1: Initial extraction fails (score 45)")
    print("="*70)
    
    retry_queue.add_to_retry_queue(
        image_path='flyer-images/walmart_bf_2023.jpg',
        reason='Low quality score: extraction bias detected',
        score=45,
        extraction_data=[
            {'product_name': 'Tool A', 'price': 99.99},
            {'product_name': 'Tool B', 'price': 149.99}
        ]
    )
    
    # Example 2: Retry with enhanced prompt - still fails
    print("\n" + "="*70)
    print("EXAMPLE 2: Retry attempt 1 - improved but still low (score 62)")
    print("="*70)
    
    retry_queue.add_to_retry_queue(
        image_path='flyer-images/walmart_bf_2023.jpg',
        reason='Low SKU coverage and price outliers',
        score=62,
        extraction_data=[
            {'product_name': 'Tool A', 'price': 99.99, 'sku': 'WAL123'},
            {'product_name': 'Tool B', 'price': 149.99, 'sku': 'WAL456'},
            {'product_name': 'Batteries AAA', 'price': 8.99, 'sku': None}
        ]
    )
    
    # Example 3: Final retry succeeds
    print("\n" + "="*70)
    print("EXAMPLE 3: Retry attempt 2 - SUCCESS (score 85)")
    print("="*70)
    
    retry_queue.mark_as_success(
        image_path='flyer-images/walmart_bf_2023.jpg',
        score=85,
        deals_count=15
    )
    
    # Print summary
    retry_queue.print_summary()
    
    print("\n💾 STORAGE STRATEGY:")
    print("="*70)
    print("✅ What we STORE:")
    print("   • Image file PATH (not the image itself)")
    print("   • Failure reason and score")
    print("   • Attempt count and timestamps")
    print("   • Optional: Failed deals.json (for debugging)")
    print()
    print("❌ What we DON'T store:")
    print("   • Duplicate image files (saves disk space)")
    print("   • Binary image data in queue")
    print()
    print("🔄 Why this works:")
    print("   • Re-extract from original image with enhanced prompt")
    print("   • No disk space wasted on duplicates")
    print("   • Can compare extraction attempts")
    print("   • Full audit trail maintained")
    print("="*70)

