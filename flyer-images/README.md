# 📂 Flyer Images Directory

This directory is where you place flyer images for processing by the `process_flyers.py` script.

## 🎯 Where to Get Flyers

### **Best Sources:**
1. **Flipp.com** - https://flipp.com (Easiest, has most stores)
2. **BlackFriday.com** - https://blackfriday.com/ads
3. **BFAds.net** - https://bfads.net
4. **Retailer Websites:**
   - Walmart: https://walmart.com/shop/weekly-ads
   - Target: https://target.com/weeklyad
   - Best Buy: https://bestbuy.com/site/misc/weekly-ad/
   - Kohl's: https://kohls.com/sale-event/black-friday.jsp

---

## 📸 How to Download Flyers

### **Option 1: Screenshot (Quickest)**
- Mac: Press `Cmd + Shift + 4`, then drag to select area
- Windows: Press `Windows + Shift + S`
- Save as JPG or PNG

### **Option 2: Print to PDF, Then Convert**
1. Open flyer in browser
2. Press `Cmd + P` (Mac) or `Ctrl + P` (Windows)
3. Choose "Save as PDF"
4. Convert PDF to images using:
   - **Preview (Mac):** File → Export → Choose JPEG
   - **Online:** https://pdf2png.com or https://ilovepdf.com/pdf_to_jpg

---

## 📋 File Naming Convention (CRITICAL!)

**⚠️ IMPORTANT:** The script extracts the store name from your filename!

### **Required Format:**
```
{STORE_NAME}_description_pageXX.png
```

### **Examples:**
```
✅ walmart_bf2025_page01.jpg    → Store: Walmart
✅ target_deals_page01.png      → Store: Target
✅ bestbuy_electronics_p1.jpg   → Store: Best Buy
✅ kohls_home_page01.png        → Store: Kohl's

❌ Screenshot 2025-11-10.png    → Won't work (no store name!)
❌ page1.jpg                     → Won't work (no store name!)
```

**Rules:**
1. **MUST start with store name** (lowercase, no spaces: `walmart`, `target`, `bestbuy`)
2. Use underscores (`_`) to separate parts, not spaces
3. Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`

📖 **See `NAMING_GUIDE.md` for detailed instructions and examples**

---

## ✅ Ready to Process?

Once you have images in this folder:

```bash
# From project root
cd /Users/chindhamani/development/DealZen/DealZen_CodeBase

# Activate virtual environment
cd backend && source .venv/bin/activate && cd ..

# Run the processing script
python scripts/process_flyers.py
```

Or use the automated script:
```bash
./process_flyers_and_load.sh
```

---

## 🧪 Testing Tips

**For initial testing**, you can:
1. Start with just 1-2 flyer images
2. Choose flyers with clear, readable deals
3. Higher resolution images work better (300+ DPI)
4. Avoid blurry or low-quality images

---

## 📊 What Happens During Processing

1. Script reads all images from this folder
2. Sends each image to GPT-4o Vision API
3. Extracts deal data into structured JSON
4. Saves all deals to `scripts/deals.json`
5. You can then ingest into Weaviate

---

## 💰 Cost Estimate

GPT-4o Vision pricing:
- ~$0.01 - $0.05 per image (depending on resolution)
- For 10 flyer images: ~$0.10 - $0.50
- Your $5 credit = ~100-500 flyer images

---

## 🆘 Need Help?

If you have issues:
1. Check image quality (not blurry)
2. Ensure file format is supported (.jpg, .png)
3. Verify OPENAI_API_KEY is set in `backend/.env`
4. Check console output for errors
