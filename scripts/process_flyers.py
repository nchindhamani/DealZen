import os
import base64
import json
import mimetypes
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the backend .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../backend/.env'))

# --- Configuration ---
# Get project root (one level up from scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FOLDER = os.path.join(PROJECT_ROOT, 'flyer-images')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'deals.json')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not found in backend/.env file")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- The "Mega-Prompt" for GPT-4o Vision ---
# This is the most critical part. It defines the extraction task.
EXTRACTION_SYSTEM_PROMPT = """
You are a precision retail flyer scanner. Your ONLY job is to find and extract EVERY SINGLE PRODUCT 
that has a price on this flyer image, regardless of type, size, or location.

CRITICAL RULES:
1. Scan the ENTIRE image systematically: top to bottom, left to right, center AND corners
2. Extract ALL products with prices - do NOT filter by category or importance
3. Treat large featured items and small corner items EQUALLY
4. If you see a price tag ($X.XX) and product name, extract it
5. Do NOT assume what matters - extract EVERYTHING
6. Missing items = extraction failure

Your goal: Maximum completeness. Every product with a price must be captured.

You MUST return your answer *only* as a valid JSON list (an array) of JSON objects.

Do not include any other text, pre-amble, or explanations. Your entire response must be the JSON list.

Each object in the list must conform to the following schema:

{
  "product_name": "string (The full product name, e.g., 'Brand X Product Model ABC123')",
  "sku": "string or null (The product SKU or model number, e.g., 'ABC123XYZ')",
  "product_category": "string or null (The product category, e.g., 'Category > Subcategory > Type')",
  "price": "float (The sale price, e.g., 499.99. Use numbers only. For 'Buy X Get Y Free' offers, use the price of what you BUY, not 0)",
  "original_price": "float or null (The original/regular price, e.g., 799.99)",
  "store": "string (The store name, e.g., 'Store Name')",
  "valid_from": "string or null (The ISO 8601 date the deal starts, e.g., '2025-11-27T08:00:00')",
  "valid_to": "string or null (The ISO 8601 date the deal ends, e.g., '2025-11-28T23:59:59')",
  "deal_type": "string (A short description of the deal, e.g., 'Black Friday Door Crasher', 'Buy One Get One Free', 'Free Gift with Purchase')",
  "in_store_only": "boolean (true if the deal is in-store only, otherwise false)",
  "deal_conditions": "list[string] (A list of fine-print conditions, e.g., ['Limit 1 per customer', 'While supplies last', 'Buy Item X to get Item Y free'])",
  "attributes": "list[string] (A list of key product features, e.g., ['Feature A', 'Feature B', 'Feature C'])",
  "bundle_deal": "boolean (true if this is a bundle/combo deal like 'Buy X Get Y Free', otherwise false)",
  "required_purchase": "string or null (For 'Get Free' offers, what product must be purchased. e.g., 'Item X ($99)'. Otherwise null)",
  "free_item": "string or null (For bundle deals, what item comes free. e.g., 'Choice of Item Y or Item Z'. Otherwise null)"
}

--- INSTRUCTIONS ---

1.  **Be EXTREMELY Thorough:** Extract EVERY SINGLE product with a price, no matter:
    - How small or large it appears
    - What category it belongs to
    - Where it's located on the page
    - How prominently it's featured
    
    If it has a price tag and product name → EXTRACT IT.
    
2.  **Be Accurate:** Extract prices and product names exactly as written.

3.  **Systematic Scanning:** Scan the image in a grid pattern:
    - Start top-left, move right
    - Then middle-left, move right  
    - Then bottom-left, move right
    - Don't skip ANY section
    
4.  **Focus on Complete Deals:** If you see partial/cut-off products at edges, IGNORE them. Only extract products that are fully visible and readable.

5.  **Use `null`:** If a non-required field (like `sku` or `original_price`) is not present, use `null`.

6.  **Infer Booleans:** `in_store_only` should be `true` if it's specified, otherwise `false`.

7.  **Infer Dates:** If specific dates/times are mentioned, use them. If it's just "Black Friday," you can infer the dates (e.g., Nov 27-28, 2025). If no date is given, use `null`.

8.  **Store Name:** The user will provide the store name in the prompt. Use that store name for ALL deals. If you can see different branding on the flyer itself, prioritize the visual branding, but default to the provided store name.

9.  **JSON ONLY:** Your output must start with `[` and end with `]`.

10. **Bundle Deals & Promotions:** Handle "Buy X Get Y Free" offers correctly:
    - If you see "BUY ONE OF THESE" + "GET 1 FREE", create ONE deal entry for the PURCHASE item
    - Set `bundle_deal` to true
    - Set `price` to the purchase item's price (NOT $0)
    - Set `required_purchase` to describe what needs to be bought
    - Set `free_item` to describe what comes free
    - Add complete details in `deal_conditions`
    - Example: Item X for $99 with free Item Y
      {
        "product_name": "Item X with Free Item Y",
        "price": 99.0,
        "deal_type": "Buy One Get One Free",
        "bundle_deal": true,
        "required_purchase": "Item X (Main Product)",
        "free_item": "Item Y (Free Bonus)",
        "deal_conditions": ["Buy Item X to get Item Y free", "Valid dates as shown"]
      }

11. **Choice-Based Deals (CRITICAL):** When you see "Choose X OR Y" or "Pick A or B", create SEPARATE deals:
    - Example: "Choose Product A OR Product B for $19.99 each"
    - Extract as TWO separate deals:
      1. {"product_name": "Product A", "price": 19.99}
      2. {"product_name": "Product B", "price": 19.99}
    - Each choice is a valid standalone product that customers can search for
    - Do NOT combine them into one deal
    - Do NOT put "or" in the product_name

CRITICAL RULES (Must Follow):
1. Do NOT skip any deals. If you see 10 products, extract all 10. If you see 50 products, extract all 50.
2. Do NOT create separate deals for free items with $0 price. Bundle them with the purchase item.
3. For "Choose X or Y" / "Pick A or B" offers, create SEPARATE deals for EACH option:
   - If text says "Choose 30-pack OR 36-pack for $X", extract TWO deals
   - If text says "Select Product A or Product B", extract TWO deals
   - Each choice = One separate deal entry
"""

def encode_image_to_base64(image_path):
    """Encodes a local image file to a base64 string."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith('image'):
        raise ValueError(f"File {image_path} is not a valid image.")
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_gpt4o_vision_api(base64_image_data, mime_type, filename):
    """
    Calls the GPT-4o Vision API to extract deals from a single flyer image.
    """
    print(f"[API Call] Sending {filename} to GPT-4o Vision...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Use the powerful vision model
            messages=[
                {
                    "role": "system",
                    "content": EXTRACTION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Extract ALL deals from this flyer image.

STORE NAME: {filename.split('_')[0].upper()}
Use this store name for all deals unless you see clear different branding in the image.

SCAN EVERY SECTION: Top, middle, bottom, left, right, corners.
Extract EVERY product that has a price - large items, small items, featured items, background items.

⚠️ SPECIAL ATTENTION - Choice-Based Deals:
If you see text like "Choose X or Y", "Pick A or B", "Select from...", create SEPARATE deals for EACH option.
Example: "Choose 30-pack OR 36-pack for $18.87" = TWO deals (one for 30-pack, one for 36-pack)

Your extraction count target: If you see 50 items, extract 50. If you see 100 items, extract 100.
Do not stop early. Extract until every priced product is captured."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=16384, # Increased from 4096 to allow comprehensive extraction
            temperature=0.1 # Be precise, not creative
        )
        
        json_response = response.choices[0].message.content
        
        # Clean the response to ensure it's valid JSON
        # GPT can sometimes add ```json ... ```
        if "```json" in json_response:
            json_response = json_response.split("```json\n", 1)[1].rsplit("```", 1)[0]
            
        print(f"[API Call] Received response for {filename}.")
        return json.loads(json_response) # Parse string to JSON list
    except Exception as e:
        print(f"[Error] API call failed for {filename}: {e}")
        return None

def main():
    """
    Main script to process all flyers and generate the deals.json file.
    """
    start_time = time.time()
    print("\n" + "="*60)
    print("    DealZen Flyer Processing Script")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not os.path.exists(INPUT_FOLDER):
        print(f"❌ [Error] Input folder not found: {INPUT_FOLDER}")
        print("Please create this folder and add your flyer images.")
        return

    # Get all image files
    image_files = [f for f in os.listdir(INPUT_FOLDER) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not image_files:
        print(f"❌ No image files found in {INPUT_FOLDER}")
        return
    
    total_images = len(image_files)
    print(f"📸 Found {total_images} image(s) to process")
    print(f"⏱️  Estimated time: {total_images * 25} seconds (~{total_images * 25 / 60:.1f} minutes)\n")
    
    all_deals = []
    
    # Loop through all files in the input folder
    for index, filename in enumerate(image_files, 1):
        image_path = os.path.join(INPUT_FOLDER, filename)
        
        try:
            image_start = time.time()
            print(f"\n[{index}/{total_images}] 📄 Processing: {filename}")
            
            mime_type, _ = mimetypes.guess_type(image_path)
            base64_image = encode_image_to_base64(image_path)
            
            print(f"    ⏳ Sending to GPT-4o Vision API...")
            # Call the AI to get the deals for this one flyer
            deals_list = call_gpt4o_vision_api(base64_image, mime_type, filename)
            
            image_time = time.time() - image_start
            
            if deals_list:
                print(f"    ✅ Extracted {len(deals_list)} deals from {filename} ({image_time:.1f}s)")
                # Add all deals from this flyer to our main list
                all_deals.extend(deals_list)
            else:
                print(f"    ⚠️  No deals found or error in {filename} ({image_time:.1f}s)")
                
        except Exception as e:
            print(f"    ❌ [Error] Failed to process {filename}: {e}")
        
        # Show progress
        remaining = total_images - index
        if remaining > 0:
            print(f"    📊 Progress: {index}/{total_images} complete, {remaining} remaining")

    # Write all collected deals to the final JSON file
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("    PROCESSING COMPLETE")
    print("="*60)
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_deals, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Extracted {len(all_deals)} total deals from {total_images} images")
        print(f"📂 Saved to: {OUTPUT_FILE}")
        print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"📊 Average: {total_time/total_images:.1f} seconds per image")
        print(f"\n🚀 Next step: Load into Weaviate with 'uv run python scripts/ingest_data.py'")
    except Exception as e:
        print(f"❌ [Error] Failed to write output file: {e}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

