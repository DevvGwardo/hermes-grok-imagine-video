# Grok Imagine Video

**Generate, animate, and edit images and videos using xAI's Grok Imagine API.**

Integrated as a [Hermes agent](https://github.com/DevvGwardo/hermes) skill for seamless natural-language control — or use the Python client directly in any project.

---

## Badges

![API](https://img.shields.io/badge/API-xAI%20Grok%20Imagine-20AA37?style=flat-square&logo=xai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-e8e8e8?style=flat-square)
![Video](https://img.shields.io/badge/Video-1--15s%20%7C%20Extended-FF6B6B?style=flat-square)
![Images](https://img.shields.io/badge/Images-Instant-4ECDC4?style=flat-square)

---

## Features

| Capability | Description | Latency |
|---|---|---|
| **Text-to-Image** | Generate images from natural language | Instant |
| **Image Editing** | Modify images via prompt | Instant |
| **Text-to-Video** | Create video clips from text | ~2-3 min |
| **Image-to-Video** | Animate a still image into motion | ~2-3 min |
| **Video Extension** | Continue a video from its last frame | ~2-3 min |
| **Video Editing** | Apply changes via natural language | ~2-3 min |
| **Long Video** | Narrative movies of any length via scene chaining | Scales with duration |

---

## Prerequisites

- **Python 3.9+**
- **ffmpeg** — required for video processing (`brew install ffmpeg` on macOS)
- **xAI API key** — get one at [console.x.ai](https://console.x.ai/)

---

## Installation

### As a Hermes Skill

```bash
# 1. Clone the repository
git clone https://github.com/DevvGwardo/hermes-grok-imagine-video.git

# 2. Copy into your Hermes skills directory
cp -r hermes-grok-imagine-video ~/.hermes/skills/grok-imagine-video

# 3. Set your API key
hermes config set xai_api_key YOUR_KEY
```

That's it. Hermes will automatically load the skill and expose all commands.

### As a Standalone Python Client

```bash
pip install requests
```

```python
import os
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(api_key=os.getenv("XAI_API_KEY"))
```

---

## Quick Start

### Images (instant)

```python
# Text-to-image
url = client.generate_image(
    prompt="A cyberpunk cityscape at night, neon reflections on wet streets",
    aspect_ratio="16:9"
)
print(url["data"][0]["url"])

# Image editing
url = client.edit_image(
    image_url="https://example.com/photo.jpg",
    prompt="Convert to a watercolor painting with warm tones"
)
```

### Videos (~2-3 min, async)

```python
# 1. Start generation
result = client.text_to_video(
    prompt="A sunset over the ocean, golden hour light reflecting on gentle waves",
    duration=10,
    resolution="720p"
)
request_id = result["request_id"]

# 2. Poll until done
video = client.wait_for_completion(request_id, poll_interval=10, timeout=600)

# 3. Download
client.download_video(video, "/tmp/sunset.mp4")
```

---

## Generating Long Videos

Videos are capped at 15 seconds per API call. For longer narratives, `generate_movie()` chains scenes together using **video-to-video extension** — the API generates content that continues directly from the end of each segment, giving smooth temporal continuity.

```python
segments = client.generate_movie(
    scenes=[
        {
            "prompt": "A superhero stands on a dark rooftop, cape billowing, city lights glowing below",
            "duration": 20,
            "image_url": "https://example.com/hero.jpg"
        },
        {
            "prompt": "Launching into a storm, lightning crackling, clouds rushing past",
            "duration": 20
        },
        {
            "prompt": "Soaring over a stormy ocean at sunset, massive waves below",
            "duration": 20
        },
        {
            "prompt": "Landing on a mountain peak as stars emerge in the darkening sky",
            "duration": 20
        },
    ],
    resolution="720p",
    output_dir="/tmp/movie_build"
)
```

Then add cinematic transitions and a music track:

```python
final = client.finalize_movie(
    segment_paths=segments,
    output_path="/tmp/cinematic_movie.mp4",
    transition_duration=1.5,       # cross-dissolve between scenes
    music_track="/path/to/score.mp3",
    music_crossfade=2.0,           # music fades at each scene boundary
    video_fade_out=3.0             # fade to black at the end
)
```

---

## Example Prompts

Use these as starting points for different video types.

### Cinematic / Film

| Scene Type | Example Prompt |
|---|---|
| Hero landing | "A superhero lands gracefully on a rooftop, cape settling around them. City lights shimmer below. Cinematic lighting, wide shot." |
| Storm launch | "The hero bursts upward through storm clouds, electricity arcing across the sky. Speed lines, dramatic low angle." |
| Ocean flight | "Flying low over a moonlit ocean, waves catching silver light. Smooth aerial tracking shot." |
| Mountain summit | "Landing on a snow-capped peak at golden hour. The hero turns to face the camera. Epic establishing shot." |
| City rooftop | "Standing tall on a rooftop at dusk, city sprawling below. Wind moves the cape. Cinematic atmosphere." |

### Nature / Landscape

| Scene Type | Example Prompt |
|---|---|
| Forest morning | "Sunlight streams through tall trees in a misty forest. Dew on leaves glistens. Peaceful, wide-angle." |
| Ocean waves | "Aerial shot of large waves crashing against rocky cliffs. Sea spray catches the light. Slow motion." |
| Mountain trek | "Tracking shot following a hiker up a mountain trail. Wildflowers on both sides. Fresh morning light." |
| Waterfall | "A powerful waterfall cascading down mossy rocks. Rainbow in the mist. Static wide shot." |
| Thunderstorm | "Dark storm clouds rolling over an open plain. Lightning strikes in the distance. Timelapse motion." |

### Urban / Architecture

| Scene Type | Example Prompt |
|---|---|
| Night street | "A rain-slicked neon street at midnight. Reflections shimmer on asphalt. Cinematic color grading." |
| Empty subway | "An empty subway platform, a single train arriving. Harsh fluorescent lighting. Moody atmosphere." |
| Skyscraper | "Drone shot circling a glass skyscraper at sunset. City skyline in background. Smooth orbit." |
| Market crowd | "A bustling street market, people moving through stalls. Warm lantern lighting. Documentary feel." |

### Character / Portrait Animation

| Scene Type | Example Prompt |
|---|---|
| Portrait turn | "The character slowly turns their head, looking over their shoulder with a slight confident smile. Soft studio lighting." |
| Walking | "The character walks confidently down a sunlit corridor, pausing to look at the camera. Natural light." |
| Surprise | "The character's expression shifts from calm to surprised, eyes widening. Close-up on face." |
| Action pose | "The character strikes a powerful heroic pose, cape billowing dynamically. Studio lighting, dramatic." |
| Dancing | "The character moves gracefully in a flowing dress, spinning slowly. Soft bokeh background." |

### Sci-Fi / Fantasy

| Scene Type | Example Prompt |
|---|---|
| Space station | "A vast space station rotating slowly against a planet. Stars in the background. Sci-fi atmosphere." |
| Dragon flight | "A dragon soaring through cloudy skies, wings spread wide. Epic scale, dramatic lighting." |
| Portal open | "A shimmering portal opens in a dark alleyway, bright light spilling out. Particle effects." |
| Robot activation | "A robot's eyes light up for the first time. Metallic reflections. Science fiction feel." |
| Laser battle | "Two characters exchange energy blasts in a futuristic arena. Speed lines and impact flashes." |

### Image Prompts (text-to-image)

| Style | Example Prompt |
|---|---|
| Photorealistic | "A close-up photograph of a wolf standing in snow, breath visible in cold air. National Geographic style." |
| Cyberpunk | "A cyberpunk street market at night, holographic advertisements, rain on neon signs, detailed digital art." |
| Oil painting | "An oil painting of a sailing ship at sunset, dramatic clouds, impasto brush texture visible." |
| Studio portrait | "Studio portrait of a person in their 30s, soft Rembrandt lighting, neutral background, fashion photography." |
| Landscape | "A vast desert canyon at golden hour, red rock formations, lone figure on cliff edge, cinematic composition." |
| Product shot | "Floating product photography of a sleek headphone on a dark background, soft studio lighting, minimal." |

---

## Method Reference

### Image Methods

```python
# Text-to-image
generate_image(prompt, n=1, aspect_ratio="1:1", response_format="url")
```

```python
# Edit an existing image
edit_image(image_url, prompt)
```

### Video Methods

```python
# Text-to-video
text_to_video(prompt, duration=10, aspect_ratio="16:9", resolution="480p")
```

```python
# Animate a still image
image_to_video(image_url, prompt, duration=10, reference_images=None)
```

```python
# Extend an existing video from its last frame
extend_video(video_url, prompt, duration=6)
```

```python
# Edit a video with natural language instructions
edit_video(video_url, edit_prompt)
```

### Polling

```python
# Check status manually
status = client.get_job_status(request_id)
# Returns: {"status": "pending" | "done" | "failed", "video": {...}, "error": {...}}

# Block until complete
video = client.wait_for_completion(request_id, poll_interval=10, timeout=600)
```

### Download

```python
# Download from a response or URL
client.download_video(response_data, "/tmp/output.mp4")
client.download_image(image_url, "/tmp/output.png")
```

### Long Video Methods

```python
# Narrative movie with scene chaining (recommended for 15s+)
generate_movie(scenes, resolution="480p", output_dir="/tmp", progress_callback=None, timeout=600)
# scenes: list of {"prompt": "...", "duration": N, "image_url": "..."} — image_url optional for scenes after the first

# Single-prompt long video (same motion throughout)
generate_long_video(prompt, total_duration, segment_duration=10, resolution="480p",
                    output_dir="/tmp", image_url=None, progress_callback=None, timeout=600)
```

```python
# Concatenate segments without transitions
concatenate_segments(segment_paths, output_path)

# Apply transitions, music, and fade-out
finalize_movie(segment_paths, output_path, transition_duration=1.0,
               music_track="", music_crossfade=2.0, video_fade_out=2.0, output_dir="/tmp")
```

---

## Parameter Reference

### Image Generation

| Parameter | Default | Range | Description |
|---|---|---|---|
| `prompt` | — | string | Text description of the desired image |
| `n` | 1 | 1–10 | Number of variations to generate |
| `aspect_ratio` | 1:1 | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3 | Aspect ratio |
| `response_format` | url | url, b64_json | Return format |

### Video Generation

| Parameter | Default | Range | Description |
|---|---|---|---|
| `prompt` | — | string | Text description of the video scene |
| `duration` | 10 | 1–15s | Length of the video |
| `aspect_ratio` | 16:9 | same as image | Aspect ratio |
| `resolution` | 480p | 480p, 720p | Quality — 480p is faster |
| `image_url` | — | URL or local path | Source image for image-to-video |
| `reference_images` | — | list of URLs | Reference images for R2V mode |
| `video_url` | — | URL or local path | Source video for extension/editing |

### Long Video

| Parameter | Default | Range | Description |
|---|---|---|---|
| `total_duration` | — | any | Total length for `generate_long_video` |
| `segment_duration` | 10 | 1–15s | Length per segment (10s recommended) |
| `transition_duration` | 1.0 | 0–10s | Cross-dissolve between segments |
| `video_fade_out` | 2.0 | 0–10s | Fade to black at end |
| `music_crossfade` | 2.0 | 0–10s | Music fade at scene boundaries |

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Missing or invalid API key | Set `xai_api_key` in Hermes config |
| `400 invalid_argument` | Local file URL not supported | Use HTTPS URL or local path (auto-converted to base64) |
| `400 Content policy` | Prompt violates guidelines | Rephrase without restricted terms |
| `429 Rate limit` | Too many requests | Wait 60s and retry |
| `TimeoutError` | Generation exceeded timeout | Increase `timeout` or reduce `duration` |
| `FileNotFoundError` | ffmpeg not installed | `brew install ffmpeg` (macOS) |

---

## File Structure

```
hermes-grok-imagine-video/
SKILL.md                              Hermes skill definition + usage guide
scripts/
  grok_video_api.py                   Python API client
references/
  api_reference.md                    Raw xAI API documentation
README.md
LICENSE
```

---

## License

MIT — see [LICENSE](LICENSE)
