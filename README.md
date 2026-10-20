# ♻️ Content Repurposer

Turn **one blog post** (or **one video**) into a **LinkedIn post, X/Twitter thread, Instagram carousel, email newsletter and short-video script**, and cut the best **short clips** out of a video automatically.

Built with Python and Claude. Includes a web app and a command-line tool.

## What it does

| Input | Output |
|---|---|
| Blog post (`.md` / `.txt` / pasted text) | LinkedIn post, X thread, IG carousel, email, 60s video script |
| Video (`.mp4`, `.mov`, ...) | Transcript, suggested short clips with timestamps, optional cut `.mp4` clips, plus all the text formats above |

## Quick start

```bash
git clone https://github.com/<your-username>/content-repurposer.git
cd content-repurposer
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Try it for free first (no API key, placeholder output):

```bash
python -m repurposer text examples/sample_blog.md --mock
streamlit run app.py
```

### Real AI output

```bash
cp .env.example .env              # then paste your Anthropic API key into .env
python -m repurposer text examples/sample_blog.md --tone friendly
```

### Video

```bash
pip install -r requirements-video.txt   # adds speech-to-text
# also install ffmpeg: https://ffmpeg.org/download.html
python -m repurposer video my_talk.mp4 --clips 3 --cut
```

## Project structure

```
repurposer/
  prompts.py     the instructions for each format (edit these to change style)
  generator.py   blog text -> all formats
  video.py       video -> transcript -> best clips -> cut files
  cli.py         terminal interface
app.py           web interface (Streamlit)
tests/           automated tests (run: python -m pytest)
```

## How it works

1. `prompts.py` holds one carefully written instruction per platform.
2. `generator.py` sends your content plus each instruction to Claude.
3. For video, `video.py` transcribes locally with faster-whisper, asks Claude to pick the best 20-60s moments, and cuts them with ffmpeg.
4. **Mock mode** (`--mock`) fakes the AI calls so the tool and tests run free and offline.

## Roadmap

- Brand voice profile (learn from your past posts)
- Direct scheduling to LinkedIn / X
- Auto-captions burned into clips
- Vertical 9:16 reframing

## License

MIT
