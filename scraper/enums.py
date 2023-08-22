"""Enum classes for this package."""
from enum import Enum, unique


@unique
class VideoType(Enum):
    """Type of video being scraped."""

    MOVIE = "movie"
    TVSHOW = "tvshow"
    TVSHOW_EPISODE = "tvshow_episode"


@unique
class Language(Enum):
    """Language and country code, ISO 639-1 and ISO 3166-1."""

    CHS = "zh-CN"  # 简体中文 Simplified Chinese
    CHT = "zh-TW"  # 繁体中文 Traditional Chinese
    CSY = "cs-CZ"  # 捷克语 Czech
    DAN = "da-DK"  # 丹麦语 Danish
    ENU = "en-US"  # 英语 English
    FRE = "fr-FR"  # 法语 French
    GER = "de-DE"  # 德语 German
    HUN = "hu-HU"  # 匈牙利语 Hungarian
    ITA = "it-IT"  # 意大利语 Italian
    JPN = "ja-JP"  # 日语 Japanese
    KRN = "ko-KR"  # 韩语 Korean
    NLD = "nl-NL"  # 荷兰语 Nederland
    NOR = "no-NO"  # 挪威语 Norwegian
    PLK = "pl-PL"  # 波兰语 Polish
    PTB = "pt-BR"  # 巴西葡萄牙语 Brazilian Portuguese
    PTG = "pt-PT"  # 葡萄牙语 Portuguese
    RUS = "ru-RU"  # 俄语 Russian
    SPN = "es-ES"  # 西班牙语 Spanish
    SVE = "sv-SE"  # 瑞典语 Swedish
    TRK = "tr-TR"  # 土耳其语 Turkish
    THA = "th-TH"  # 泰语 Thai


def video_type(value):
    """Convert string to VideoType enum."""
    return VideoType[value.upper()]


def lang_type(value):
    """Convert string to Language enum."""
    return Language[value.upper()]
