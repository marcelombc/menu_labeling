try:
    import PyPDF2

    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("Warning: PyPDF2 not installed. PDF extraction disabled.")


class PDFExtractor:
    """Extract text from PDF files"""

    @staticmethod
    def extract(pdf_path: str) -> str:
        """Extract text from PDF"""
        if not HAS_PDF:
            raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")

        text = []
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)

        return "\n".join(text)
