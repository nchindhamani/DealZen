# Flyer Images Folder

## Purpose

This folder is where you place your retail flyer images for processing by the `process_flyers.py` script.

## Supported Formats

- `.png`
- `.jpg`
- `.jpeg`

## File Naming Convention (Recommended)

For best results, name your files with the store name at the beginning:

- `bestbuy_blackfriday_2025.jpg`
- `walmart_thanksgiving_deals.png`
- `target_cyber_monday.jpg`

The script will use the first part of the filename (before the underscore) as a hint for the store name.

## Usage

1. **Add flyer images** to this folder
2. **Run the processing script:**
   ```bash
   cd scripts
   python process_flyers.py
   ```
3. **The script will:**
   - Read all images from this folder
   - Send them to GPT-4o Vision API
   - Extract deal information
   - Save results to `scripts/deals.json`

## Example

```bash
flyer-images/
├── bestbuy_blackfriday_page1.jpg
├── bestbuy_blackfriday_page2.jpg
├── walmart_deals_nov27.png
└── target_electronics_sale.jpg
```

## Notes

- Large images may take longer to process
- Processing time depends on the number of deals in the flyer
- API costs apply per image processed (GPT-4o Vision pricing)
- Keep original flyers for reference/backup

## After Processing

Once `deals.json` is generated in the `scripts/` folder, you can:

1. Review the extracted deals for accuracy
2. Run the ingestion script: `python ingest_data.py`
3. Start your DealZen application

---

**Ready to process flyers? Add your images here and run `python process_flyers.py`!**

