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
You are a precision data extraction engine. Your task is to analyze an image of a retail flyer and extract every single deal or product promotion you see.

You MUST return your answer *only* as a valid JSON list (an array) of JSON objects.

Do not include any other text, pre-amble, or explanations. Your entire response must be the JSON list.

Each object in the list must conform to the following schema:

{
  "product_name": "string (The full product name, e.g., 'Samsung 55\" QLED TV (QN55Q80C)')",
  "sku": "string or null (The product SKU or model number, e.g., 'QN55Q80CBUXA')",
  "product_category": "string or null (The product category, e.g., 'Electronics > Televisions > QLED TVs')",
  "price": "float (The sale price, e.g., 499.99. Use numbers only)",
  "original_price": "float or null (The original/regular price, e.g., 799.99)",
  "store": "string (The store name, e.g., 'Best Buy', 'Walmart')",
  "valid_from": "string or null (The ISO 8601 date the deal starts, e.g., '2025-11-27T08:00:00')",
  "valid_to": "string or null (The ISO 8601 date the deal ends, e.g., '2025-11-28T23:59:59')",
  "deal_type": "string (A short description of the deal, e.g., 'Black Friday Door Crasher', 'Online Special')",
  "in_store_only": "boolean (true if the deal is in-store only, otherwise false)",
  "deal_conditions": "list[string] (A list of fine-print conditions, e.g., ['Limit 1 per customer', 'While supplies last'])",
  "attributes": "list[string] (A list of key product features, e.g., ['QLED', '55-inch', '4K', 'Smart TV'])"
}

--- INSTRUCTIONS ---

1.  **Be Thorough:** Find ALL deals on the page.
2.  **Be Accurate:** Extract prices and names exactly as written.
3.  **Focus on Complete Deals:** If you see partial/cut-off products at edges or corners, IGNORE them. Only extract deals that are fully visible and readable.
4.  **Use `null`:** If a non-required field (like `sku` or `original_price`) is not present, use `null`.
5.  **Infer Booleans:** `in_store_only` should be `true` if it's specified, otherwise `false`.
6.  **Infer Dates:** If specific dates/times are mentioned, use them. If it's just "Black Friday," you can infer the dates (e.g., Nov 27-28, 2025). If no date is given, use `null`.
7.  **Store Name:** The user will provide the store name in the prompt. Use that store name for ALL deals. If you can see different branding on the flyer itself, prioritize the visual branding, but default to the provided store name.
8.  **JSON ONLY:** Your output must start with `[` and end with `]`.
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
                            "text": f"""Extract all deals from this flyer image.

STORE NAME: {filename.split('_')[0].upper()}
Use this store name for all deals unless you see clear different branding in the image.

IMPORTANT: This may be a screenshot with edges of other pages visible. Focus only on the main, center content. Ignore any partial/cut-off deals at the edges or corners.

Extract only complete, fully visible deals."""
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
            max_tokens=4096, # Give it plenty of space for JSON
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

