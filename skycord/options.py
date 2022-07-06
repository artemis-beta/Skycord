import enum

class CMAP(enum.Enum):
    HAXBY = enum.auto()
    SEALAND = enum.auto()
    GEO = enum.auto()
    COOL = enum.auto()
    DRYWET = enum.auto()
    GRAY = enum.auto()
    HOT = enum.auto()
    JET = enum.auto()
    GEBCO = enum.auto()
    POLAR = enum.auto()
    RAINBOW = enum.auto()
    RED2GREEN = enum.auto()
    RELIEF = enum.auto()
    SEIS = enum.auto()
    GLOBE = enum.auto()
    WYSIWYG = enum.auto()
    WYSIWYGCONT = enum.auto()
    OCEAN = enum.auto()


def as_string(enum_type: enum.EnumMeta) -> str:
    return enum_type.name.lower()
