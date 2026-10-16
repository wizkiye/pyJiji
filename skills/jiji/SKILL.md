---
name: jiji
description: Search and browse Jiji Ethiopia (jiji.com.et) classified listings via the `jiji` CLI or the pyJiji Python package. Use when the user asks about Ethiopian marketplace ads, prices in ETB, or listings for cars, phones, electronics, real estate, or jobs in Ethiopia, or wants to search Jiji.
---

# Jiji Ethiopia Listings

Uses the `jiji` CLI from the [pyJiji](https://github.com/wizkiye/pyJiji) package (unofficial Jiji Ethiopia API client). Covers jiji.com.et listings, prices in ETB, and seller info.

## Setup

```bash
pip install git+https://github.com/wizkiye/pyJiji.git
jiji --version
```

## CLI Reference

| Command | Purpose |
| --- | --- |
| `jiji search QUERY` | Search ads (`--page N`, `--min-price`, `--max-price`, `--sort <order>`) |
| `jiji product ID` | Full ad details by id |
| `jiji categories` | All categories (id, name, ad counts) |
| `jiji trending` | Trending ads (`--page N`) |
| `jiji recommendations` | Recommended ads (`--size N`) |

Sort orders: `recommended`, `lowest-price`, `highest-price`, `newest`, `oldest`.

Add `--json` to any command for machine-readable output. Always use `--json` when parsing results programmatically.

## Examples

```bash
jiji search "iphone 13" --max-price 50000 --sort lowest-price --json
jiji search "toyota corolla" --page 2
jiji product 3894190 --json
jiji categories --json
```

## Output Fields

- Search/trending/recommendation items: `id`, `title`, `price` (string, ETB, may be null), `price_type`, `image`, `date`, `region_id`, `user_id`, `count_images`.
- `product ID`: adds `description`, `attributes` (Brand, Condition, etc.), `images`, `user` (name/phone), `regions_display`, `share_link`, `date_created`.

## Workflow

1. Start with a specific multi-word query (`"iphone 13"`, `"toyota corolla"`) - single category words like `phone` resolve to the whole category.
2. Filter with `--min-price`/`--max-price` to narrow results; use `--sort lowest-price`.
3. Page through results with `--page N` (`found` in JSON tells you the total).
4. Fetch details for promising ids with `jiji product ID --json`.
5. Prices are strings with thousands separators (`"74,999"`); strip commas before numeric comparisons.

## Python API (async)

```python
import asyncio
from jiji import JiJi

async def main():
    client = JiJi()
    result = await client.search("iphone 13")
    product = await result.products[0].get_product()
    print(product.title, product.formatted_price)

asyncio.run(main())
```

## Notes

- jiji.com.et is the Ethiopian Jiji site; region `15` is Addis Ababa (see `regions_display` on products).
- `user_phone` is only present on some endpoints (e.g. recommendations, product details).
- If a command fails with a connection error, verify network access to `api.jiji.com.et`.
