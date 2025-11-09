import json
import weaviate
from backend.app.weaviate_client import get_weaviate_client, get_deal_schema
from weaviate.classes.config import Configure

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

    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    deals_file = os.path.join(script_dir, 'deals.example.json')
    
    with open(deals_file, 'r') as f:
        data = json.load(f)

    with deals_collection.batch.dynamic() as batch:
        for deal in data:
            vector_text = create_vector_text(deal)
            
            # Parse dates from ISO 8601 format strings
            valid_from = deal.get("valid_from")  # Already in ISO format
            valid_to = deal.get("valid_to")      # Already in ISO format
            
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
                "valid_from": valid_from,  # ISO 8601 string
                "valid_to": valid_to,      # ISO 8601 string
                "full_json": json.dumps(deal),
            }
            
            batch.add_object(
                properties=properties
            )
    
    print(f"Successfully ingested {len(data)} deals.")

if __name__ == "__main__":
    main()

