from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, constr
from datetime import datetime
from typing import Union
from . import constants
from enum import Enum
from . import utils
import orjson


# Custom Pydantic model
class ORJSONModel(BaseModel):
    class Config:
        json_encoders = {datetime: utils.to_timestamp}
        json_dumps = utils.orjson_dumps
        json_loads = orjson.loads
        use_enum_values = True
        orm_mode = True

    def serializable_dict(self, **kwargs):
        default_dict = super().dict(**kwargs)
        return jsonable_encoder(default_dict)


# Enums
class WatchStatusEnum(str, Enum):
    planned = constants.WATCH_PLANNED
    watching = constants.WATCH_WATCHING
    completed = constants.WATCH_COMPLETED
    on_hold = constants.WATCH_ON_HOLD
    dropped = constants.WATCH_DROPPED


# Args
class PaginationArgs(ORJSONModel):
    page: int = Field(default=1, gt=0)


# Responses
class PaginationResponse(ORJSONModel):
    total: int
    pages: int
    page: int


class QuerySearchArgs(ORJSONModel):
    query: Union[constr(min_length=3, max_length=255), None] = None
    page: int = Field(default=1, gt=0)


class AnimeResponse(ORJSONModel):
    media_type: Union[str, None]
    title_ua: Union[str, None]
    title_en: Union[str, None]
    title_ja: Union[str, None]
    episodes: Union[int, None]
    poster: Union[str, None]
    status: Union[str, None]
    scored_by: int
    score: float
    slug: str


class CharacterResponse(ORJSONModel):
    name_ua: Union[str, None]
    name_en: Union[str, None]
    name_ja: Union[str, None]
    image: Union[str, None]
    slug: str


class PersonResponse(ORJSONModel):
    name_native: Union[str, None]
    name_ua: Union[str, None]
    name_en: Union[str, None]
    image: Union[str, None]
    slug: str


class AnimeFavouriteResponse(ORJSONModel):
    anime: AnimeResponse
    created: datetime
    reference: str


class WatchResponse(ORJSONModel):
    note: Union[str, None]
    anime: AnimeResponse
    updated: datetime
    created: datetime
    reference: str
    episodes: int
    status: str
    score: int


class SuccessResponse(ORJSONModel):
    success: bool


class CompanyResponse(ORJSONModel):
    image: Union[str, None]
    name: str
    slug: str
