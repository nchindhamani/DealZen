import weaviate
import weaviate.classes.config as wvc
from weaviate.classes.query import Filter
from datetime import datetime, timezone
import os

def get_weaviate_client():
    """Establishes connection to the Weaviate instance."""
    # Get API key at runtime (after .env is loaded)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        headers={"X-OpenAI-Api-Key": openai_api_key}
    )
    return client

async def perform_hybrid_search(client: weaviate.WeaviateClient, query: str):
    """
    Performs a hybrid search with date filtering.
    - Vector search on 'vector_text'
    - Keyword search on 'product_name', 'sku', and 'product_category'
    - Filters out expired deals (valid_to < current date)
    - Retrieves Top 5 results.
    """
    deals = client.collections.get("Deal")
    
    # Get current date in ISO format
    current_date = datetime.now(timezone.utc).isoformat()
    
    # Build filter for non-expired deals
    # Only show deals where valid_to >= current_date
    # (Removed null check as it requires indexNullState configuration)
    date_filter = Filter.by_property("valid_to").greater_or_equal(current_date)
    
    response = deals.query.hybrid(
        query=query,
        # Define properties for hybrid search
        query_properties=["vector_text^2", "product_name", "sku", "product_category"],
        # 50/50 blend of vector and keyword
        alpha=0.5,
        # Filter out expired deals
        filters=date_filter,
        # Retrieve TOP 20 (increased from 10 for broader price comparison)
        limit=20
    )
    
    return [item.properties for item in response.objects]

def get_deal_schema():
    """Returns the schema for our 'Deal' collection."""
    return [
        wvc.Property(name="product_name", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.WORD),
        wvc.Property(name="sku", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.FIELD),
        wvc.Property(name="product_category", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.WORD),
        wvc.Property(name="vector_text", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.WORD, skip_vectorization=True),
        wvc.Property(name="price", data_type=wvc.DataType.NUMBER),
        wvc.Property(name="store", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.FIELD),
        wvc.Property(name="original_price", data_type=wvc.DataType.NUMBER),
        wvc.Property(name="deal_type", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.FIELD),
        wvc.Property(name="in_store_only", data_type=wvc.DataType.BOOL),
        wvc.Property(name="deal_conditions", data_type=wvc.DataType.TEXT_ARRAY, tokenization=wvc.Tokenization.FIELD),
        wvc.Property(name="valid_from", data_type=wvc.DataType.DATE),  # Date filtering
        wvc.Property(name="valid_to", data_type=wvc.DataType.DATE),    # Date filtering
        wvc.Property(name="bundle_deal", data_type=wvc.DataType.BOOL),  # Bundle/combo deals
        wvc.Property(name="required_purchase", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.WORD),  # What to buy
        wvc.Property(name="free_item", data_type=wvc.DataType.TEXT, tokenization=wvc.Tokenization.WORD),  # What comes free
        wvc.Property(name="full_json", data_type=wvc.DataType.TEXT, skip_vectorization=True),
    ]

