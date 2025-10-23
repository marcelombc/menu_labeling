import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from src.analyzers import MenuAnalyzer
from src.extractors import PDFExtractor
from src.labels import MenuLabels
from src.scrapers import WebScraper


class MenuLabelingPipeline:
    """Main pipeline for processing multiple menus"""

    def __init__(self):
        self.results: List[MenuLabels] = []

    def process_pdf(self, pdf_path: str) -> MenuLabels:
        """Process a single PDF file"""
        print(f"Processing PDF: {pdf_path}")

        # Extract text
        text = PDFExtractor.extract(pdf_path)

        # Get restaurant name from filename
        # Warning: This may not always yield the correct restaurant name
        # name = Path(pdf_path).stem.replace("-", " ").replace("_", " ").title()  # noqa

        # Analyze
        analyzer = MenuAnalyzer(text)
        result = analyzer.analyze()
        result.source = pdf_path

        self.results.append(result)
        return result

    def process_url(self, url: str, name: str = "") -> MenuLabels:
        """Process a URL"""
        print(f"Processing URL: {url}")

        # Scrape text
        text = WebScraper.scrape(url)

        # Analyze
        analyzer = MenuAnalyzer(text, name)
        result = analyzer.analyze()
        result.source = url

        self.results.append(result)
        return result

    def process_restaurants_json(self, json_path: str) -> List[MenuLabels]:
        """Process restaurants from JSON file"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        restaurants = data.get("Restaurants", {})

        for name, url in restaurants.items():
            try:
                self.process_url(url, name.replace("_", " "))
                print("  ✓ Success")
            except Exception as e:
                print(f"  ✗ Error: {e}")

        return self.results

    def process_pdfs_directory(self, directory: str) -> List[MenuLabels]:
        """Process all PDFs in a directory"""
        pdf_files = list(Path(directory).glob("*.pdf"))

        for pdf_file in pdf_files:
            try:
                self.process_pdf(str(pdf_file))
                print("  ✓ Success")
            except Exception as e:
                print(f"  ✗ Error: {e}")

        return self.results

    def export_json(self, output_path: str):
        """Export results to JSON"""
        data = [asdict(result) for result in self.results]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results exported to JSON: {output_path}")

    def export_csv(self, output_path: str):
        """Export results to CSV"""
        if not self.results:
            print("No results to export")
            return

        # Get fieldnames from first result
        fieldnames = [
            "restaurant_name",
            "source",
            "regional_seasonal",
            "multi_course_menu",
            "small_menu",
            "large_menu",
            "vegan_options",
            "vegetarian_options",
            "gluten_free_options",
            "average_price",
            "main_dish_count",
            "vegan_percentage",
            "vegetarian_percentage",
            "gluten_free_count",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                writer.writerow(asdict(result))

        print(f"\n✓ Results exported to CSV: {output_path}")

    def print_summary(self):
        """Print summary of results"""
        if not self.results:
            print("No results to summarize")
            return

        print("\n" + "=" * 70)
        print("MENU LABELING SUMMARY")
        print("=" * 70)
        print(f"Total restaurants analyzed: {len(self.results)}")
        print(
            f"\nRegional & Seasonal: {sum(1 for r in self.results if r.regional_seasonal == 'Yes')}"  # noqa
        )
        print(
            f"Multi-course menus: {sum(1 for r in self.results if r.multi_course_menu == 'Yes')}"  # noqa
        )
        print(
            f"Small menus (≤4 mains): {sum(1 for r in self.results if r.small_menu == 'Yes')}"  # noqa
        )
        print(
            f"Large menus (>20 mains): {sum(1 for r in self.results if r.large_menu == 'Yes')}"  # noqa
        )
        print(
            f"With vegan options (≥30%): {sum(1 for r in self.results if r.vegan_options == 'Yes')}"  # noqa
        )
        print(
            f"With vegetarian options (≥30%): {sum(1 for r in self.results if r.vegetarian_options == 'Yes')}"  # noqa
        )
        print(
            f"With gluten-free options (≥2): {sum(1 for r in self.results if r.gluten_free_options == 'Yes')}"  # noqa
        )

        avg_price = sum(r.average_price for r in self.results) / len(
            self.results
        )
        print(f"\nAverage price across all: {avg_price:.2f} CHF")
