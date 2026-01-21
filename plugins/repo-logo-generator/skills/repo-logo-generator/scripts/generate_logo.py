#!/usr/bin/env python3
"""
Logo generation with transparent background using Gemini + PIL.

This script generates high-quality logos by:
1. Using Gemini (google/gemini-3-pro-image-preview) with #ffffff background
2. Programmatically converting #ffffff pixels to transparent using PIL

Usage:
    uv run --with requests --with pillow generate_logo.py "Your logo prompt" --output logo.png

Environment:
    SKILL_OPENROUTER_API_KEY - Required API key from https://openrouter.ai/keys

Dependencies: requests, pillow
"""

import argparse
import base64
import io
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required.", file=sys.stderr)
    print("Run with: uv run --with requests --with pillow generate_logo.py ...", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: pillow library required.", file=sys.stderr)
    print("Run with: uv run --with requests --with pillow generate_logo.py ...", file=sys.stderr)
    sys.exit(1)


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str):
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://claude.ai/claude-code",
            "X-Title": "Claude Code"
        }

    def _request(self, method: str, endpoint: str, payload: dict = None, max_retries: int = 3):
        """Make API request with retry logic."""
        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}/{endpoint}"

        for attempt in range(max_retries):
            try:
                if method == "GET":
                    response = requests.get(url, headers=self.headers, timeout=120)
                else:
                    response = requests.post(url, headers=self.headers, json=payload, timeout=120)

                if response.status_code == 200:
                    return response.json()

                error = response.json().get("error", {})
                code = error.get("code", response.status_code)
                message = error.get("message", response.text)

                # Retryable errors
                if code in [408, 429, 502, 503] and attempt < max_retries - 1:
                    wait = min(2 ** attempt * 2, 30)
                    print(f"Retrying in {wait}s (attempt {attempt + 1}/{max_retries})...", file=sys.stderr)
                    time.sleep(wait)
                    continue

                # Non-retryable errors
                error_messages = {
                    400: "Bad request - check parameters",
                    401: "Invalid API key - check SKILL_OPENROUTER_API_KEY",
                    402: "Insufficient credits - add funds at openrouter.ai",
                    403: "Content flagged by moderation",
                    429: "Rate limited - wait before retrying"
                }
                msg = error_messages.get(code, message)
                raise Exception(f"OpenRouter error {code}: {msg}")

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    continue
                raise Exception("Request timed out after retries")
            except requests.exceptions.RequestException as e:
                raise Exception(f"Network error: {e}")

        raise Exception("Max retries exceeded")

    def generate_image(self, model: str, prompt: str, aspect_ratio: str = "1:1",
                       size: str = "1K") -> list:
        """Generate image using chat completions endpoint."""
        image_config = {"aspect_ratio": aspect_ratio, "image_size": size}

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
            "image_config": image_config,
            "n": 1
        }

        result = self._request("POST", "chat/completions", payload)
        images = result["choices"][0]["message"].get("images", [])
        return images


def convert_white_to_transparent(image_bytes: bytes, tolerance: int = 10) -> Image.Image:
    """Convert #ffffff (white) pixels to transparent.

    Args:
        image_bytes: Input image as bytes
        tolerance: Color tolerance for white detection (0-255)

    Returns:
        PIL Image with transparency
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Get image dimensions
    width, height = img.size

    # Replace white pixels with transparent
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # Check if pixel is white (within tolerance)
            if r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance:
                # Make transparent
                pixels[x, y] = (255, 255, 255, 0)

    return img


def main():
    parser = argparse.ArgumentParser(
        description="Logo generation with Gemini + programmatic transparency"
    )
    parser.add_argument("prompt", help="Logo description prompt")
    parser.add_argument("--output", "-o", default="logo.png", help="Output filename")
    parser.add_argument("--aspect", "-a", default="1:1", help="Aspect ratio (1:1, 16:9, etc)")
    parser.add_argument("--size", "-z", default="1K", help="Size (1K, 2K, 4K)")
    parser.add_argument("--model", "-m", default="google/gemini-3-pro-image-preview",
                        help="Model to use for generation")
    parser.add_argument("--tolerance", "-t", type=int, default=10,
                        help="White pixel tolerance (0-255, default 10)")
    parser.add_argument("--keep-original", action="store_true",
                        help="Keep original image with white background")

    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("SKILL_OPENROUTER_API_KEY")
    if not api_key:
        print("Error: SKILL_OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        print("Get your key at: https://openrouter.ai/keys", file=sys.stderr)
        sys.exit(1)

    client = OpenRouterClient(api_key)
    output_path = Path(args.output).resolve()

    try:
        # Enhance prompt to request #ffffff background
        enhanced_prompt = f"{args.prompt}\n\nIMPORTANT: Use pure white (#ffffff) for the background only. Do not use white (#ffffff) anywhere else in the design - the logo/icon itself should use other colors."

        # Generate with Gemini
        print(f"Generating with {args.model}...", file=sys.stderr)
        images = client.generate_image(
            args.model,
            enhanced_prompt,
            aspect_ratio=args.aspect,
            size=args.size
        )

        if not images:
            print("Error: No images generated", file=sys.stderr)
            sys.exit(1)

        # Get image data URL
        data_url = images[0]["image_url"]["url"]
        base64_data = data_url.split(",")[1]
        image_bytes = base64.b64decode(base64_data)

        print("✓ Image generation complete", file=sys.stderr)

        # Save original if requested
        if args.keep_original:
            original_path = output_path.parent / f"{output_path.stem}_original{output_path.suffix}"
            original_path.parent.mkdir(parents=True, exist_ok=True)
            with open(original_path, "wb") as f:
                f.write(image_bytes)
            print(f"  Saved original: {original_path}", file=sys.stderr)

        # Convert white to transparent
        print("Converting #ffffff to transparent...", file=sys.stderr)
        transparent_img = convert_white_to_transparent(image_bytes, tolerance=args.tolerance)
        print("✓ Transparency conversion complete", file=sys.stderr)

        # Save final output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        transparent_img.save(output_path, format='PNG')

        print(f"✓ Saved logo: {output_path}", file=sys.stderr)
        print(f"\nSuccess! Transparent logo created at: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
