import math
import re
from dataclasses import asdict, is_dataclass


def plain(value):
    return asdict(value) if is_dataclass(value) else value


def verdict(valid, message, **details):
    return {"valid": bool(valid), "score": 1.0 if valid else 0.0, "message": message, "details": details}


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("noncanonical date")
    y, m, d = [int(part) for part in value.split("-")]
    if y < 1 or not 1 <= m <= 12:
        raise ValueError("invalid year or month")
    leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    months = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not 1 <= d <= months[m - 1]:
        raise ValueError("invalid day")
    previous = y - 1
    return 365 * previous + previous // 4 - previous // 100 + previous // 400 + sum(months[: m - 1]) + d


def stamp(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
        raise ValueError("timestamps must use canonical UTC")
    h, m, s = [int(part) for part in value[11:19].split(":")]
    if h > 23 or m > 59 or s > 59:
        raise ValueError("invalid clock time")
    return day(value[:10]) * 86400 + h * 3600 + m * 60 + s


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("integer outside supported bounds")


def finite(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("expected finite number")


def unique(rows, key):
    ids = [r[key] for r in rows]
    if any(not isinstance(x, str) or not x.strip() for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("identifiers must be nonempty and unique")


def equivalent(actual, expected):
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all(equivalent(actual[k], v) for k, v in expected.items())
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(equivalent(a, b) for a, b in zip(actual, expected))
        )
    if type(expected) is float:
        return (
            type(actual) in (int, float)
            and math.isfinite(actual)
            and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9)
        )
    return type(actual) is type(expected) and actual == expected


def validate(x):
    integer(x["short_window"], 1, 1000)
    integer(x["long_window"], x["short_window"] + 1, 1001)
    integer(x["rsi_period"], 1, 1000)
    day(x["cutoff"])
    unique(x["bars"], "date")
    dates = [r["date"] for r in x["bars"]]
    if dates != sorted(dates):
        raise ValueError("bars must be chronological")
    for r in x["bars"]:
        day(r["date"])
        finite(r["close"])
        if not 0 < r["close"] <= 1e12:
            raise ValueError("close must be positive and at most 1e12")
    n = sum(r["date"] <= x["cutoff"] for r in x["bars"])
    if n < max(x["long_window"], x["rsi_period"] + 1):
        raise ValueError("insufficient eligible history")


def expected(x):
    from itertools import pairwise

    p = [r["close"] for r in x["bars"] if r["date"] <= x["cutoff"]]
    a = math.fsum(p[-x["short_window"] :]) / x["short_window"]
    b = math.fsum(p[-x["long_window"] :]) / x["long_window"]
    tail = p[-x["rsi_period"] - 1 :]
    changes = [v - u for u, v in pairwise(tail)]
    up = math.fsum(max(d, 0) for d in changes)
    down = math.fsum(max(-d, 0) for d in changes)
    return {
        "sma_short": a,
        "sma_long": b,
        "rsi": 50.0 if up + down == 0 else 100.0 * up / (up + down),
        "signal": "buy" if p[-1] > a > b else "sell" if p[-1] < a < b else "hold",
    }
