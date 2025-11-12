# 📝 Image Naming & Placement Guide

## 🎯 **Where to Place Images**

Place ALL flyer images in this directory:
```
/Users/chindhamani/development/DealZen/DealZen_CodeBase/flyer-images/
```

---

## 🏷️ **Critical: File Naming Convention**

### **Why Naming Matters:**
- ✅ The script extracts the **store name** from the filename
- ✅ Even if pages don't show store logo, we'll know which store it is
- ✅ Helps organize and track which flyers you've processed

---

## 📋 **Naming Format:**

```
{STORE_NAME}_{description}_{page_number}.{extension}

Examples:
walmart_bf2025_page01.png
walmart_bf2025_page02.png
walmart_electronics_page01.jpg
target_black_friday_page01.png
bestbuy_doorbuster_page01.png
kohls_home_deals_page01.jpg
```

### **Required Parts:**

1. **STORE_NAME** (REQUIRED - must be first)
   - Examples: `walmart`, `target`, `bestbuy`, `kohls`, `costco`, `amazon`
   - Use lowercase, no spaces
   - This tells the script which store the deals belong to

2. **Description** (Optional but helpful)
   - Examples: `bf2025`, `black_friday`, `electronics`, `thanksgiving`
   - Helps you remember what the flyer contains

3. **Page Number** (Recommended for multi-page flyers)
   - Examples: `page01`, `page02`, `p1`, `p2`
   - Use leading zeros for better sorting (01, 02, not 1, 2)

4. **Extension** (Auto-detected)
   - Supported: `.png`, `.jpg`, `.jpeg`, `.webp`

---

## ✅ **Good Examples:**

```
✅ walmart_page01.png          → Store: Walmart
✅ walmart_page02.png          → Store: Walmart
✅ target_bf_page01.jpg        → Store: Target
✅ bestbuy_electronics.png     → Store: Best Buy
✅ kohls_home_deals_p1.jpg     → Store: Kohl's
✅ costco_thanksgiving_01.png  → Store: Costco
```

---

## ❌ **Bad Examples:**

```
❌ Screenshot 2025-11-10.png   → No store name!
❌ page1.jpg                   → No store name!
❌ deals.png                   → No store name!
❌ IMG_1234.jpg                → No store name!
❌ Black Friday Walmart.png    → Spaces (use underscores), store not first
```

---

## 🔧 **How the Script Extracts Store Name**

The script uses this logic:
```python
# Example filename: "walmart_bf2025_page01.png"
store_name = filename.split('_')[0]  # Gets "walmart"
# Then converts to "WALMART" and tells GPT-4o
```

**What this means:**
- The text BEFORE the first underscore (`_`) becomes the store name
- `walmart_page1.png` → Store: "WALMART"
- `target_deals.jpg` → Store: "TARGET"
- `bestbuy_electronics_page03.png` → Store: "BESTBUY"

---

## 📚 **Real-World Example:**

### **Scenario: You have an 11-page Walmart flyer**

**Step 1: Take screenshots** (from Flipp.com or PDF)

**Step 2: Name them systematically:**
```
walmart_bf2025_page01.png
walmart_bf2025_page02.png
walmart_bf2025_page03.png
walmart_bf2025_page04.png
walmart_bf2025_page05.png
walmart_bf2025_page06.png
walmart_bf2025_page07.png
walmart_bf2025_page08.png
walmart_bf2025_page09.png
walmart_bf2025_page10.png
walmart_bf2025_page11.png
```

**Step 3: Place in this directory**
```bash
/Users/chindhamani/development/DealZen/DealZen_CodeBase/flyer-images/
```

**Step 4: Run the script**
```bash
cd /Users/chindhamani/development/DealZen/DealZen_CodeBase
./process_flyers_and_load.sh
```

**Result:** All 11 pages will be processed with store name "Walmart" ✅

---

## 🔄 **Multiple Stores in One Session**

You can process flyers from multiple stores at once:

```
flyer-images/
├── walmart_bf_page01.png
├── walmart_bf_page02.png
├── walmart_bf_page03.png
├── target_thanksgiving_page01.png
├── target_thanksgiving_page02.png
├── bestbuy_doorbuster_page01.png
├── kohls_home_deals_page01.png
└── costco_electronics_page01.png
```

The script will:
1. Process all images
2. Extract store name from each filename
3. Assign correct store to each deal
4. Combine all into one `deals.json`

---

## 🛠️ **Quick Rename Tips**

### **Mac Terminal (Batch Rename):**
```bash
# If you have badly named files, rename them:
cd flyer-images/

# Rename all Screenshot files to walmart_page_XX.png
i=1
for file in Screenshot*.png; do
  mv "$file" "walmart_page_$(printf %02d $i).png"
  ((i++))
done
```

### **Using Finder (Mac):**
1. Select all images from same store
2. Right-click → "Rename X items"
3. Format: `walmart_page`
4. Add number sequence starting at 1

---

## 📊 **Current Directory Status**

To see your files:
```bash
cd /Users/chindhamani/development/DealZen/DealZen_CodeBase/flyer-images
ls -lh
```

To check store names that will be extracted:
```bash
ls *.{png,jpg,jpeg} | awk -F'_' '{print $1}' | sort -u
```

---

## ✅ **Ready to Process?**

Once your files are named correctly:
```bash
cd /Users/chindhamani/development/DealZen/DealZen_CodeBase
./process_flyers_and_load.sh
```

The script will:
1. ✅ Read all images from this folder
2. ✅ Extract store name from filename
3. ✅ Tell GPT-4o which store each flyer is from
4. ✅ Handle overlapping page edges (focus on center content)
5. ✅ Generate `scripts/deals.json` with all deals

