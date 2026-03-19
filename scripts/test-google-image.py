#!/usr/bin/env python3
"""
Test script: Google AI (Gemini) image generation
Generates 3 test images using Joshua's locked visual identity.

Run from project root:
  python scripts/test-google-image.py
"""

import os
import base64
import sys
from pathlib import Path
from datetime import date

# Load env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

# Check key
GOOGLE_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_AI_API_KEY not found in .env")
    sys.exit(1)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

try:
    from PIL import Image
    import io
except ImportError:
    print("ERROR: pillow not installed. Run: pip install pillow")
    sys.exit(1)

# ─── CONFIG ───────────────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "creative" / "tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "nano-banana-pro-preview"

# Joshua's fixed brand DNA block — included in every prompt
BRAND_DNA = """Shot on Sony A7 IV, 35mm f/1.8, Kodak Portra 400 color grade. \
No airbrushing. No oversaturation. No symmetrical composition. \
Not stock photography. Not CGI. Not a digital render. \
Natural grain. Editorial documentary aesthetic."""

# ─── PROMPTS ──────────────────────────────────────────────────────────────────

PROMPTS = [
    {
        "name": "linkedin-post-header",
        "filename": "linkedin-post-header-test.png",
        "target_size": (1200, 628),
        "description": "LinkedIn post header — Bangkok workspace wide shot",
        "prompt": f"""{BRAND_DNA}

Wide establishing shot of a modern Bangkok high-rise workspace at blue hour. \
Floor-to-ceiling windows dominate the right two-thirds of the frame, revealing the Bangkok skyline \
with city lights beginning to glow against a deep blue sky. A worn oak desk sits in the left foreground, \
a single amber desk lamp casting warm light on scattered handwritten notebooks. A ceramic mug sits beside them. \
No person present. Camera: Sony A7 IV, 35mm f/1.8 at f/2.8. \
Electric blue from the city sky contrasting with warm amber desk light. \
Rule of thirds. Landscape orientation, 16:9 aspect ratio."""
    },
    {
        "name": "carousel-slide-dark",
        "filename": "carousel-slide-dark-bg-test.png",
        "target_size": (1080, 1080),
        "description": "LinkedIn carousel slide — dark background, text-safe",
        "prompt": f"""{BRAND_DNA}

Close-up detail shot of a Bangkok workspace desk surface at night. \
Deep navy ambient city light from a large window fills the background. \
A single electric blue monitor glow illuminates the edge of an open notebook and black pen \
in the lower-left corner of frame. The center and lower 60% of the frame is intentionally \
dark and uncluttered — clear space for text overlay. No person present. \
Shallow depth of field, notebook edge sharp, window background dissolved into deep navy. \
Sony A7 IV, 35mm f/1.8 at f/1.8. Cinestill 800T color temperature. \
Very minimal composition. Square format, 1:1 aspect ratio."""
    },
    {
        "name": "youtube-thumbnail",
        "filename": "youtube-thumbnail-test.png",
        "target_size": (1080, 1920),
        "description": "YouTube Short thumbnail — vertical portrait format",
        "prompt": f"""{BRAND_DNA}

Portrait-format close-up of a 35-year-old man, short dark hair, slight stubble, \
three-quarter angle, looking slightly off-camera to the left as if concentrating on something \
beyond the frame. Bangkok cityscape visible through a large window behind him at blue hour, \
city lights soft and glowing out of focus. He wears a plain dark navy crewneck. \
Expression: focused, curious — mid-thought, not performing for camera. \
Rembrandt lighting from the left window, soft natural shadow on the right side of his face. \
Shallow depth of field — face sharp, cityscape completely soft. \
Lower 40% of frame intentionally darker for text overlay. \
Sony A7 IV, 35mm f/1.8 at f/1.8. Kodak Portra 400. \
Vertical portrait format, 9:16 aspect ratio, taller than wide."""
    },
]

# ─── GENERATION ───────────────────────────────────────────────────────────────

def generate_and_save(client, prompt_config: dict) -> dict:
    """Generate one image and save to disk. Returns result dict."""
    name = prompt_config["name"]
    filename = prompt_config["filename"]
    prompt = prompt_config["prompt"]
    target_size = prompt_config["target_size"]
    output_path = OUTPUT_DIR / filename

    print(f"\n{'─'*60}")
    print(f"Generating: {name}")
    print(f"Description: {prompt_config['description']}")
    print(f"Target size: {target_size[0]}×{target_size[1]}")
    print(f"Output: {output_path}")
    print("Sending to Gemini...", end=" ", flush=True)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        image_data = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                image_data = part.inline_data.data  # already raw bytes
                break

        if not image_data:
            print("FAILED — no image in response")
            # Print any text response for debugging
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    print(f"Model response text: {part.text[:200]}")
            return {"name": name, "status": "failed", "error": "no image data in response"}

        # Save raw image
        raw_path = OUTPUT_DIR / f"{name}-raw.png"
        with open(raw_path, 'wb') as f:
            f.write(image_data)

        # Resize to platform spec
        img = Image.open(io.BytesIO(image_data))
        print(f"Generated ({img.width}×{img.height})", end=" ")

        # Crop and resize to target
        target_w, target_h = target_size
        target_ratio = target_w / target_h
        current_ratio = img.width / img.height

        if abs(current_ratio - target_ratio) > 0.05:
            if current_ratio > target_ratio:
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            else:
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))

        img = img.resize(target_size, Image.LANCZOS)
        img.save(output_path, quality=95)
        print(f"→ resized to {target_w}×{target_h} ✓")
        print(f"Saved: {output_path}")

        return {
            "name": name,
            "status": "success",
            "path": str(output_path),
            "size": f"{target_w}×{target_h}",
        }

    except Exception as e:
        print(f"ERROR: {e}")
        return {"name": name, "status": "failed", "error": str(e)}


def main():
    print("=" * 60)
    print("GOOGLE AI IMAGE GENERATION TEST")
    print(f"Model: {MODEL}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Generating {len(PROMPTS)} test images")
    print("=" * 60)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    results = []

    for prompt_config in PROMPTS:
        result = generate_and_save(client, prompt_config)
        results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    print(f"✓ Succeeded: {len(success)}/{len(results)}")
    for r in success:
        print(f"  → {r['name']}: {r['path']} ({r['size']})")

    if failed:
        print(f"✗ Failed: {len(failed)}/{len(results)}")
        for r in failed:
            print(f"  → {r['name']}: {r['error']}")

    if success:
        print(f"\nOpen your output directory to view results:")
        print(f"  open {OUTPUT_DIR}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
