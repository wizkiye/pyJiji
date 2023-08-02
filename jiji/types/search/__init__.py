from dataclasses import dataclass
from typing import List

from jiji.types import MinProduct


@dataclass
class SearchResult:
    products: List[MinProduct]
    found: int
    next_url: str | None

    @property
    def has_next(self) -> bool:
        return bool(self.next_url)
