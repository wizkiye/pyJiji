import argparse
import asyncio
import json
import sys
from dataclasses import fields, is_dataclass
from datetime import datetime

from jiji import JiJi
from jiji.errors import UnknownError
from jiji.filters import price as price_filter
from jiji.filters import sort_by as sort_filter
from jiji.types import SortBy

try:
    from importlib.metadata import version as _package_version

    __version__ = _package_version("jiji")
except Exception:
    __version__ = "dev"

SORTS = {
    "recommended": SortBy.RECOMMENDED,
    "lowest-price": SortBy.LOWEST_PRICE,
    "highest-price": SortBy.HIGHEST_PRICE,
    "newest": SortBy.NEWEST,
    "oldest": SortBy.OLDEST,
}


def _serialize(obj):
    if is_dataclass(obj) and not isinstance(obj, type):
        return {
            field.name: _serialize(getattr(obj, field.name))
            for field in fields(obj)
            if not field.name.startswith("_")
        }
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (list, tuple)):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    return obj


def _print_json(result):
    print(json.dumps(_serialize(result), indent=2, ensure_ascii=False))


def _print_products(products, found=None, next_url=None):
    if found is not None:
        print(f"found {found} ads, showing {len(products)}")
    for index, product in enumerate(products, start=1):
        price = f"{product.price} ETB" if product.price else "price not set"
        print(f"{index:>3}. [{product.id}] {product.title} - {price}")
    if next_url:
        print("more results available (use --page to continue)")


def _print_product(product):
    print(f"[{product.id}] {product.title}")
    print(f"  price:    {product.formatted_price}")
    print(f"  category: {product.category_slug}")
    print(f"  regions:  {', '.join(product.regions_display or [])}")
    print(f"  posted:   {product.date_created:%Y-%m-%d %H:%M}")
    print(f"  seller:   {product.user.name} ({product.user.phone})")
    print(f"  link:     {product.share_link}")
    if product.description:
        print(f"  about:    {product.description[:300]}")


async def _handle_search(args):
    filters = None
    if args.min_price is not None or args.max_price is not None:
        filters = price_filter(args.min_price or 0, args.max_price or "")
    if args.sort:
        sort = sort_filter(SORTS[args.sort])
        filters = filters & sort if filters else sort
    result = await JiJi().search(args.query, page=args.page, filters=filters)
    if args.json:
        _print_json(result)
    else:
        _print_products(result.products, found=result.found, next_url=result.next_url)


async def _handle_categories(args):
    categories = await JiJi().get_categories()
    if args.json:
        _print_json(categories)
    else:
        for index, category in enumerate(categories, start=1):
            print(f"{index:>3}. [{category.id}] {category.name} ({category.total_ads} ads)")


async def _handle_trending(args):
    products = await JiJi().get_trending(page=args.page)
    if args.json:
        _print_json(products)
    else:
        _print_products(products)


async def _handle_recommendations(args):
    products = await JiJi().get_recommendations(size=args.size)
    if args.json:
        _print_json(products)
    else:
        _print_products(products)


async def _handle_product(args):
    product = await JiJi().get_product(args.product_id)
    if args.json:
        _print_json(product)
    else:
        _print_product(product)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="jiji",
        description="Jiji Ethiopia API CLI - search and browse jiji.com.et listings",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search ads")
    search_parser.add_argument("query", help="Search query, e.g. 'iphone 13'")
    search_parser.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    search_parser.add_argument("--min-price", type=int, help="Minimum price in ETB")
    search_parser.add_argument("--max-price", type=int, help="Maximum price in ETB")
    search_parser.add_argument("--sort", choices=sorted(SORTS), help="Sort order")
    search_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    search_parser.set_defaults(handler=_handle_search)

    categories_parser = subparsers.add_parser("categories", help="List all categories")
    categories_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    categories_parser.set_defaults(handler=_handle_categories)

    trending_parser = subparsers.add_parser("trending", help="List trending ads")
    trending_parser.add_argument("--page", type=int, default=1, help="Page number (default 1)")
    trending_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    trending_parser.set_defaults(handler=_handle_trending)

    recommendations_parser = subparsers.add_parser(
        "recommendations", help="List recommended ads"
    )
    recommendations_parser.add_argument(
        "--size", type=int, default=6, help="Number of ads (default 6)"
    )
    recommendations_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    recommendations_parser.set_defaults(handler=_handle_recommendations)

    product_parser = subparsers.add_parser("product", help="Show a single ad by id")
    product_parser.add_argument("product_id", type=int, help="Ad id")
    product_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    product_parser.set_defaults(handler=_handle_product)

    return parser


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        asyncio.run(args.handler(args))
    except UnknownError as error:
        parser.exit(1, f"error: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "\ninterrupted\n")


if __name__ == "__main__":
    main()
