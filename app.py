"""Web app: the friendly screen for people who do not use a terminal.

Run it with:  streamlit run app.py
"""

import os
import tempfile

import streamlit as st

from repurposer import video
from repurposer.generator import repurpose
from repurposer.prompts import ALL_FORMATS

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

LABELS = {
    "linkedin": "LinkedIn post",
    "twitter": "X / Twitter thread",
    "instagram_carousel": "Instagram carousel",
    "email": "Email newsletter",
    "short_script": "Short video script",
}

st.set_page_config(page_title="Content Repurposer", page_icon="♻️", layout="wide")
st.title("♻️ Content Repurposer")
st.caption("Write once. Publish everywhere.")

with st.sidebar:
    st.header("Settings")
    tone = st.selectbox("Tone", ["professional", "friendly", "bold", "witty", "educational"])
    chosen = st.multiselect("Formats", ALL_FORMATS, default=ALL_FORMATS, format_func=LABELS.get)
    mock = st.checkbox("Mock mode (free, no API key)", value=not os.getenv("ANTHROPIC_API_KEY"))


def show_results(results: dict) -> None:
    tabs = st.tabs([LABELS[f] for f in results])
    for tab, (fmt, text) in zip(tabs, results.items()):
        with tab:
            st.text_area("Copy from here", text, height=350, key=f"box_{fmt}")
            st.download_button("Download .md", text, file_name=f"{fmt}.md", key=f"dl_{fmt}")


blog_tab, video_tab = st.tabs(["📝 Blog to posts", "🎬 Video to clips + posts"])

with blog_tab:
    blog = st.text_area("Paste your blog post", height=300)
    if st.button("Repurpose blog", type="primary"):
        try:
            with st.spinner("Writing..."):
                show_results(repurpose(blog, chosen, tone, mock))
        except Exception as e:  # show a readable message instead of a crash
            st.error(str(e))

with video_tab:
    upload = st.file_uploader("Upload a video", type=["mp4", "mov", "mkv", "webm"])
    n_clips = st.slider("Number of clips to suggest", 1, 6, 3)
    if st.button("Repurpose video", type="primary"):
        if not upload and not mock:
            st.warning("Please upload a video (or turn on mock mode).")
        else:
            try:
                path = ""
                if upload:
                    suffix = os.path.splitext(upload.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(upload.getbuffer())
                        path = tmp.name
                with st.spinner("Transcribing and finding the best moments..."):
                    segments = video.transcribe(path, mock=mock)
                    clips = video.find_clips(segments, n_clips, mock)
                    results = repurpose(video.transcript_to_text(segments), chosen, tone, mock)
                st.subheader("Suggested clips")
                for i, c in enumerate(clips, 1):
                    st.markdown(
                        f"**{i}. {c['title']}**  \n"
                        f"`{video.format_timestamp(c['start'])} - {video.format_timestamp(c['end'])}`  \n{c['why']}"
                    )
                with st.expander("Full transcript"):
                    st.write(video.transcript_to_text(segments))
                show_results(results)
            except Exception as e:
                st.error(str(e))
