from typing import Callable, Union, Dict, Any, Optional

from .types import SortBy


class Filter:
    def __call__(self) -> Dict[str, Any]:
        raise NotImplementedError

    def __and__(self, other):
        return And(self, other)


class And(Filter):
    def __init__(self, base, other):
        self.base = base
        self.other = other

    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        x = self.base(*args, **kwargs)
        y = self.other(x, *args, **kwargs)

        return y


CUSTOM_FILTER_NAME = "CustomFilter"


def create(func: Callable, name: str = None, **kwargs) -> Filter:
    return type(
        name or func.__name__ or CUSTOM_FILTER_NAME,
        (Filter,),
        {"__call__": func, **kwargs},
    )()


def price(
    min_price: Optional[Union[int, str]] = 0, max_price: Optional[Union[int, str]] = ""
) -> Filter:
    def func(flt, prev=None) -> dict:
        if prev:
            prev["price_max"] = flt.max_price
            prev["price_min"] = flt.min_price
            return prev
        return {"price_max": flt.max_price, "price_min": flt.min_price}

    return create(
        func,
        name="Price",
        min_price=min_price,
        max_price=max_price,
    )


#
#
# def condition(cond: Union[Conditions, str]) -> Filter:
#     cond = cond.value if isinstance(cond, Conditions) else cond
#
#     def func(flt, prev=None) -> dict:
#         if prev:
#             prev["condition"] = flt.condition
#             return prev
#         return {"condition": flt.condition}
#
#     return create(
#         func,
#         name="Condition",
#         condition=cond,
#     )


def sort_by(sort: Union[str, SortBy]) -> Filter:
    sort = sort.value if isinstance(sort, SortBy) else sort

    def func(flt, prev=None) -> dict:
        if prev:
            prev["sort"] = flt.sort
            return prev
        return {"sort": flt.sort}

    return create(
        func,
        name="Sort",
        sort=sort,
    )
