import os
import base64
import json
import mimetypes
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the backend .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../backend/.env'))

# --- Configuration ---
INPUT_FOLDER = './flyer-images' 
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
3.  **Use `null`:** If a non-required field (like `sku` or `original_price`) is not present, use `null`.
4.  **Infer Booleans:** `in_store_only` should be `true` if it's specified, otherwise `false`.
5.  **Infer Dates:** If specific dates/times are mentioned, use them. If it's just "Black Friday," you can infer the dates (e.g., Nov 27-28, 2025). If no date is given, use `null`.
6.  **Store Name:** Infer the store from the flyer's branding (e.g., Best Buy, Coach, Macy's). You must include this in *every* deal object.
7.  **JSON ONLY:** Your output must start with `[` and end with `]`.
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
                            "text": f"Extract all deals from this flyer image. The store appears to be {filename.split('_')[0]}. Please be precise."
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
    print("--- Starting DealZen Flyer Processing Script ---")
    
    if not os.path.exists(INPUT_FOLDER):
        print(f"[Error] Input folder not found: {INPUT_FOLDER}")
        print("Please create this folder and add your flyer images.")
        return

    all_deals = []
    
    # Loop through all files in the input folder
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(INPUT_FOLDER, filename)
            
            try:
                print(f"--- Processing: {filename} ---")
                mime_type, _ = mimetypes.guess_type(image_path)
                base64_image = encode_image_to_base64(image_path)
                
                # Call the AI to get the deals for this one flyer
                deals_list = call_gpt4o_vision_api(base64_image, mime_type, filename)
                
                if deals_list:
                    print(f"   > Extracted {len(deals_list)} deals from {filename}.")
                    # Add all deals from this flyer to our main list
                    all_deals.extend(deals_list)
                else:
                    print(f"   > No deals found or error in {filename}.")
                    
            except Exception as e:
                print(f"[Error] Failed to process {filename}: {e}")
            
            print("--------------------")

    # Write all collected deals to the final JSON file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_deals, f, indent=2, ensure_ascii=False)
        
        print(f"\n--- SUCCESS ---")
        print(f"Total deals extracted: {len(all_deals)}")
        print(f"All deals saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n[Error] Failed to write final JSON file: {e}")

if __name__ == "__main__":
    main()

