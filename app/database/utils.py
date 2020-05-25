from dataclasses import dataclass
from math import ceil


@dataclass
class Pagination:
    current_page: int
    items_per_page: int
    total_items: int

    @property
    def total_pages(self):
        return ceil(self.total_items / self.items_per_page)


@dataclass
class PaginatedCollection:
    pagination: Pagination
    items: list
