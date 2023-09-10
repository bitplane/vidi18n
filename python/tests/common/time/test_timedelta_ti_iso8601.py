from datetime import timedelta

import pytest
from vidi18n.common.time import timedelta_to_iso8601


def test_seconds_only():
    assert timedelta_to_iso8601(timedelta(hours=0, minutes=0, seconds=45)) == "PT45S"
    assert timedelta_to_iso8601(timedelta(hours=0, minutes=0, seconds=5)) == "PT5S"


def test_minutes_and_seconds():
    assert timedelta_to_iso8601(timedelta(hours=0, minutes=15, seconds=0)) == "PT15M"
    assert timedelta_to_iso8601(timedelta(hours=0, minutes=5, seconds=20)) == "PT5M20S"


def test_hours():
    assert (
        timedelta_to_iso8601(timedelta(hours=1, minutes=30, seconds=15)) == "PT1H30M15S"
    )
    assert timedelta_to_iso8601(timedelta(hours=2, minutes=0, seconds=0)) == "PT2H"


def test_fractional_seconds():
    assert timedelta_to_iso8601(timedelta(seconds=10, milliseconds=500)) == "PT10.5S"


def test_days():
    assert timedelta_to_iso8601(timedelta(days=2)) == "PT2D"
    assert timedelta_to_iso8601(timedelta(days=2, hours=3)) == "PT2D3H"
    assert timedelta_to_iso8601(timedelta(days=7, minutes=5)) == "PT7D5M"


def test_no_duration():
    assert timedelta_to_iso8601(timedelta(hours=0, minutes=0, seconds=0)) == "PT0S"


def test_negative_durations():
    with pytest.raises(ValueError):
        timedelta_to_iso8601(timedelta(seconds=-1))


def test_fractional_seconds_edge_cases():
    assert timedelta_to_iso8601(timedelta(seconds=10, microseconds=500000)) == "PT10.5S"
    assert (
        timedelta_to_iso8601(timedelta(seconds=10, microseconds=123456))
        == "PT10.123456S"
    )


def test_all_units():
    assert (
        timedelta_to_iso8601(
            timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=500)
        )
        == "PT1D2H3M4.5S"
    )


def test_large_values():
    assert timedelta_to_iso8601(timedelta(days=1_000_000)) == "PT1000000D"


def test_wrap():
    assert timedelta_to_iso8601(timedelta(hours=24)) == "PT1D"
    assert timedelta_to_iso8601(timedelta(minutes=120)) == "PT2H"
    assert timedelta_to_iso8601(timedelta(seconds=240)) == "PT4M"
