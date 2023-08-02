from datetime import datetime
from typing import List

import httpx

from jiji import constants
from jiji.errors import UnknownError
from jiji.filters import Filter
from jiji.types import (
    MinProduct,
    Product,
    Attribute,
    Category,
    Price,
    User,
    PriceValuation,
    Image,
    SearchResult,
)


class JiJi:
    def __init__(self):
        self._session = httpx.AsyncClient(
            headers={
                "User-Agent": constants.USER_AGENT,
            }
        )
        self._BASE_URL = "https://api.jiji.com.et/api/v1/{}"

    async def _process_request(
        self,
        endpoint: str,
        json: dict = None,
        **kwargs,
    ) -> dict:
        method = "POST" if json else "GET"
        try:
            res = await self._session.request(
                method=method,
                url=self._BASE_URL.format(endpoint),
                timeout=30,
                json=json,
                **kwargs,
            )
            return res.json()
        except httpx.HTTPError:
            res = await self._session.request(
                method=method,
                url=self._BASE_URL.format(endpoint),
                timeout=30,
                json=json,
                **kwargs,
            )
            return res.json()
        except Exception as e:
            raise UnknownError(str(e))

    @staticmethod
    def _dict_to_product(res: dict) -> Product:
        return Product(
            id=res["id"],
            guid=res["guid"],
            category_slug=res.get("category_slug"),
            title=res["title"],
            region_id=res["region_id"],
            regions_display=res["regions_display"],
            published=res.get("published"),
            date_created=datetime.fromtimestamp(res["date_created"]),
            date_moderated=datetime.fromtimestamp(res["date_moderated"])
            if res.get("date_moderated")
            else None,
            review_estimation=res["review_estimation"],
            price=res["price"],
            price_history=res["price_history"],
            formatted_price=res["formatted_price"],
            price_obj=Price(
                value=res["price_obj"]["value"],
                view=res["price_obj"]["view"],
                period=res["price_obj"]["period"],
                bulk=res["price_obj"]["bulk"],
                price=res["price_obj"]["price"],
                text=res["price_obj"]["text"],
            ),
            price_type=res["price_type"],
            attributes=[Attribute(**attr) for attr in res["attributes"]],
            description=res["description"],
            video=res["video"],
            user=User(
                id=res["user_id"],
                phone=res["user_phone"],
                name=res["user_name"],
                avatar_url=res["user_avatar_url"],
                phones=res["user_phones"],
                email=res["user_email"],
                user_registered=res["user_registered"],
                last_seen=res["last_seen"],
            ),
            category_id=res["category_id"],
            tags=res["tags"],
            long_tag=res["longest_tag"],
            rating=res["rating"],
            page_views=res["page_views"],
            moderation_reasons=res["moderation_reasons"],
            on_hold_reason=res["on_hold_reason"],
            can_make_offer=res["can_make_offer"],
            share_link=res["share_link"],
            is_boost=res["is_boost"],
            is_top=res["is_top"],
            tops_count=res["tops_count"],
            paid_info=res["paid_info"],
            tracking_params=res["tracking_params"],
            price_valuation=PriceValuation(
                value=res["price_valuation"]["value"],
                price_range=res["price_valuation"]["price_range"],
                label=res["price_valuation"]["label"],
                url=res["price_valuation"]["url"],
            )
            if res.get("price_valuation")
            else None,
            images=[Image(**image) for image in res["images"]],
            can_leave_opinion=res["can_leave_opinion"],
            abuse_reported=res["abuse_reported"],
            sold_reported=res["sold_reported"],
            advert_status=res["advert_status"],
            appropriate_status_for_top=res["appropriate_status_for_top"],
            is_open=res["is_open"],
            fav_count=res["fav_count"],
            is_user_ad=res["is_user_ad"],
            x_listing_id=res["X-Listing-ID"] if res.get("X-Listing-ID") else None,
            is_vip=res["is_vip"],
        )

    def _dict_to_min_product(self, product: dict) -> MinProduct:
        return MinProduct(
            id=product["id"],
            guid=product["guid"],
            title=product["title"],
            region_id=product["region_id"],
            published=product.get("published"),
            date=datetime.fromtimestamp(product["date_long"]),
            price=product["price"],
            price_type=product["price_type"],
            image=product["img_url"],
            attributes=product["attributes"],
            details=product.get("details"),
            user_id=product["user_id"],
            user_phone=product["user_phone"],
            image_count=product["count_images"],
            _client=self,
        )

    async def get_categories(self) -> List[Category]:
        """
        Get all categories from the site.
        :return: List of categories.
        """
        res = await self._process_request(constants.CATEGORIES)
        return [Category(**category) for category in res["categories"]]

    async def get_recommendations(self, size: int = 6) -> List[MinProduct]:
        """
        Get all categories from the site.
        :return: List of categories.
        """
        res = await self._process_request(
            constants.RECOMMENDATIONS, params={"size": size}
        )
        return [self._dict_to_min_product(product) for product in res["results"]]

    async def get_product(self, product_id: int) -> Product:
        """
        Get product by id.
        :param product_id: Product id.
        :return: Product.
        """
        res = await self._process_request(
            constants.PRODUCT.format(id=product_id), params={"ad_attr_view": 2}
        )
        return self._dict_to_product(res)

    async def get_trending(self, page: int = 1) -> List[MinProduct]:
        """
        get trending products
        :return: List of products.
        """
        res = await self._process_request(constants.TRENDING, json={"page": page})
        return [self._dict_to_min_product(product) for product in res["results"]]

    async def search(
        self, query: str, page: int = 1, filters: Filter = None
    ) -> SearchResult:
        params = {}
        if filters:
            params = filters()
        page = f"/page{page}" if page > 1 else ""
        params["query"] = query
        res = await self._process_request(
            constants.SEARCH.format(page=page),
            params=params,
        )
        result = res["results"]
        return SearchResult(
            found=res["found"],
            next_url=res["next_url"],
            products=[self._dict_to_min_product(product) for product in result],
        )
