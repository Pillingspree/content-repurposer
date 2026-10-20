"""The text engine: takes a blog post and produces every format.

How it works, in plain English:
1. Read the blog text.
2. For each format (LinkedIn, X, ...), send the blog + that format's
   instructions to Claude.
3. Collect the answers into one dictionary: {"linkedin": "...", ...}

"Mock mode" skips step 2 and returns placeholder text, so you can demo and
test the whole tool for free, with no API key.
"""

import os

from .prompts import ALL_FORMATS, FORMAT_PROMPTS, SYSTEM_PROMPT

# Which Claude model to use. Override without touching code by setting the
# CLAUDE_MODEL environment variable.
DEFAULT_MODEL = "claude-sonnet-5-5"


def ask_claude(system: str, user: str, max_tokens: int = 1500) -> str:
    """Send one request to Claude and return the text of its answer."""
    # Imported here (not at the top) so the rest of the tool, including
    # mock mode and the tests, works even if the library is not installed.
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add "
            "your key, or run with mock mode (--mock) to try the tool for free."
        )

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", DEFAULT_MODEL),
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


def _mock_output(fmt: str, blog_text: str) -> str:
    """Placeholder output used in mock mode. No network, no cost."""
    title = blog_text.strip().splitlines()[0].lstrip("# ").strip() if blog_text.strip() else "Untitled"
    return f"[MOCK {fmt.upper()}] Draft based on: {title}\n(Run without --mock to get real AI-written content.)"


def repurpose(
    blog_text: str,
    formats: list[str] | None = None,
    tone: str = "professional",
    mock: bool = False,
) -> dict[str, str]:
    """Turn one piece of long-form text into several platform formats.

    Returns a dictionary mapping format name -> generated content.
    """
    if not blog_text or not blog_text.strip():
        raise ValueError("The blog text is empty. Nothing to repurpose.")

    formats = formats or ALL_FORMATS
    unknown = [f for f in formats if f not in FORMAT_PROMPTS]
    if unknown:
        raise ValueError(f"Unknown format(s): {unknown}. Choose from: {ALL_FORMATS}")

    results: dict[str, str] = {}
    system = SYSTEM_PROMPT.format(tone=tone)
    for fmt in formats:
        if mock:
            results[fmt] = _mock_output(fmt, blog_text)
        else:
            user_message = f"{FORMAT_PROMPTS[fmt]}\n\nCONTENT:\n{blog_text}"
            results[fmt] = ask_claude(system, user_message)
    return results


def save_results(results: dict[str, str], out_dir: str = "output", name: str = "pack") -> list[str]:
    """Write each result to its own .md file and return the file paths."""
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for fmt, content in results.items():
        path = os.path.join(out_dir, f"{name}_{fmt}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        paths.append(path)
    return paths
