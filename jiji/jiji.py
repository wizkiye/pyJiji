from dataclasses import dataclass
from datetime import datetime
from typing import Union, List, Any, Optional

import httpx
from rich.pretty import pprint

import constants
from errors import UnknownError


@dataclass
class ProductAttribute:
    name: str
    value: str
    unit: Union[str, None]


@dataclass
class Attribute:
    name: str
    value: Union[int, str]
    data_type: str
    unit: Optional[str]
    group_type: str
    # value_str: Union[int, str]


@dataclass
class Price:
    value: int
    view: str
    period: None
    bulk: None
    price: str
    text: str


@dataclass
class PriceValuation:
    value: str
    price_range: List[int]
    label: str
    url: str


@dataclass
class MakeOfferRange:
    min: int
    max: int


@dataclass
class Image:
    id: int
    url: str
    is_main: bool
    width: int
    height: int
    s3: bool
    position: int


@dataclass
class User:
    name: str
    avatar_url: str
    id: int
    email: str
    phone: str
    phones: List[str]
    last_seen: str
    user_registered: str


@dataclass
class Badge:
    pass


@dataclass
class PriceValuation:
    value: str
    price_range: List[int]
    label: str
    url: str


@dataclass
class Product:
    id: int
    guid: str
    category_slug: str
    title: str
    region_id: int
    regions_display: List[str]
    published: str
    review_estimation: None
    price: str
    price_history: bool
    formatted_price: str
    price_obj: Price
    price_type: str
    attributes: List[Attribute]
    description: str
    video: None | str
    user: User
    category_id: int
    tags: List[List[str]]
    long_tag: str
    date_moderated: datetime
    date_created: datetime
    rating: None | int
    page_views: int
    is_user_ad: bool
    moderation_reasons: None
    on_hold_reason: None
    can_make_offer: bool
    # badge: Badge
    share_link: str
    share_link: str
    is_boost: bool
    is_vip: bool
    is_top: bool
    tops_count: int
    paid_info: None
    tracking_params: None
    price_valuation: PriceValuation
    images: List[Image]
    can_leave_opinion: bool
    abuse_reported: bool
    sold_reported: bool
    advert_status: str
    appropriate_status_for_top: bool
    is_open: bool
    fav_count: int
    x_listing_id: str


@dataclass
class Category:
    id: int
    parent_id: Union[int, None]
    name: str
    slug: str
    image: Union[str, None]
    image_v2: str
    total_ads: int
    listing_on_top_lvl: bool
    pos: int
    readonly: bool
    target_price: Union[float, None]

    @property
    def link(self) -> str:
        return f"https://www.jiji.com.et/{self.slug}"


@dataclass
class MinProduct:
    id: int
    guid: str
    title: str
    region_id: int
    published: str
    date: datetime
    price: int | None
    price_type: str | None
    image: str
    attributes: List[Any]
    details: str
    user_id: int
    user_phone: str
    image_count: int
    _client: "JIJI" = None

    async def get_product(self) -> Product:
        if not self._client:
            raise ValueError("Client is not set.")
        return await self._client.get_product(self.id)


class JIJI:
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
            pprint(self._BASE_URL.format(endpoint))
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
        return [
            MinProduct(
                id=product["id"],
                guid=product["guid"],
                title=product["title"],
                region_id=product["region_id"],
                published=product["published"],
                date=datetime.fromtimestamp(product["date_long"]),
                price=product["price"],
                price_type=product["price_type"],
                image=product["img_url"],
                attributes=product["attributes"],
                details=product["details"],
                user_id=product["user_id"],
                user_phone=product["user_phone"],
                image_count=product["count_images"],
                _client=self,
            )
            for product in res["results"]
        ]

    async def get_product(self, product_id: int) -> Product:
        """
        Get product by id.
        :param product_id: Product id.
        :return: Product.
        """
        res = await self._process_request(
            constants.PRODUCT.format(id=product_id), params={"ad_attr_view": 2}
        )
        return Product(
            id=res["id"],
            guid=res["guid"],
            category_slug=res["category_slug"],
            title=res["title"],
            region_id=res["region_id"],
            regions_display=res["regions_display"],
            published=res["published"],
            date_created=datetime.fromtimestamp(res["date_moderated"]),
            date_moderated=datetime.fromtimestamp(res["date_moderated"]),
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

    async def get_trending(self, page: int = 1) -> List[MinProduct]:
        """
        get trending products
        :return: List of products.
        """
        res = await self._process_request(constants.TRENDING, json={"page": page})
        return [
            MinProduct(
                id=product["id"],
                guid=product["guid"],
                title=product["title"],
                region_id=product["region_id"],
                published=product["published"],
                date=datetime.fromtimestamp(product["date_long"]),
                price=product["price"],
                price_type=product["price_type"],
                image=product["img_url"],
                attributes=product["attributes"],
                details=product["details"],
                user_id=product["user_id"],
                user_phone=product["user_phone"],
                image_count=product["count_images"],
                _client=self,
            )
            for product in res["results"]
        ]


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    jiji = JIJI()
    pprint(loop.run_until_complete(jiji.get_product(546021)))
