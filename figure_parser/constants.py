from enum import Enum


class BrandHost(str, Enum):
    GSC = "goodsmile.info"
    ALTER = "alter-web.jp"
    NATIVE = "native-web.jp"


class GSCCategory(str, Enum):
    SCALE = "scale"
    NENDOROID = "nendoroid_series"
    FIGMA = "figma"
    OTHER_FIGURE = "other_figures"
    GOODS = "goods_other"


class AlterCategory(str, Enum):
    ALL = "products"
    FIGURE = "figure"
    ALTAIR = "altair"
    COLLABO = "collabo"
    OTHER = "other"
    ALMECHA = "almecha"


class NativeCategory(str, Enum):
    CREATORS = "creators"
    CHARACTERS = "characters"


class GSCLang(str, Enum):
    ENGLISH = "en"
    JAPANESE = "ja"
    TRADITIONAL_CHINESE = "zh"
