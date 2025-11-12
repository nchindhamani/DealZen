# 🎯 Quick Answers to Common Questions

## ❓ Question 1: Screenshots Have Overlapping Pages - Will It Work?

### ✅ **Answer: YES! The script is now smart about this.**

**What I updated:**
1. **System Prompt:** Added instruction to "ignore partial/cut-off deals at edges"
2. **User Message:** Explicitly tells GPT-4o "This may be a screenshot with edges of other pages visible. Focus only on the main, center content."

**Result:**
- GPT-4o Vision will focus on the center/main content
- Ignores partial products at corners and edges
- Only extracts complete, fully visible deals

**Your action:** Just take normal screenshots - don't worry about perfect cropping! ✅

---

## ❓ Question 2: Pages Don't Show Store Name - How Will You Know?

### ✅ **Answer: The filename tells the script which store it is!**

**How it works:**
```python
# Filename: "walmart_bf2025_page01.png"
# Script extracts: "walmart"
# Tells GPT-4o: "STORE NAME: WALMART"
```

**Critical Naming Rule:**
```
✅ GOOD:
walmart_page01.png        → Store: Walmart
target_bf_page01.jpg      → Store: Target
bestbuy_deals_p1.png      → Store: Best Buy

❌ BAD:
Screenshot_001.png        → Unknown store!
page1.jpg                 → Unknown store!
flyer.png                 → Unknown store!
```

**The Formula:**
```
{STORE_NAME}_anything_else.png
     ↑
     └── This part (before first underscore) = Store Name
```

---

## 📍 Where to Place Images?

```
/Users/chindhamani/development/DealZen/DealZen_CodeBase/flyer-images/
```

Put ALL your flyer screenshots in this folder.

---

## 📝 Example: 11-Page Walmart Flyer

### **Scenario:**
You screenshot an 11-page Walmart flyer from Flipp.com. Some pages show Walmart logo, some don't.

### **What to do:**
```bash
# 1. Name all files starting with "walmart"
walmart_bf2025_page01.png
walmart_bf2025_page02.png
walmart_bf2025_page03.png
...
walmart_bf2025_page11.png

# 2. Place in flyer-images/ folder

# 3. Run script
./process_flyers_and_load.sh
```

### **What happens:**
1. Script reads filename: `walmart_bf2025_page01.png`
2. Extracts store: `walmart`
3. Tells GPT-4o: "All deals are from WALMART"
4. GPT-4o extracts deals with `"store": "Walmart"`
5. **Even if page doesn't show logo, we know it's Walmart!** ✅

---

## 🎯 Real-World Workflow

### **Complete Example:**

```bash
# === You have 3 flyers ===
# Walmart (11 pages), Target (8 pages), Best Buy (5 pages)

# === Step 1: Take screenshots ===
# From Flipp.com or PDF viewer

# === Step 2: Rename files ===
# Walmart
walmart_bf_page01.png
walmart_bf_page02.png
...
walmart_bf_page11.png

# Target
target_thanksgiving_page01.png
target_thanksgiving_page02.png
...
target_thanksgiving_page08.png

# Best Buy
bestbuy_doorbuster_page01.png
bestbuy_doorbuster_page02.png
...
bestbuy_doorbuster_page05.png

# === Step 3: Move to flyer-images/ ===
# All 24 images in one folder

# === Step 4: Run script ===
cd /Users/chindhamani/development/DealZen/DealZen_CodeBase
./process_flyers_and_load.sh

# === Result ===
# All 24 pages processed
# Deals correctly tagged with Walmart, Target, or Best Buy
# Even if individual pages don't show store logo!
```

---

## 💡 Key Takeaways

1. **Overlapping pages?** → No problem! Script focuses on center content ✅
2. **No store logo on page?** → Filename provides store name ✅
3. **Multiple stores?** → Name files correctly, process all at once ✅
4. **Multi-page flyers?** → Each page = one image, name sequentially ✅

---

## 🚀 You're Ready!

**Next steps:**
1. Go to Flipp.com or retailer website
2. Take screenshots of 1-2 flyers (start small for testing)
3. Name them: `walmart_page01.png`, `walmart_page02.png`, etc.
4. Place in `flyer-images/` folder
5. Run: `./process_flyers_and_load.sh`
6. Test in frontend! 🎉

---

## 📚 More Details

- **Naming Guide:** See `flyer-images/NAMING_GUIDE.md`
- **Download Guide:** See `FLYER_DOWNLOAD_GUIDE.md`
- **Full Setup:** See `README.md`

