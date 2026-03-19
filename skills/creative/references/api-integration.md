# API Integration Reference — Google AI + HiggsField

## Environment Variables

All credentials live in `/Users/joshuamaddox/Documents/code/JM-Personal-Swarm/.env`

```
GOOGLE_AI_API_KEY=...          # Gemini image generation
HIGGSFIELD_API_KEY_ID=...      # HiggsField auth ID
HIGGSFIELD_API_KEY_SECRET=...  # HiggsField auth secret
HF_API_KEY=...                 # HiggsField alternate key (same account)
HF_API_SECRET=...              # HiggsField alternate secret (same account)
```

Load with `python-dotenv`:
```python
from dotenv import load_dotenv
import os
load_dotenv('/Users/joshuamaddox/Documents/code/JM-Personal-Swarm/.env')
GOOGLE_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
HF_KEY_ID = os.getenv('HIGGSFIELD_API_KEY_ID')
HF_KEY_SECRET = os.getenv('HIGGSFIELD_API_KEY_SECRET')
```

---

## Google AI — Image Generation

### Installation
```bash
pip install google-genai pillow python-dotenv
```

### Core Image Generation Pattern

```python
import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv('/Users/joshuamaddox/Documents/code/JM-Personal-Swarm/.env')

client = genai.Client(api_key=os.getenv('GOOGLE_AI_API_KEY'))

def generate_image(prompt: str, output_path: str, model: str = "nano-banana-pro-preview") -> str:
    """
    Generate an image using Gemini and save to disk.
    Returns the path to the saved file.
    """
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"]
        )
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = part.inline_data.data  # already raw bytes — do NOT base64 decode
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(image_data)
            print(f"Image saved: {output_path}")
            return output_path

    raise ValueError("No image in response. Check prompt for policy violations.")

# Usage:
image_path = generate_image(
    prompt="YOUR PROMPT HERE",
    output_path="outputs/creative/tests/test-workspace-header.png"
)
```

### Aspect Ratio Guidance

Gemini image generation does not accept explicit pixel dimensions — it infers from prompt language. Include the ratio in natural language:

```python
# For 16:9 (LinkedIn post header)
prompt += " Wide landscape format, 16:9 aspect ratio."

# For 1:1 (carousel slide)
prompt += " Square format, 1:1 aspect ratio."

# For 9:16 (YouTube Short / thumbnail)
prompt += " Vertical portrait format, 9:16 aspect ratio, taller than wide."
```

Then resize after generation using Pillow:

```python
from PIL import Image

def resize_to_spec(input_path: str, output_path: str, width: int, height: int):
    """Resize and crop image to exact platform spec."""
    img = Image.open(input_path)
    # Calculate crop to maintain aspect ratio
    target_ratio = width / height
    current_ratio = img.width / img.height

    if current_ratio > target_ratio:
        # Image too wide — crop sides
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        # Image too tall — crop top/bottom
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))

    img = img.resize((width, height), Image.LANCZOS)
    img.save(output_path, quality=95)
    return output_path
```

### Error Handling

```python
from google.api_core import exceptions

def generate_image_safe(prompt: str, output_path: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return generate_image(prompt, output_path)
        except exceptions.InvalidArgument as e:
            print(f"Policy block on attempt {attempt + 1}: {e}")
            # Strip potentially blocked content and retry
            prompt = prompt.replace("Bangkok", "modern Asian city")
            prompt = prompt.replace("Joshua Maddox", "a 35-year-old man")
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
    return None
```

---

## HiggsField — Image-to-Video Generation

**Important:** HiggsField's API supports **image-to-video** animation (DoP model). Kling 3.0, Veo 3.1, and other generative video models are web-only at `higgsfield.ai/create/video`. The programmatic pipeline is: NanoBanan generates still → HiggsField animates it.

**Endpoint:** `POST /v1/image2video/dop`
**SDK:** `higgsfield_client` (official Python package)
**Auth:** Set `HF_API_KEY` and `HF_API_SECRET` in `.env` — SDK reads them automatically and constructs `Authorization: Key {ID}:{SECRET}` header.
**Credits required:** Video generation costs credits. Top up at `cloud.higgsfield.ai/billing`.

### Core Image-to-Video Pattern

```python
import higgsfield_client
from higgsfield_client import SyncClient
from PIL import Image
from dotenv import load_dotenv
import requests
from pathlib import Path

load_dotenv('/Users/joshuamaddox/Documents/code/JM-Personal-Swarm/.env')
# SDK auto-reads HF_API_KEY + HF_API_SECRET from env

def animate_image(image_path: str, motion_prompt: str, output_path: str,
                  aspect_ratio: str = "16:9") -> str:
    """
    Animate a still image using HiggsField DoP model.
    Returns path to saved MP4.

    image_path: path to a JPG/PNG image (generated by NanoBanan)
    motion_prompt: description of desired camera movement and motion
    aspect_ratio: "16:9" for LinkedIn/X, "9:16" for YouTube Shorts
    """
    client = SyncClient()  # reads HF_API_KEY + HF_API_SECRET automatically

    # Upload the still image
    img = Image.open(image_path)
    image_url = client.upload_image(img, format="jpeg")

    # Submit animation job — note: params wrapper is required
    result = higgsfield_client.subscribe(
        '/v1/image2video/dop',
        arguments={
            "params": {
                "model": "dop-turbo",
                "prompt": motion_prompt,
                "aspect_ratio": aspect_ratio,
                "input_images": [{"type": "image_url", "image_url": image_url}],
            }
        },
        on_queue_update=lambda s: print(f"  Status: {type(s).__name__}"),
    )

    # Extract video URL (response shape: {"video": {"url": "..."}})
    video_url = (
        result.get("url") or
        result.get("video", {}).get("url") or
        result.get("video_url")
    )
    if not video_url:
        raise ValueError(f"No video URL in result: {result}")

    # Download to disk
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(video_url, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    print(f"Video saved: {output_path}")
    return output_path
```

### Motion Prompt Templates (for DoP model)

```
# Workspace ambient B-roll
"Slow dolly in toward the desk. City lights outside the window gently flicker. Desk lamp light subtly shifts warmer. Cinematic and smooth."

# Establishing reveal
"Slow pan right across the workspace. Floor-to-ceiling windows reveal the full Bangkok skyline. Smooth and cinematic."

# Focus pull
"Camera holds still. Subtle rack focus from the foreground notebook to the city lights in the background window."

# Atmospheric
"No camera movement. The only motion: steam rising from the coffee mug and the ambient flicker of city lights outside."
```

---

## Model Selection Decision Tree

```
Need IMAGES?
  → Use Google AI (Gemini) → gemini-2.0-flash-preview-image-generation

Need VIDEO?
  → Multi-shot / social content / camera movement precision?
      YES → Kling 3.0
  → Commercial quality / every frame must look like a film?
      YES → Veo 3.1
  → Physics-critical (liquid, fabric, impact)?
      YES → Sora 2
  → Budget-conscious or primarily about camera move over still?
      YES → WAN 2.5
  → DEFAULT → Kling 3.0
```

---

## Output File Naming Convention

```
outputs/creative/[YYYY-MM-DD]/[platform]-[format]-[slot].[ext]

Examples:
outputs/creative/2026-03-18/linkedin-carousel-slide-bg-monday.png
outputs/creative/2026-03-18/youtube-thumbnail-monday.png
outputs/creative/2026-03-18/youtube-broll-opening.mp4
outputs/creative/2026-03-18/linkedin-post-header-wednesday.png
```

---

## Dependency Installation

```bash
pip install google-genai pillow python-dotenv requests
```

Verify installation:
```bash
python -c "from google import genai; import PIL; import requests; print('All dependencies OK')"
```
