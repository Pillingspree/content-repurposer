"""The instructions we give the AI for each output format.

Changing the text in this file changes the style and quality of everything
the tool produces. No other file needs to change.
"""

SYSTEM_PROMPT = (
    "You are an expert content strategist. You turn long-form content into "
    "platform-native posts. Keep the author's ideas and facts accurate. "
    "Never invent statistics, quotes or claims that are not in the source. "
    "Write in a {tone} tone. Output only the finished content, with no "
    "preamble and no explanation."
)

FORMAT_PROMPTS = {
    "linkedin": (
        "Write one LinkedIn post from the content below.\n"
        "- Strong first line (a hook) that works before the 'see more' cut\n"
        "- Short paragraphs, 1-2 sentences each\n"
        "- 150-250 words\n"
        "- End with a question that invites comments\n"
        "- At most 3 hashtags at the very end"
    ),
    "twitter": (
        "Write an X/Twitter thread from the content below.\n"
        "- 6 to 8 tweets, each under 270 characters\n"
        "- Number them like 1/, 2/, 3/\n"
        "- Tweet 1 is a hook; the last tweet is a takeaway plus a call to action\n"
        "- No hashtags except optionally one in the last tweet"
    ),
    "instagram_carousel": (
        "Write an Instagram carousel from the content below.\n"
        "- 7 slides: cover slide, 5 content slides, closing call-to-action slide\n"
        "- Format each as 'Slide N: <headline in max 8 words>' followed by "
        "'<one or two supporting lines, max 25 words>'\n"
        "- Then add a caption (max 60 words) and 5 hashtags"
    ),
    "email": (
        "Write a newsletter email from the content below.\n"
        "- Start with 'Subject:' and one subject line (under 60 characters)\n"
        "- Then 'Preview:' with a preview line (under 90 characters)\n"
        "- Then the body: friendly greeting, 3 short sections with clear "
        "takeaways, and one call-to-action link placeholder [LINK]\n"
        "- 180-280 words in the body"
    ),
    "short_script": (
        "Write a 45-60 second script for a short vertical video (Reels, "
        "TikTok, YouTube Shorts) from the content below.\n"
        "- Two columns of information per beat: [VISUAL] and [VOICEOVER]\n"
        "- Open with a 3-second hook\n"
        "- 5 to 7 beats, around 130-150 spoken words in total\n"
        "- End with a call to action"
    ),
}

ALL_FORMATS = list(FORMAT_PROMPTS.keys())

CLIP_FINDER_PROMPT = (
    "Below is a timestamped transcript of a video. Pick the {n} best moments "
    "to cut as standalone short clips (each between 20 and 60 seconds). "
    "Choose moments that make sense without extra context and open with a hook.\n\n"
    "Reply with ONLY a JSON list, no other text. Each item must look like:\n"
    '{{"start": <seconds>, "end": <seconds>, "title": "<short title>", '
    '"why": "<one sentence on why this works>"}}\n\n'
    "TRANSCRIPT:\n{transcript}"
)
