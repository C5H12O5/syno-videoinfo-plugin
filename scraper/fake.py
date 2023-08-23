"""Fake result for testing."""
import json
from typing import Any, List


def fake_result(plugin_id: str, videotype: str) -> str:
    """Return fake result."""
    result: List[Any] = []
    if videotype == "movie":
        result.append(_movie)
    elif videotype == "tvshow":
        result.append(_tvshow)
    elif videotype == "tvshow_episode":
        result.append(_tvshow_episode)
    return json.dumps(
        {"success": True, "result": result}, ensure_ascii=False, indent=2
    ).replace("[plugin_id]", plugin_id)


_movie = {
    "title": "unknown",
    "tagline": "unknown",
    "original_available": "1970-01-01",
    "summary": "unknown",
    "certificate": "unknown",
    "genre": ["unknown"],
    "actor": ["unknown"],
    "writer": ["unknown"],
    "director": ["unknown"],
    "extra": {
        "[plugin_id]": {
            "rating": {"[plugin_id]": 0},
            "poster": ["unknown"],
            "backdrop": ["unknown"],
        }
    },
}

_tvshow = {
    "title": "unknown",
    "original_available": "1970-01-01",
    "summary": "unknown",
    "extra": {
        "[plugin_id]": {
            "poster": ["unknown"],
            "backdrop": ["unknown"],
        }
    },
}

_tvshow_episode = {
    "title": "unknown",
    "tagline": "unknown",
    "season": 1,
    "episode": 1,
    "original_available": "1970-01-01",
    "summary": "unknown",
    "certificate": "unknown",
    "genre": ["unknown"],
    "actor": ["unknown"],
    "writer": ["unknown"],
    "director": ["unknown"],
    "extra": {
        "[plugin_id]": {
            "tvshow": {
                "title": "unknown",
                "original_available": "1970-01-01",
                "summary": "unknown",
                "extra": {
                    "[plugin_id]": {
                        "poster": ["unknown"],
                        "backdrop": ["unknown"],
                    }
                },
            },
            "rating": {"[plugin_id]": 0},
            "poster": ["unknown"],
        }
    },
}
