from dataclasses import dataclass
from typing import List, Union

from jiji.types import MinProduct


@dataclass
class SearchResult:
    products: List[MinProduct]
    found: int
    next_url: Union[str, None]

    @property
    def has_next(self) -> bool:
        return bool(self.next_url)
