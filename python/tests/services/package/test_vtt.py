from vidi18n.services.package.listeners import (
    contiguous_frontier,
    render_vtt,
    timestamp,
)


def test_timestamp():
    assert timestamp(3_723_456) == "01:02:03.456"


def test_contiguous_frontier_ignores_later_chunks():
    assert contiguous_frontier({0, 1, 3, 4}) == 2
    assert contiguous_frontier({1, 2}) == 0


def test_vtt_is_ordered_and_escapes_arrow():
    cues = [
        {
            "segment_id": "later",
            "start_ms": 10_000,
            "end_ms": 20_000,
            "text": "later",
        },
        {
            "segment_id": "first",
            "start_ms": 0,
            "end_ms": 10_000,
            "text": "one --> two",
        },
    ]
    output = render_vtt(cues)
    assert output.startswith("WEBVTT\n\nfirst\n00:00:00.000 --> 00:00:10.000")
    assert "one → two" in output
    assert output.index("first") < output.index("later")
