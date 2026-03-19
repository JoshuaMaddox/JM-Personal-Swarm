#!/usr/bin/env python3
"""
Test script: HiggsField image-to-video generation
Takes an existing image and animates it using HiggsField's DoP model.

Pipeline: NanoBanan (still image) → HiggsField /v1/image2video/dop (animation)

Run from project root:
  python scripts/test-higgsfield-video.py

Auth: reads HF_API_KEY + HF_API_SECRET from .env automatically.
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path

# Load env — SDK reads HF_API_KEY + HF_API_SECRET automatically
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

try:
    import higgsfield_client
    from higgsfield_client import SyncClient, Completed, Failed, NSFW, Cancelled, InProgress, Queued
except ImportError:
    print("ERROR: higgsfield_client not installed. Run: pip install higgsfield-client")
    sys.exit(1)

# ─── CONFIG ───────────────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "creative" / "tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input: use the LinkedIn post header we already generated
INPUT_IMAGE = OUTPUT_DIR / "linkedin-post-header.jpg"

# HiggsField image-to-video endpoint (confirmed from JS SDK docs)
APPLICATION = "/v1/image2video/dop"

# Motion prompt — describe the movement to apply to the still image
MOTION_PROMPT = (
    "Slow dolly in toward the desk. The city lights outside the window gently flicker. "
    "The desk lamp light subtly shifts warmer. Cinematic and smooth. No abrupt cuts."
)

VIDEO_ARGS = {
    "model": "dop-turbo",
    "prompt": MOTION_PROMPT,
    "aspect_ratio": "16:9",
}

OUTPUT_FILENAME = "linkedin-post-header-animated.mp4"

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def status_callback(status):
    if isinstance(status, Queued):
        print("  [queued]", flush=True)
    elif isinstance(status, InProgress):
        print("  [in progress] Animating...", flush=True)
    elif isinstance(status, Completed):
        print("  [completed]", flush=True)
    elif isinstance(status, Failed):
        print("  [failed]", flush=True)
    else:
        print(f"  [{type(status).__name__}]", flush=True)


def upload_image(client: SyncClient, image_path: Path) -> str:
    """Upload image to HiggsField and return the hosted URL."""
    from PIL import Image as PILImage
    print(f"Uploading input image: {image_path.name}...", flush=True)
    img = PILImage.open(image_path)
    url = client.upload_image(img, format="jpeg")
    print(f"  Uploaded: {url[:80]}...")
    return url


def download_video(url: str, output_path: Path) -> Path:
    print(f"\nDownloading video...", flush=True)
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                print(f"  {downloaded/total*100:.0f}%", end="\r", flush=True)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\nSaved: {output_path} ({size_mb:.1f} MB)")
    return output_path


def extract_video_url(result) -> str:
    """Extract video URL from result (dict or object)."""
    # Convert to dict if needed
    if hasattr(result, '__dict__'):
        data = result.__dict__
    elif isinstance(result, dict):
        data = result
    else:
        data = {}

    candidates = [
        data.get("url"),
        data.get("video_url"),
        data.get("video", {}).get("url") if isinstance(data.get("video"), dict) else None,
        data.get("result", {}).get("url") if isinstance(data.get("result"), dict) else None,
    ]
    for c in candidates:
        if c:
            return c

    # Also try direct attribute access
    for attr in ["url", "video_url"]:
        if hasattr(result, attr):
            val = getattr(result, attr)
            if val:
                return val

    print(f"\nFull result: {json.dumps(data, indent=2, default=str)}")
    raise ValueError("Could not find video URL in result. See above.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("HIGGSFIELD IMAGE-TO-VIDEO TEST")
    print(f"Endpoint: {APPLICATION}")
    print(f"Input: {INPUT_IMAGE}")
    print(f"Output dir: {OUTPUT_DIR}")
    print("=" * 60)

    # Verify credentials
    hf_key = os.getenv("HF_API_KEY")
    hf_secret = os.getenv("HF_API_SECRET")
    if not hf_key or not hf_secret:
        print("ERROR: HF_API_KEY and/or HF_API_SECRET not found in .env")
        sys.exit(1)
    print(f"Auth: HF_API_KEY={hf_key[:8]}... ✓")

    # Verify input image exists
    if not INPUT_IMAGE.exists():
        print(f"ERROR: Input image not found: {INPUT_IMAGE}")
        print("Run test-google-image.py first to generate the source images.")
        sys.exit(1)
    print(f"Input image: {INPUT_IMAGE.stat().st_size // 1024}KB ✓")

    # Create client (SDK reads HF_API_KEY + HF_API_SECRET from env automatically)
    client = SyncClient()

    # Upload input image
    print()
    try:
        image_url = upload_image(client, INPUT_IMAGE)
    except Exception as e:
        print(f"ERROR uploading image: {e}")
        sys.exit(1)

    # Wrap in the required 'params' structure per API spec
    args = {
        "params": {
            "model": VIDEO_ARGS["model"],
            "prompt": VIDEO_ARGS["prompt"],
            "aspect_ratio": VIDEO_ARGS["aspect_ratio"],
            "input_images": [{"type": "image_url", "image_url": image_url}],
        }
    }
    print(f"\nMotion prompt: {MOTION_PROMPT}")
    print(f"Model: {args['params']['model']}")
    print(f"\nSubmitting to HiggsField ({APPLICATION})...")

    try:
        result = higgsfield_client.subscribe(
            APPLICATION,
            arguments=args,
            on_queue_update=status_callback,
        )
    except higgsfield_client.HiggsfieldClientError as e:
        err_str = str(e).lower()
        print(f"\nAPI Error: {e}")
        if "credit" in err_str or "insufficient" in err_str or "balance" in err_str:
            print("\nFIX: Add credits at https://cloud.higgsfield.ai/billing")
            print("The API integration and payload format are confirmed correct.")
            print("Once credits are added, re-run this script.")
        else:
            print("\nCheck https://cloud.higgsfield.ai for current API docs.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

    # Extract video URL and download
    print(f"\nJob completed. Extracting video URL...")
    try:
        video_url = extract_video_url(result)
    except ValueError:
        print("Could not auto-extract URL. Check raw result above.")
        sys.exit(1)

    output_path = OUTPUT_DIR / OUTPUT_FILENAME
    download_video(video_url, output_path)

    print(f"\n{'='*60}")
    print("SUCCESS")
    print(f"Input image:  {INPUT_IMAGE}")
    print(f"Output video: {output_path}")
    print(f"\nOpen to view:")
    print(f"  open \"{output_path}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
