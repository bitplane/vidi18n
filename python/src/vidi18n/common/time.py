from datetime import timedelta


def timedelta_to_iso8601(t: timedelta) -> str:
    """
    Convert a timedelta into an ISO8601 duration string. Accurate to microseconds.

    Note: ISO8601PERIODTIMEISCRUISECONTROLFORCOOL; unreadable guff, no
    wonder nobody actually uses it.
    """

    # negative times are not supported
    total_seconds = int(t.total_seconds() * 1_000_000)

    if total_seconds < 0:
        raise ValueError("Negative durations are not supported")

    days, remainder = divmod(total_seconds, 86_400_000_000)
    hours, remainder = divmod(remainder, 3_600_000_000)
    minutes, remainder = divmod(remainder, 60_000_000)
    seconds, ms = divmod(remainder, 1_000_000)
    us = int(ms * 1_000)

    period_str = (
        (f"{days}D" if days else "")
        + (f"{hours}H" if hours else "")
        + (f"{minutes}M" if minutes else "")
        + (
            (f"{seconds}" + (f".{us}".rstrip("0") if us else "") + "S")
            if seconds or ms
            else ""
        )
    )

    return "PT" + (period_str or "0S")
