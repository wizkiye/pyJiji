from enum import Enum


class SortBy(Enum):
    """Sort by."""

    RECOMMENDED = "rel"
    LOWEST_PRICE = "price"
    HIGHEST_PRICE = "price_desc"
    NEWEST = "new"
    OLDEST = "date-asc-rank"
