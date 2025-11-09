import weaviate
import weaviate.classes.config as wvc
import os

# Get Weaviate and OpenAI API keys from environment variables
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_weaviate_client():
    """Establishes connection to the Weaviate instance."""
    client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}
    )
    return client

async def perform_hybrid_search(client: weaviate.WeaviateClient, query: str):
    """
    Performs a hybrid search.
    - Vector search on 'vector_text'
    - Keyword search on 'product_name', 'sku', and 'product_category'
    - Retrieves Top 5 results.
    """
    deals = client.collections.get("Deal")
    
    response = deals.query.hybrid(
        query=query,
        # Define properties for hybrid search
        query_properties=["vector_text^2", "product_name", "sku", "product_category"],
        # 50/50 blend of vector and keyword
        alpha=0.5,
        # Retrieve TOP 5
        limit=5 
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
        wvc.Property(name="full_json", data_type=wvc.DataType.TEXT, skip_vectorization=True),
    ]

