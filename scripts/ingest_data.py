import json
import sys
import os
import weaviate
from weaviate.classes.config import Configure
from dotenv import load_dotenv

# Add project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Load environment variables from backend/.env
env_path = os.path.join(project_root, 'backend', '.env')
load_dotenv(dotenv_path=env_path)

# Verify OPENAI_API_KEY is loaded
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY not found in backend/.env")
    print(f"   Looked for .env at: {env_path}")
    print("   Please add your OpenAI API key to backend/.env")
    sys.exit(1)

from backend.app.weaviate_client import get_weaviate_client, get_deal_schema

def create_vector_text(deal: dict):
    """
    Creates a rich text string for vectorization from the deal's JSON.
    This is our 'intelligent chunking' for semantic search.
    """
    attrs = ", ".join(deal.get("attributes", []))
    conditions = ", ".join(deal.get("deal_conditions", []))
    
    return (
        f"Product: {deal.get('product_name', '')}. "
        f"Category: {deal.get('product_category', '')}. "
        f"Store: {deal.get('store', '')}. "
        f"Type of Deal: {deal.get('deal_type', '')}. "
        f"Features: {attrs}. "
        f"Conditions: {conditions}."
    )

def main():
    client = get_weaviate_client()
    
    collection_name = "Deal"
    if client.collections.exists(collection_name):
        client.collections.delete(collection_name)
    
    deals_collection = client.collections.create(
        name=collection_name,
        vectorizer_config=Configure.Vectorizer.text2vec_openai(),
        properties=get_deal_schema()
    )

    # Determine which deals file to use
    script_dir = os.path.dirname(os.path.abspath(__file__))
    deals_file = os.path.join(script_dir, 'deals.json')
    
    # Fallback to example file if deals.json doesn't exist
    if not os.path.exists(deals_file):
        deals_file = os.path.join(script_dir, 'deals.example.json')
        print(f"ℹ️  deals.json not found, using {deals_file}")
    else:
        print(f"✅ Loading deals from: {deals_file}")
    
    with open(deals_file, 'r') as f:
        data = json.load(f)

    with deals_collection.batch.dynamic() as batch:
        for deal in data:
            vector_text = create_vector_text(deal)
            
            # Parse and format dates to RFC3339 (required by Weaviate)
            # Format: YYYY-MM-DDTHH:MM:SSZ
            valid_from = deal.get("valid_from")
            valid_to = deal.get("valid_to")
            
            # Helper function to ensure RFC3339 format
            def ensure_rfc3339(date_str):
                if not date_str or not isinstance(date_str, str):
                    return None
                
                date_str = date_str.strip()
                
                # If date only (no time), add default time
                if 'T' not in date_str:
                    # For valid_from, use start of day; for valid_to, use end of day
                    # But we'll use 00:00:00 for both and adjust later if needed
                    date_str = date_str + 'T00:00:00'
                
                # If no timezone, add UTC
                if not date_str.endswith('Z') and '+' not in date_str[-6:] and '-' not in date_str[-6:]:
                    date_str = date_str + 'Z'
                
                return date_str
            
            valid_from = ensure_rfc3339(valid_from)
            valid_to = ensure_rfc3339(valid_to)
            
            # For valid_to, if it was date-only, use end of day instead
            if valid_to and deal.get("valid_to") and 'T' not in deal.get("valid_to"):
                valid_to = valid_to.replace('T00:00:00Z', 'T23:59:59Z')
            
            properties = {
                "product_name": deal.get("product_name"),
                "sku": deal.get("sku"),
                "product_category": deal.get("product_category"),
                "vector_text": vector_text,
                "price": deal.get("price"),
                "store": deal.get("store"),
                "original_price": deal.get("original_price"),
                "deal_type": deal.get("deal_type"),
                "in_store_only": deal.get("in_store_only"),
                "deal_conditions": deal.get("deal_conditions"),
                "valid_from": valid_from,  # RFC3339 format with timezone
                "valid_to": valid_to,      # RFC3339 format with timezone
                "bundle_deal": deal.get("bundle_deal", False),  # Bundle deals
                "required_purchase": deal.get("required_purchase"),  # What to buy
                "free_item": deal.get("free_item"),  # What comes free
                "full_json": json.dumps(deal),
            }
            
            batch.add_object(
                properties=properties
            )
    
    # Check for failed objects
    if deals_collection.batch.failed_objects:
        failed = len(deals_collection.batch.failed_objects)
        successful = len(data) - failed
        
        print(f"\n⚠️  BATCH ERRORS DETECTED:")
        print(f"   ✅ Successful: {successful}/{len(data)}")
        print(f"   ❌ Failed: {failed}/{len(data)}")
        print(f"\n📋 First 3 errors:")
        
        for i, failed_obj in enumerate(deals_collection.batch.failed_objects[:3]):
            print(f"\n   Error {i+1}:")
            if hasattr(failed_obj, 'message'):
                print(f"   Message: {failed_obj.message}")
            if hasattr(failed_obj, 'object_'):
                try:
                    product_name = failed_obj.object_.properties.get('product_name', 'Unknown')
                    print(f"   Product: {product_name}")
                except:
                    pass
    else:
        print(f"\n✅ Successfully ingested {len(data)} deals with no errors!")

if __name__ == "__main__":
    main()

