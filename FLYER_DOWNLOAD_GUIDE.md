# 🛒 Quick Flyer Download Guide

## 🎯 **Easiest Method: Flipp.com Screenshots**

### Step-by-Step:

1. **Go to Flipp.com**
   ```
   https://flipp.com
   ```

2. **Search for a Store**
   - Type "Walmart" or "Best Buy" in search
   - Click on the store's current flyer

3. **Take Screenshots**
   - **Mac:** Press `Cmd + Shift + 4`
   - **Windows:** Press `Windows + Shift + S`
   - Drag to select the flyer area
   - Screenshot saves automatically

4. **Save to flyer-images folder**
   ```bash
   # Move your screenshots here:
   /Users/chindhamani/development/DealZen/DealZen_CodeBase/flyer-images/
   ```

5. **Rename Files**
   ```
   Before: Screenshot 2025-11-10 at 3.45.21 PM.png
   After:  walmart_bf2025_electronics.png
   ```

---

## 🔥 **Quick Links to Current Flyers**

### **Active Now (November 2024/2025):**

| Store | Link | Type |
|-------|------|------|
| Walmart | https://www.walmart.com/shop/weekly-ads | Weekly Ad |
| Target | https://www.target.com/weeklyad | Weekly Ad |
| Best Buy | https://www.bestbuy.com/site/electronics/weekly-ad/ | Weekly Ad |
| Kohl's | https://www.kohls.com/sale-event/black-friday.jsp | Black Friday |
| Costco | https://www.costco.com/coupon-book.html | Coupon Book |

### **Flyer Aggregators:**
- **Flipp**: https://flipp.com (Best for screenshots)
- **Black Friday Ads**: https://blackfriday.com/ads
- **BF Ads**: https://bfads.net

---

## 💡 **Pro Tips**

### **For Best Results:**
- ✅ Use clear, high-resolution images
- ✅ Capture full deals (don't cut off text)
- ✅ One flyer page = one image file
- ✅ Name files clearly (include store name)

### **Avoid:**
- ❌ Blurry or pixelated images
- ❌ Multiple pages in one image (split them)
- ❌ Images with glare or shadows

---

## 🚀 **Ready in 5 Minutes**

### **Quick Test (1-2 Flyers):**

```bash
# 1. Download 1-2 flyers from Flipp.com (screenshot method)
# 2. Save to flyer-images/ folder
# 3. Run this command:

cd /Users/chindhamani/development/DealZen/DealZen_CodeBase
./process_flyers_and_load.sh
```

**What it does:**
- Reads images from `flyer-images/`
- Extracts deals using GPT-4o Vision
- Loads into Weaviate
- Ready to test in frontend!

---

## 💰 Cost Reference

**GPT-4o Vision Pricing (2024):**
- Input: $2.50 per 1M tokens
- Output: $10 per 1M tokens
- **Per Image:** ~$0.01 - $0.05 (typical flyer)

**Your $5 Credit:**
- Can process ~100-500 flyer images
- More than enough for Black Friday event!

---

## 📝 Example Workflow

```bash
# Step 1: Download flyer
# Go to flipp.com → Search "Walmart" → Screenshot

# Step 2: Save to folder
# Save as: walmart_bf2025_electronics.png

# Step 3: Process
cd /Users/chindhamani/development/DealZen/DealZen_CodeBase
./process_flyers_and_load.sh

# Step 4: Test in frontend
# Open browser: http://localhost:5173
# Ask: "Show me TV deals"
```

---

## 🆘 **Stuck? Try This:**

### **Can't Find PDF Download?**
→ Use screenshots! They work just as well.

### **PDF Instead of Images?**
→ Convert using Preview (Mac):
   1. Open PDF in Preview
   2. File → Export
   3. Format: JPEG
   4. Save

### **Images Too Large?**
→ That's fine! Script handles it automatically.

---

## 📞 **Next Step**

Once you have 1-2 flyer images in `flyer-images/` folder, let me know and we'll process them! 🚀

