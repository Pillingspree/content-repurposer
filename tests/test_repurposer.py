"""Automated tests. They run offline and cost nothing (mock mode only).

Run them with:  python -m pytest
A green result means the core pieces still work after you change something.
"""

import pytest

from repurposer.generator import repurpose, save_results
from repurposer.prompts import ALL_FORMATS
from repurposer.video import MOCK_SEGMENTS, find_clips, format_timestamp, parse_clips_json, transcript_to_text

BLOG = "# Why Consistency Wins\n\nShip small things often."


def test_all_formats_returned_in_mock_mode():
    results = repurpose(BLOG, mock=True)
    assert set(results) == set(ALL_FORMATS)
    assert "Why Consistency Wins" in results["linkedin"]


def test_empty_blog_is_rejected():
    with pytest.raises(ValueError):
        repurpose("   ", mock=True)


def test_unknown_format_is_rejected():
    with pytest.raises(ValueError):
        repurpose(BLOG, formats=["myspace"], mock=True)


def test_save_results_writes_files(tmp_path):
    paths = save_results(repurpose(BLOG, ["email"], mock=True), str(tmp_path), "demo")
    assert len(paths) == 1 and paths[0].endswith("demo_email.md")


def test_format_timestamp():
    assert format_timestamp(75.4) == "01:15"


def test_parse_clips_handles_chatty_replies_and_bad_clips():
    raw = 'Sure! Here you go:\n[{"start": 5, "end": 30, "title": "A"}, {"start": 40, "end": 10, "title": "bad"}]'
    clips = parse_clips_json(raw)
    assert len(clips) == 1 and clips[0]["title"] == "A"


def test_parse_clips_without_json_fails_clearly():
    with pytest.raises(ValueError):
        parse_clips_json("no list here")


def test_mock_clips_are_inside_video_length():
    clips = find_clips(MOCK_SEGMENTS, 3, mock=True)
    total = MOCK_SEGMENTS[-1]["end"]
    assert len(clips) == 3
    assert all(0 <= c["start"] < c["end"] <= total for c in clips)


def test_transcript_joins_text():
    assert "Most founders" in transcript_to_text(MOCK_SEGMENTS)
