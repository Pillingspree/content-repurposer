"""Command-line interface: the 'front door' for people using a terminal.

Examples:
    python -m repurposer text examples/sample_blog.md --mock
    python -m repurposer text my_post.md --formats linkedin email --tone friendly
    python -m repurposer video my_talk.mp4 --clips 3 --cut
"""

import argparse
import os

from .generator import repurpose, save_results
from .prompts import ALL_FORMATS


def _load_env() -> None:
    """Load secrets from a .env file if the helper library is installed."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repurposer", description="Turn one blog or video into many posts.")
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("text", help="Repurpose a blog post (.md or .txt file)")
    t.add_argument("file", help="Path to the blog post")
    t.add_argument("--formats", nargs="+", choices=ALL_FORMATS, default=ALL_FORMATS)
    t.add_argument("--tone", default="professional")
    t.add_argument("--out", default="output")
    t.add_argument("--mock", action="store_true", help="No API key needed; placeholder output")

    v = sub.add_parser("video", help="Repurpose a video file")
    v.add_argument("file", help="Path to the video (.mp4, .mov, ...)")
    v.add_argument("--clips", type=int, default=3, help="How many short clips to suggest")
    v.add_argument("--cut", action="store_true", help="Also cut the clips with ffmpeg")
    v.add_argument("--formats", nargs="+", choices=ALL_FORMATS, default=ALL_FORMATS)
    v.add_argument("--tone", default="professional")
    v.add_argument("--out", default="output")
    v.add_argument("--mock", action="store_true", help="No API key or video needed; placeholder output")
    return parser


def main(argv: list[str] | None = None) -> None:
    _load_env()
    args = build_parser().parse_args(argv)
    name = os.path.splitext(os.path.basename(args.file))[0]

    if args.command == "text":
        with open(args.file, encoding="utf-8") as f:
            blog = f.read()
        results = repurpose(blog, args.formats, args.tone, args.mock)
        for p in save_results(results, args.out, name):
            print("Saved", p)

    elif args.command == "video":
        # Imported here so text-only users never need the video packages.
        from . import video

        segments = video.transcribe(args.file, mock=args.mock)
        transcript = video.transcript_to_text(segments)
        results = repurpose(transcript, args.formats, args.tone, args.mock)
        paths = save_results(results, args.out, name)

        clips = video.find_clips(segments, args.clips, args.mock)
        clips_path = os.path.join(args.out, f"{name}_clips.md")
        with open(clips_path, "w", encoding="utf-8") as f:
            for i, c in enumerate(clips, 1):
                f.write(
                    f"## Clip {i}: {c['title']}\n"
                    f"{video.format_timestamp(c['start'])} - {video.format_timestamp(c['end'])}\n"
                    f"{c['why']}\n\n"
                )
        paths.append(clips_path)
        if args.cut and not args.mock:
            paths += video.cut_clips(args.file, clips, os.path.join(args.out, "clips"))
        for p in paths:
            print("Saved", p)


if __name__ == "__main__":
    main()
