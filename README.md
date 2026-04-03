# Grok Imagine Video — Hermes Agent Skill

A skill for the [Hermes agent](https://github.com/DevvGwardo/hermes) that provides image and video generation via [xAI's Grok Imagine API](https://docs.x.ai/developers/model-capabilities).

## Overview

Drop this into your Hermes agent's `~/.hermes/skills/` directory to enable natural language image and video generation directly from chat.

## Features

- **Text-to-image** — Generate images from text descriptions
- **Image editing** — Modify images via natural language instructions
- **Text-to-video** — Create video clips from text descriptions
- **Image-to-video** — Animate static images into motion
- **Video editing** — Apply filters, speed changes, color grading
- **Long video** — Videos beyond 15s via segmentation + ffmpeg

## Setup

1. **Get an API key** from [console.x.ai](https://console.x.ai/)

2. **Add to your Hermes config:**
   ```
   hermes config set xai_api_key YOUR_KEY
   ```

3. **Copy the skill** into your agent:
   ```
   cp -r hermes-grok-imagine-video ~/.hermes/skills/
   ```

## Usage

Once installed, just talk to Hermes naturally:

- "Create an image of a cyberpunk city at night"
- "Generate a video of a golden retriever running on the beach"
- "Animate this image — make the water look calm"
- "Edit this video — add a warm vintage filter"

See [SKILL.md](SKILL.md) for full documentation.
