# Menu Labeling Pipeline

A Python script for automated menu analysis and labeling from PDFs and restaurant URLs.

## Setup and run Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Installation

```bash
pip install requests beautifulsoup4 PyPDF2
```

## Quick Start

### Analyze a Single PDF

```bash
python main.py --pdf data/speisekarte-de.pdf --output output/result.json
```

### Analyze Multiple PDFs

```bash
python main.py --pdfs-dir <some_directory_with_menu_pdfs> --output results.csv
```

### Analyze from URLs (restaurants.json)

```bash
python main.py --restaurants-json data/restaurants.json --output output/results.json
```

```bash
python main.py --restaurants-json data/restaurants.json --output output/results.json
```

### Analyze a Single URL

```bash
python main.py --url <some_restaurant_url> --name <some_restaurant_name> --output output/results.csv
```

## Output Format

### JSON Output
```json
[
  {
    "restaurant_name": "Goldener Sternen Basel",
    "source": "data/speisekarte-de.pdf",
    "regional_seasonal": "Yes",
    "multi_course_menu": "Yes",
    "small_menu": "No",
    "large_menu": "Yes",
    "vegan_options": "No",
    "vegetarian_options": "No",
    "gluten_free_options": "No",
    "average_price": 64.01,
    "main_dish_count": 22,
    "vegan_percentage": 0.0,
    "vegetarian_percentage": 0.0,
    "gluten_free_count": 0
  }
]
```

### CSV Output
```csv
restaurant_name,source,regional_seasonal,multi_course_menu,small_menu,large_menu,vegan_options,vegetarian_options,gluten_free_options,average_price,main_dish_count,vegan_percentage,vegetarian_percentage,gluten_free_count
Goldener Sternen Basel,speisekarte-de.pdf,Yes,Yes,No,No,No,Yes,Yes,64.01,22,0.0,0.0,0
```

## Labeling Criteria

| Label | Criteria |
|-------|----------|
| **Regional & Seasonal** | Menu must mention BOTH regional sourcing AND seasonal ingredients |
| **Multi-course Menu** | Offers ≥4 courses (excluding sharing concepts) |
| **Small Menu** | Maximum 4 main dishes |
| **Large Menu** | More than 20 main dishes |
| **Vegan Options** | At least 30% of main dishes are vegan |
| **Vegetarian Options** | At least 30% of main dishes are vegetarian |
| **Gluten-free Options** | At least 2 gluten-free main dishes |
| **Average Price** | Average cost of 1 starter + 1 main dish |

## Input File Formats

### restaurants.json
```json
{
  "Restaurants": {
    "chez_smith": "https://chez-smith.ch/de/",
    "La_Catedral": "https://www.lacatedral.ch/menu",
    "lulu": "https://www.lulu-zh.ch/de/",
    "Hermanseck": "https://www.hermanseck.ch/",
    "Grotto Reale": "https://grottoreale.ch/",
    "Miki": "http://miki.ch/",
    "China Restaurant 99": "http://chinarestaurant-99.ch/",
    "Lee House": "https://www.leehouse.ch/menu.html",
    "Gamper_Restaurant": "http://gamper-restaurant.ch/",
    "Neue_Taverne": "https://neuetaverne.ch/",
    "Wirtschaft_im_Franz": "http://www.wirtschaftimfranz.ch/"
  }
}
```

## Usage in a Pipeline

```python
from src.pipelines import MenuLabelingPipeline

# Initialize pipeline
pipeline = MenuLabelingPipeline()

# Process PDFs
pipeline.process_pdf("menu1.pdf")
pipeline.process_pdf("menu2.pdf")

# Process URLs
pipeline.process_url("https://restaurant.com/menu", "Restaurant Name")

# Export results
pipeline.export_json("results.json")
pipeline.export_csv("results.csv")
pipeline.print_summary()
```

## Example with Provided Files

```bash
# Analyze the two sample PDFs
python main.py --pdf data/speisekarte-de.pdf --output output/result.json
python main.py --pdf data/Verdi-Speisekarte-05.25.pdf --output output/result.json

# Process all restaurants from JSON
python main.py --restaurants-json data/restaurants.json --output output/results.csv
```

## Detection Logic

### Regional & Seasonal Detection
- **Regional keywords**: "schweiz", "swiss", "regional", "lokal", "freiland", "basel", "km"
- **Seasonal keywords**: "saisonal", "seasonal", "marktfrisch", "sommer", "winter"
- **Result**: "Yes" only if BOTH regional AND seasonal keywords found

### Dietary Options Detection
- **Vegan markers**: "vegan", "v+", "(v+)", "pflanzlich"
- **Vegetarian markers**: "vegetarisch", "vegetarian", "(v)", "v "
- **Gluten-free markers**: "glutenfrei", "gluten-free", "gf"

### Menu Item Classification
- **Starters**: Items in sections like "vorspeise", "antipasti", "starter"
- **Mains**: Items in "hauptgericht", "main", "pasta", "risotto" OR price ≥ 20 CHF
- **Desserts**: Items in "dessert", "dolci", "glacé" sections

## Customization

Modify the keywords in the `MenuAnalyzer` class:

```python
class MenuAnalyzer:
    REGIONAL_KEYWORDS = ['your', 'custom', 'keywords']
    SEASONAL_KEYWORDS = ['seasonal', 'keywords']
    # ... etc
```

## Troubleshooting

**Error: "PyPDF2 not installed"**
```bash
pip install PyPDF2
```

**Error: "requests/beautifulsoup4 not installed"**
```bash
pip install requests beautifulsoup4
```

**Poor extraction from PDF**
- Try installing `pdfplumber` for better quality: `pip install pdfplumber`
- Modify code to use pdfplumber instead of PyPDF2

**URL scraping not working**
- Check if website requires JavaScript (script only handles static HTML)
- Some sites block scrapers - you may need to manually download the menu

## Notes

- Price extraction assumes CHF/EUR format
- Works best with well-structured menus
- Manual review recommended for critical applications
- Confidence varies based on menu formatting quality

## Future Improvements

- Add support for pdfplumber (better PDF extraction)
- OCR support for image-based PDFs
- Multi-language support
- ML-based classification
- Caching for repeated URLs
- Parallel processing for batch jobs
