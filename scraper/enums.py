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
    """Language code for the movie or TV show."""

    CHS = "chs"  # 简体中文 Simplified Chinese
    CHT = "cht"  # 繁体中文 Traditional Chinese
    CSY = "csy"  # 捷克语 Czech
    DAN = "dan"  # 丹麦语 Danish
    ENU = "enu"  # 英语 English
    FRE = "fre"  # 法语 French
    GER = "ger"  # 德语 German
    HUN = "hun"  # 匈牙利语 Hungarian
    ITA = "ita"  # 意大利语 Italian
    JPN = "jpn"  # 日语 Japanese
    KRN = "krn"  # 韩语 Korean
    NLD = "nld"  # 荷兰语 Nederland
    NOR = "nor"  # 挪威语 Norwegian
    PLK = "plk"  # 波兰语 Polish
    PTB = "ptb"  # 巴西葡萄牙语 Brazilian Portuguese
    PTG = "ptg"  # 葡萄牙语 Portuguese
    RUS = "rus"  # 俄语 Russian
    SPN = "spn"  # 西班牙语 Spanish
    SVE = "sve"  # 瑞典语 Swedish
    TRK = "trk"  # 土耳其语 Turkish
    THA = "tha"  # 泰语 Thai
