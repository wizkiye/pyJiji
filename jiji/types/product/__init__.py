from dataclasses import dataclass
from datetime import datetime
from typing import List, Any, Union, Optional

from jiji import jiji


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
    category_slug: str | None
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
    _client: "jiji.JiJi" = None

    async def get_product(self) -> Product:
        if not self._client:
            raise ValueError("Client is not set.")
        return await self._client.get_product(self.id)
