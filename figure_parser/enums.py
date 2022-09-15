from enum import Enum

__all__ = (
    "BrandHost",
    "GSCCategory",
    "GSCLang",
    "AlterCategory",
    "NativeCategory",
)


class StrEnum(str, Enum):
    pass


class BrandHost(StrEnum):
    GSC = "goodsmile.info"
    ALTER = "alter-web.jp"
    NATIVE = "native-web.jp"
    AMAKUNI = "amakuni.info"


class GSCCategory(StrEnum):
    SCALE = "scale"
    NENDOROID = "nendoroid_series"
    FIGMA = "figma"
    OTHER_FIGURE = "other_figures"
    GOODS = "goods_other"


class AlterCategory(StrEnum):
    ALL = "products"
    FIGURE = "figure"
    ALTAIR = "altair"
    COLLABO = "collabo"
    OTHER = "other"
    ALMECHA = "almecha"


class NativeCategory(StrEnum):
    CREATORS = "creators"
    CHARACTERS = "characters"


class GSCLang(StrEnum):
    ENGLISH = "en"
    JAPANESE = "ja"
    TRADITIONAL_CHINESE = "zh"
