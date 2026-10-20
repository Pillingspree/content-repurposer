# Beginner's Guide: What Every Part Does

You do not need to read code to own this project. This guide explains what each file does, what it means for the product, and what changes if you edit it.

## The big picture

Think of the tool as a small factory:

1. **Input**: a blog post, or a video.
2. **Brain**: Claude (an AI) rewrites the content for each platform.
3. **Output**: files and on-screen tabs you can copy and post.

## The files, one by one

### `repurposer/prompts.py`: the instructions
**What it is:** plain-English instructions for the AI, one per platform (for example "LinkedIn post, 150-250 words, strong hook, end with a question").
**Impact on the project:** this is the *quality and style* of your product. Better instructions mean better posts.
**Safe to edit?** Yes, this is the best file to experiment with. Change "6 to 8 tweets" to "10 tweets" and every thread changes.

### `repurposer/generator.py`: the engine
**What it is:** reads your blog, sends it to Claude once per format, and collects the answers.
**Impact:** this is the core feature. It also contains **mock mode**, which returns placeholder text instead of calling the AI.
**Why that matters:** each real call to Claude costs a small amount of money. Mock mode lets you demo, test and develop for free.
**Safety built in:** it refuses empty text and unknown formats, so the tool fails with a clear message, not a confusing crash.

### `repurposer/video.py`: the video feature
**What it is:** three steps. (1) Convert speech to text with timestamps. (2) Ask Claude which 20-60 second moments make the best short clips. (3) Cut those moments into separate files.
**Impact:** this is what makes your project stand out in a portfolio. Most repurposing tools only handle text.
**Cost:** transcription runs on the user's own computer, so it is free. Only the clip-picking step uses the AI.
**Needs:** the extra packages in `requirements-video.txt` and a free program called ffmpeg for cutting.

### `repurposer/cli.py` and `__main__.py`: the terminal interface
**What it is:** lets people run the tool with typed commands like `python -m repurposer text my_blog.md`.
**Impact:** makes the tool scriptable, so it can later run automatically (for example every time you publish a post).

### `app.py`: the web interface
**What it is:** a simple web page (built with Streamlit) with tabs for blog and video, a tone picker, and copy/download buttons.
**Impact:** this is what you screenshot for your portfolio and what non-technical users would use.

### `tests/test_repurposer.py`: the safety net
**What it is:** small automated checks, for example "does the tool return all five formats?" and "does it reject empty input?".
**Impact:** when you or a developer change something later, running the tests tells you immediately if something broke. Employers and investors look for tests in a repository.

### `requirements.txt` and `requirements-video.txt`: the shopping lists
**What they are:** lists of the outside software the project depends on. One command installs everything.
**Impact:** anyone can set the project up in minutes. The video list is separate so text users do not have to download the heavier speech model.

### `.env.example` and `.gitignore`: protecting your secrets
**What they are:** `.env` holds your secret API key. `.gitignore` tells GitHub to **never upload** it.
**Impact:** this is critical. If an API key is uploaded to a public GitHub repo, strangers can find it and spend your money. Never delete the `.env` line from `.gitignore`.

### `README.md`: the shop window
**What it is:** the first thing visitors see on GitHub. It explains what the project is and how to run it.
**Impact:** for a portfolio, this matters as much as the code.

## Putting it on GitHub (step by step)

1. Create a free account at github.com if you have not already.
2. Click **New repository**. Name it `content-repurposer`. Choose **Public**. Do **not** tick "Add a README" (we already have one).
3. Unzip the project folder on your computer and open a terminal inside it.
4. Run these commands one at a time:

```bash
git init
git add .
git commit -m "Initial commit: content repurposing tool"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/content-repurposer.git
git push -u origin main
```

What each does: `git init` starts tracking changes in the folder. `git add .` selects all files. `git commit` saves a snapshot with a label. `git remote add` connects your folder to the GitHub page you made. `git push` uploads it.

5. Open your repository page and check that `.env` is **not** listed. Only `.env.example` should be there.

## Making it look great in a portfolio

- Add 2 screenshots of the web app to the README.
- Run it on `examples/sample_blog.md` with a real key and paste one output into the README as a demo.
- Pin the repository on your GitHub profile.

## Cost awareness

Each blog repurposed into 5 formats makes 5 AI calls, typically a few cents in total. A video adds one more call. Mock mode is free.
