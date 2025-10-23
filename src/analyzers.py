import re
from typing import Dict, List, Optional, Tuple

from src.labels import MenuLabels


class MenuAnalyzer:
    """Analyze menu text and generate labels"""

    # Keywords for detection
    REGIONAL_KEYWORDS = [
        "schweiz",
        "swiss",
        "regional",
        "lokal",
        "local",
        "freiland",
        "basel",
        "zürich",
        "bern",
        "km",
        "aus der region",
        "heimisch",
    ]

    SEASONAL_KEYWORDS = [
        "saisonal",
        "seasonal",
        "season",
        "marktfrisch",
        "market fresh",
        "sommer",
        "winter",
        "herbst",
        "frühling",
        "spring",
        "summer",
        "autumn",
        "fall",
    ]

    VEGAN_MARKERS = ["vegan", "v+", "(v+)", "pflanzlich", "plant-based"]
    VEGETARIAN_MARKERS = ["vegetarisch", "vegetarian", " v ", "(v)", "veggie"]
    GLUTEN_FREE_MARKERS = [
        "glutenfrei",
        "gluten-free",
        "gluten free",
        "gf ",
        "(gf)",
    ]

    COURSE_PATTERN = r"(\d+)[-\s]?(gang|course|gänge|gericht)"
    MENU_CONCEPTS = ["tavolata", "degustation", "tasting menu", "set menu"]

    def __init__(self, text: str, restaurant_name: str = ""):
        self.text = text
        self.text_lower = text.lower()
        print(restaurant_name)
        self.restaurant_name = restaurant_name or self._extract_name()
        self.items = self._extract_items()
        self.main_dishes = self._filter_main_dishes()

    def _extract_name(self) -> str:
        """Extract restaurant name from first few lines"""
        lines = self.text.split("\n")
        print(lines)
        for line in lines[:5]:
            line = line.strip()
            if 3 < len(line) < 50 and not self._extract_price(line):
                return line
        return "Unknown Restaurant"

    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        patterns = [
            r"(\d+)[,\.](\d{2})\s*$",
            r"(\d+)\s*$",
            r"(\d+)[,\.](\d{2})\s*(?:CHF|EUR|€|CHF)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return float(f"{groups[0]}.{groups[1]}")
                elif len(groups) == 1:
                    val = float(groups[0])
                    if val > 5:  # Sanity check
                        return val
        return None

    def _extract_items(self) -> List[Dict]:
        """Extract menu items with prices"""
        items = []
        lines = self.text.split("\n")
        current_section = "unknown"

        # Section keywords
        section_keywords = {
            "starter": [
                "vorspeise",
                "antipasti",
                "starter",
                "appetizer",
                "insalat",
                "salat",
                "salad",
            ],
            "main": [
                "hauptgericht",
                "hauptgang",
                "main",
                "carni",
                "pesci",
                "fleisch",
                "fisch",
                "meat",
                "fish",
                "pasta",
                "risotto",
                "dall",
            ],
            "dessert": ["dessert", "nachspeise", "dolci", "sweet", "glacé"],
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Update section
            line_lower = line.lower()
            for section, keywords in section_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    current_section = section
                    break

            # Extract price
            price = self._extract_price(line)
            if price and price > 5 and price < 200:
                # Remove price from name
                name = re.sub(
                    r"[\d,\.]+\s*(?:CHF|EUR|€)?\s*$", "", line
                ).strip()

                # Check dietary markers
                is_vegan = any(
                    marker in line_lower for marker in self.VEGAN_MARKERS
                )
                is_vegetarian = (
                    any(
                        marker in line_lower
                        for marker in self.VEGETARIAN_MARKERS
                    )
                    or is_vegan
                )
                is_gf = any(
                    marker in line_lower for marker in self.GLUTEN_FREE_MARKERS
                )

                items.append(
                    {
                        "name": name,
                        "price": price,
                        "section": current_section,
                        "vegan": is_vegan,
                        "vegetarian": is_vegetarian,
                        "gluten_free": is_gf,
                    }
                )

        return items

    def _filter_main_dishes(self) -> List[Dict]:
        """Filter to main dishes only"""
        mains = []
        for item in self.items:
            # Main section OR price >= 20 (but not dessert)
            if item["section"] == "main" or (
                item["price"] >= 20 and item["section"] != "dessert"
            ):
                mains.append(item)
        return mains

    def check_regional_seasonal(self) -> str:
        """Check for regional AND seasonal focus"""
        has_regional = any(
            kw in self.text_lower for kw in self.REGIONAL_KEYWORDS
        )
        has_seasonal = any(
            kw in self.text_lower for kw in self.SEASONAL_KEYWORDS
        )

        return "Yes" if (has_regional and has_seasonal) else "No"

    def check_multi_course(self) -> str:
        """Check for multi-course menu (≥4 courses)"""
        # Look for explicit course numbers
        matches = re.findall(self.COURSE_PATTERN, self.text_lower)
        if matches:
            course_counts = [int(m[0]) for m in matches if m[0].isdigit()]
            if any(count >= 4 for count in course_counts):
                return "Yes"

        # Look for menu concepts
        if any(concept in self.text_lower for concept in self.MENU_CONCEPTS):
            return "Yes"

        return "No"

    def check_small_menu(self) -> str:
        """Check if menu has max 4 main dishes"""
        return "Yes" if len(self.main_dishes) <= 4 else "No"

    def check_large_menu(self) -> str:
        """Check if menu has >20 main dishes"""
        return "Yes" if len(self.main_dishes) > 20 else "No"

    def check_vegan_options(self) -> Tuple[str, float]:
        """Check if at least 30% vegan mains"""
        if not self.main_dishes:
            return "No", 0.0

        vegan_count = sum(1 for item in self.main_dishes if item["vegan"])
        percentage = (vegan_count / len(self.main_dishes)) * 100

        return ("Yes" if percentage >= 30 else "No"), percentage

    def check_vegetarian_options(self) -> Tuple[str, float]:
        """Check if at least 30% vegetarian mains"""
        if not self.main_dishes:
            return "No", 0.0

        veg_count = sum(1 for item in self.main_dishes if item["vegetarian"])
        percentage = (veg_count / len(self.main_dishes)) * 100

        return ("Yes" if percentage >= 30 else "No"), percentage

    def check_gluten_free_options(self) -> Tuple[str, int]:
        """Check if at least 2 gluten-free mains"""
        if not self.main_dishes:
            return "No", 0

        # Explicit markers
        gf_count = sum(1 for item in self.main_dishes if item["gluten_free"])

        # Natural gluten-free items
        gf_keywords = ["risotto", "salat", "salad", "grilled", "gegrillt"]
        for item in self.main_dishes:
            if any(kw in item["name"].lower() for kw in gf_keywords):
                gf_count += 1

        # Check text for general GF mention
        has_gf_mention = any(
            marker in self.text_lower for marker in self.GLUTEN_FREE_MARKERS
        )

        return ("Yes" if (gf_count >= 2 or has_gf_mention) else "No"), gf_count

    def calculate_average_price(self) -> float:
        """Calculate average price for starter + main"""
        starters = [
            item for item in self.items if item["section"] == "starter"
        ]
        mains = [
            item
            for item in self.items
            if item["section"] == "main" or item["price"] >= 20
        ]

        if not starters or not mains:
            # Fallback: average of all items
            all_prices = [item["price"] for item in self.items]
            return (
                round(sum(all_prices) / len(all_prices), 2)
                if all_prices
                else 0.0
            )

        avg_starter = sum(s["price"] for s in starters) / len(starters)
        avg_main = sum(m["price"] for m in mains) / len(mains)

        return round(avg_starter + avg_main, 2)

    def analyze(self) -> MenuLabels:
        """Perform complete analysis"""
        vegan_result, vegan_pct = self.check_vegan_options()
        veg_result, veg_pct = self.check_vegetarian_options()
        gf_result, gf_count = self.check_gluten_free_options()

        return MenuLabels(
            restaurant_name=self.restaurant_name,
            source="",  # To be filled by caller
            regional_seasonal=self.check_regional_seasonal(),
            multi_course_menu=self.check_multi_course(),
            small_menu=self.check_small_menu(),
            large_menu=self.check_large_menu(),
            vegan_options=vegan_result,
            vegetarian_options=veg_result,
            gluten_free_options=gf_result,
            average_price=self.calculate_average_price(),
            main_dish_count=len(self.main_dishes),
            vegan_percentage=round(vegan_pct, 1),
            vegetarian_percentage=round(veg_pct, 1),
            gluten_free_count=gf_count,
        )
