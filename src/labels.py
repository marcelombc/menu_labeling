from dataclasses import dataclass


@dataclass
class MenuLabels:
    """Menu labeling results"""

    restaurant_name: str
    source: str
    regional_seasonal: str  # "Yes" or "No"
    multi_course_menu: str
    small_menu: str
    large_menu: str
    vegan_options: str
    vegetarian_options: str
    gluten_free_options: str
    average_price: float

    # Additional details for reference
    main_dish_count: int = 0
    vegan_percentage: float = 0.0
    vegetarian_percentage: float = 0.0
    gluten_free_count: int = 0
