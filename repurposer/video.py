"""The video feature: video file in -> transcript, best clips, and a text pack out.

Pipeline, in plain English:
1. TRANSCRIBE: a speech-to-text model (faster-whisper) listens to the video
   and writes down what is said, with timestamps. It runs on your own
   computer, so there is no extra cost.
2. FIND CLIPS: we send the timestamped transcript to Claude and ask it to
   pick the best 20-60 second moments for short-form video.
3. CUT CLIPS (optional): ffmpeg, a free video tool, cuts those moments out
   of the original file into separate .mp4 files.
4. The transcript is also fed through the normal text engine, so a video
   gets LinkedIn / X / carousel / email / script versions too.
"""

import json
import os
import shutil
import subprocess

from .generator import ask_claude
from .prompts import CLIP_FINDER_PROMPT


def format_timestamp(seconds: float) -> str:
    """Turn 75.4 into '01:15'."""
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


MOCK_SEGMENTS = [
    {"start": 0.0, "end": 20.0, "text": "Most founders think content takes too long. It does not have to."},
    {"start": 20.0, "end": 55.0, "text": "Write one strong idea, then reshape it for every platform you care about."},
    {"start": 55.0, "end": 95.0, "text": "A single blog can become a post, a thread, a carousel, an email and a short video."},
    {"start": 95.0, "end": 130.0, "text": "The secret is keeping the idea the same and changing only the format."},
]


def transcribe(video_path: str, model_size: str = "base", mock: bool = False) -> list[dict]:
    """Convert speech in a video to text segments with start/end times.

    In mock mode we return a built-in sample transcript so you can try the
    whole pipeline without a video file or the speech model.
    """
    if mock:
        return list(MOCK_SEGMENTS)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError(
            "Video features need extra packages. Run: pip install -r requirements-video.txt"
        ) from e

    # "int8" keeps memory use low so it runs on a normal laptop CPU.
    model = WhisperModel(model_size, compute_type="int8")
    segments, _info = model.transcribe(video_path)
    return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]


def transcript_to_text(segments: list[dict], with_timestamps: bool = False) -> str:
    """Join segments into one block of text, optionally with [mm:ss] markers."""
    if with_timestamps:
        return "\n".join(f"[{format_timestamp(s['start'])}] ({s['start']:.0f}s) {s['text']}" for s in segments)
    return " ".join(s["text"] for s in segments)


def parse_clips_json(raw: str) -> list[dict]:
    """Pull the JSON list out of Claude's reply, even if it adds extra words."""
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Claude's reply did not contain a JSON list of clips.")
    clips = json.loads(raw[start : end + 1])
    cleaned = []
    for c in clips:
        s, e = float(c["start"]), float(c["end"])
        if e <= s:
            continue  # skip nonsense where the end is before the start
        cleaned.append({"start": s, "end": e, "title": c.get("title", "Clip"), "why": c.get("why", "")})
    return cleaned


def find_clips(segments: list[dict], n: int = 3, mock: bool = False) -> list[dict]:
    """Ask Claude for the best n clip moments (or fake evenly spaced ones in mock mode)."""
    if not segments:
        return []
    if mock:
        total = segments[-1]["end"]
        length = min(30.0, total / (n + 1))
        return [
            {
                "start": round(total * (i + 1) / (n + 1) - length / 2, 1),
                "end": round(total * (i + 1) / (n + 1) + length / 2, 1),
                "title": f"Mock clip {i + 1}",
                "why": "Placeholder: evenly spaced clip used in mock mode.",
            }
            for i in range(n)
        ]
    prompt = CLIP_FINDER_PROMPT.format(n=n, transcript=transcript_to_text(segments, with_timestamps=True))
    reply = ask_claude("You are a short-form video editor.", prompt, max_tokens=1200)
    return parse_clips_json(reply)


def cut_clips(video_path: str, clips: list[dict], out_dir: str = "output/clips") -> list[str]:
    """Cut each clip out of the video with ffmpeg and return the file paths."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not installed. Get it from https://ffmpeg.org/download.html")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, clip in enumerate(clips, start=1):
        path = os.path.join(out_dir, f"clip_{i}.mp4")
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(clip["start"]),
                "-i", video_path,
                "-t", str(clip["end"] - clip["start"]),
                "-c:v", "libx264", "-c:a", "aac",
                path,
            ],
            check=True,
            capture_output=True,  # keeps ffmpeg's noisy logs out of your terminal
        )
        paths.append(path)
    return paths
