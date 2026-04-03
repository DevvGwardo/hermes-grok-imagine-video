---
name: hermes-grok-imagine-video
description: Hermes agent skill for xAI Grok Imagine API — generate, edit, and animate images and videos via natural language. Use when the user wants to create images, videos, or animations using xAI's Grok Imagine API.
version: 1.0.0
tags: [video, image, generation, xai, grok, hermes, text-to-video, image-to-video, editing]
required_env: [XAI_API_KEY]
commands: [python3]
metadata:
  hermes:
    platform: hermes-agent
    triggers:
      - "generate an image"
      - "create a video"
      - "generate a video"
      - "animate this image"
      - "edit this video"
      - "make a video of"
      - "grok imagine"
      - "xai image"
      - "xai video"
---

# Grok Imagine Video — Hermes Agent Skill

Generate images and videos using xAI's Grok Imagine API directly from the Hermes agent chat interface.

## When to Use

- User wants to generate an image from a text description
- User wants to create a video from text or an image
- User wants to animate a static image into video
- User wants to edit an existing image or video with natural language
- Keywords: imagine, generate, create video, create image, xai, grok

## Setup

**Required:** `XAI_API_KEY` from https://console.x.ai/

The skill reads the key from the `XAI_API_KEY` environment variable automatically. If not set, the agent requests it from the user before proceeding.

**Runtime:** Python 3 with the `requests` library.

## Capabilities

| Feature | Description | Latency |
|---------|-------------|---------|
| Text-to-image | Generate images from text (up to 10 variations) | Instant |
| Image editing | Edit images via natural language | Instant |
| Text-to-video | Create videos from text descriptions | ~2-3 min |
| Image-to-video | Animate a static image into video | ~2-3 min |
| Video editing | Apply filters, speed, color grading via natural language | ~2-3 min |
| Long video | Videos longer than 15s via frame-chaining + ffmpeg | Scales with length |

## Workflows

### Image Generation (instant)

**User says:** "Create an image of a cyberpunk cityscape at night"

```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))
result = client.generate_image(
    prompt="A cyberpunk cityscape at night, neon lights reflecting on wet streets",
    n=1,
    aspect_ratio="16:9",
    response_format="url"
)
print(result.get("data", [{}])[0].get("url", ""))
EOF
```

Images generate instantly. Return the URL directly to the user.

### Image Editing (instant)

**User says:** "Edit this image — make it look like a watercolor painting"

```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))
result = client.edit_image(
    image_url="https://example.com/photo.jpg",
    prompt="Make it look like a watercolor painting"
)
print(result.get("data", [{}])[0].get("url", ""))
EOF
```

### Text-to-Video (~2-3 min, async)

**User says:** "Generate a video of a sunset over the ocean"

Step 1 — Start generation:
```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))
result = client.text_to_video(
    prompt="A beautiful sunset over the ocean, golden hour lighting",
    duration=10,
    aspect_ratio="16:9",
    resolution="720p"
)
print(result.get("request_id", ""))
EOF
```

Step 2 — Poll for completion:
```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))

def progress(response):
    done = "video" in response
    print(f"Polling... {'Done!' if done else 'Pending'}")

final = client.wait_for_completion(
    "REQUEST_ID_HERE",
    poll_interval=10,
    timeout=600,
    progress_callback=progress
)
print(final.get("video", {}).get("url", ""))
EOF
```

Step 3 — Download and deliver:
```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))
output = "/tmp/video_output.mp4"
client.download_video({"video": {"url": "VIDEO_URL_HERE"}}, output)
print(output)
EOF
```

Send the file to the user with `MEDIA:/tmp/video_output.mp4`.

### Image-to-Video

**User says:** "Animate this image — make the clouds move slowly"

```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))
result = client.image_to_video(
    image_url="https://example.com/landscape.jpg",
    prompt="Make the clouds drift slowly across the sky",
    duration=10
)
print(result.get("request_id", ""))
EOF
```

Then poll with `wait_for_completion()` and download as above.

### Video Editing

**User says:** "Edit this video — add a warm sunset filter and slow it to 50% speed"

```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))
result = client.edit_video(
    video_url="https://example.com/clip.mp4",
    edit_prompt="Add a warm sunset filter and slow down to 50% speed"
)
print(result.get("request_id", ""))
EOF
```

Then poll and download.

### Long Video (beyond 15s)

For videos longer than 15 seconds, the client generates segments **sequentially** and chains them — after each segment completes, it extracts the last frame and feeds it as input to the next segment. This creates smooth continuous motion instead of jump cuts.

If a starting `image_url` is provided, the first segment animates that image. Each subsequent segment builds from the last frame of the previous one.

```
python3 - << 'EOF'
import os, sys
sys.path.insert(0, 'scripts')
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))

def progress(idx, total, status):
    print(f"Segment {idx+1}/{total}: {status}")

# Option A: Animate a starting image (chained from last frames)
segments = client.generate_long_video(
    prompt="The superhero stands heroically, cape billowing. Camera zooms out revealing a city skyline. Hero takes flight, soaring through clouds.",
    total_duration=60,
    segment_duration=10,        # 10s per segment recommended for chaining
    resolution="720p",
    output_dir="/tmp",
    progress_callback=progress,
    image_url="https://example.com/hero.jpg"   # Optional starting image
)

# Option B: Text-to-video long video (no image chaining)
segments = client.generate_long_video(
    prompt="A cinematic journey through ancient ruins at golden hour",
    total_duration=60,
    segment_duration=10,
    resolution="720p",
    output_dir="/tmp",
    progress_callback=progress
)

output = "/tmp/long_video.mp4"
client.concatenate_segments(segments, output)
print(output)
EOF
```

Send the final file with `MEDIA:/tmp/long_video.mp4`.

## Parameters Reference

### Image Generation

| Param | Default | Notes |
|-------|---------|-------|
| `prompt` | required | Be descriptive |
| `n` | 1 | 1-10 variations |
| `aspect_ratio` | 1:1 | 16:9, 9:16, 4:3, 3:4, 3:2, 2:3 |
| `response_format` | url | or b64_json |

### Video Generation (text-to-video, image-to-video)

| Param | Default | Notes |
|-------|---------|-------|
| `prompt` | required | Specific, include camera direction |
| `duration` | 10 | 1-15 seconds |
| `aspect_ratio` | 16:9 | same options as image |
| `resolution` | 480p | 480p (faster) or 720p (quality) |

### Long Video

| Param | Default | Notes |
|-------|---------|-------|
| `total_duration` | required | Any length |
| `segment_duration` | 15 | Max 15s per API call |
| `resolution` | 480p | 480p or 720p |

## Error Handling

| Error | Response |
|-------|----------|
| `401 Unauthorized` | API key missing or invalid — request key from user |
| `429 Rate limit` | Wait and retry with exponential backoff |
| `400 Content policy` | Rephrase prompt to comply with content guidelines |
| `TimeoutError` | Reduce duration or complexity |
| `FileNotFoundError` | Install ffmpeg (`brew install ffmpeg` on macOS) |

## Best Practices

- **Images are instant** — deliver URLs immediately without polling
- **Videos take 2-3 minutes** — send progress updates to the user while polling
- **Be descriptive in prompts** — specify style, lighting, camera movement
- **For videos, include camera direction** — "slow pan", "drone shot over", "close-up of"
- **Use 480p for fast iteration** — switch to 720p for final output
- **Download promptly** — image/video URLs are temporary and expire
- **Deliver via MEDIA:** — use `MEDIA:/path/to/file` to send files natively in chat

## File Structure

```
hermes-grok-imagine-video/
SKILL.md                              ← This file
scripts/grok_video_api.py             ← API client
references/api_reference.md            ← Full API documentation
README.md
LICENSE
```
