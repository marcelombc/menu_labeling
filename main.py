"""
Menu Labeling Pipeline
======================
Analyzes restaurant menus from PDFs and URLs to extract structured
characteristics.

Usage:
    python main.py --pdf <pdf> --output output/result.csv
    python main.py --url <url> --output output/result.json

Requirements:
    pip install requests beautifulsoup4 PyPDF2
"""

import argparse
import os
import uuid

from src.pipelines import MenuLabelingPipeline


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Menu Labeling Pipeline")
    parser.add_argument("--pdf", help="Path to single PDF file")
    parser.add_argument("--url", help="URL to scrape")
    parser.add_argument("--name", help="Restaurant name (for URL scraping)")
    parser.add_argument("--pdfs-dir", help="Directory containing PDF files")
    parser.add_argument(
        "--restaurants-json", help="Path to restaurants.json file"
    )
    parser.add_argument(
        "--output", required=True, help="Output file (.json or .csv)"
    )

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = MenuLabelingPipeline()

    # Process based on input type
    if args.pdf:
        pipeline.process_pdf(args.pdf)
    elif args.url:
        pipeline.process_url(args.url, args.name or "")
    elif args.pdfs_dir:
        pipeline.process_pdfs_directory(args.pdfs_dir)
    elif args.restaurants_json:
        pipeline.process_restaurants_json(args.restaurants_json)
    else:
        print(
            "Error: Please specify --pdf, --url, --pdfs-dir, or --restaurants-json"  # noqa
        )
        return

    original_output_path = args.output
    # Split into directory and filename
    directory, filename = os.path.split(original_output_path)
    name, ext = os.path.splitext(filename)
    # Generate a unique ID
    unique_id = uuid.uuid4()
    # Create new filename with UUID
    new_filename = f"{name}_{unique_id}{ext}"
    # Combine back into full path
    output_path = os.path.join(directory, new_filename)

    # Export results
    if output_path.endswith(".json"):
        pipeline.export_json(output_path)
    elif output_path.endswith(".csv"):
        pipeline.export_csv(output_path)
    else:
        print("Error: Output file must be .json or .csv")
        return

    # Print summary
    pipeline.print_summary()


if __name__ == "__main__":
    main()
