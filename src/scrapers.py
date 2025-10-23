try:
    import requests
    from bs4 import BeautifulSoup

    HAS_WEB_SCRAPING = True
except ImportError:
    HAS_WEB_SCRAPING = False
    print("Warning: beautifulsoup4 not installed. Web scraping disabled.")


class WebScraper:
    """Scrape menu text from restaurant URLs"""

    @staticmethod
    def scrape(url: str) -> str:
        """Scrape text from URL"""
        if not HAS_WEB_SCRAPING:
            raise ImportError("beautifulsoup4 not found!")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"  # noqa
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator="\n")

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = "\n".join(line for line in lines if line)

        return text
