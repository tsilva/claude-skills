#!/usr/bin/env python3
"""
Two-step logo generation: Gemini for quality + GPT-5 Image for transparency.

This script generates high-quality logos by:
1. Using Gemini (google/gemini-3-pro-image-preview) for superior image generation
2. Using GPT-5 Image (openai/gpt-5-image) to convert to transparent background

Usage:
    uv run --with requests generate_logo_two_step.py "Your logo prompt" --output logo.png

Environment:
    SKILL_OPENROUTER_API_KEY - Required API key from https://openrouter.ai/keys

Dependencies: requests
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required.", file=sys.stderr)
    print("Run with: uv run --with requests generate_logo_two_step.py ...", file=sys.stderr)
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
                       size: str = "1K", background: str = None, quality: str = None,
                       output_format: str = None) -> list:
        """Generate image using chat completions endpoint."""
        image_config = {"aspect_ratio": aspect_ratio, "image_size": size}

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
            "image_config": image_config,
            "n": 1
        }

        # Add top-level parameters (for OpenAI GPT Image models)
        if background:
            payload["background"] = background
        if quality:
            payload["quality"] = quality
        if output_format:
            payload["output_format"] = output_format

        result = self._request("POST", "chat/completions", payload)
        images = result["choices"][0]["message"].get("images", [])
        return images

    def convert_image_to_transparent(self, input_image_data: str, aspect_ratio: str = "1:1",
                                      size: str = "1K") -> list:
        """Convert an existing image to transparent background using GPT-5 Image."""
        payload = {
            "model": "openai/gpt-5-image",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": input_image_data}
                        },
                        {
                            "type": "text",
                            "text": "Remove the background from this image. Keep the logo/icon exactly as it is, but make the entire background completely transparent."
                        }
                    ]
                }
            ],
            "modalities": ["image", "text"],
            "image_config": {
                "aspect_ratio": aspect_ratio,
                "image_size": size
            },
            "background": "transparent",
            "quality": "high",
            "output_format": "png",
            "n": 1
        }

        result = self._request("POST", "chat/completions", payload)
        images = result["choices"][0]["message"].get("images", [])
        return images


def image_to_base64_data_url(image_data: bytes) -> str:
    """Convert image bytes to base64 data URL."""
    b64_data = base64.b64encode(image_data).decode()
    return f"data:image/png;base64,{b64_data}"


def save_image(image_data_url: str, output_path: Path):
    """Save base64 data URL to file."""
    base64_data = image_data_url.split(",")[1]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(base64_data))


def main():
    parser = argparse.ArgumentParser(
        description="Two-step logo generation: Gemini for quality + GPT-5 for transparency"
    )
    parser.add_argument("prompt", help="Logo description prompt")
    parser.add_argument("--output", "-o", default="logo.png", help="Output filename")
    parser.add_argument("--aspect", "-a", default="1:1", help="Aspect ratio (1:1, 16:9, etc)")
    parser.add_argument("--size", "-z", default="1K", help="Size (1K, 2K, 4K)")
    parser.add_argument("--gemini-model", default="google/gemini-3-pro-image-preview",
                        help="Gemini model for initial generation")
    parser.add_argument("--keep-intermediate", action="store_true",
                        help="Keep intermediate Gemini image")

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
        # Step 1: Generate with Gemini for quality
        print(f"Step 1: Generating with {args.gemini_model}...", file=sys.stderr)
        gemini_images = client.generate_image(
            args.gemini_model,
            args.prompt,
            aspect_ratio=args.aspect,
            size=args.size
        )

        if not gemini_images:
            print("Error: No images generated by Gemini", file=sys.stderr)
            sys.exit(1)

        gemini_data_url = gemini_images[0]["image_url"]["url"]
        print("✓ Gemini generation complete", file=sys.stderr)

        # Save intermediate if requested
        if args.keep_intermediate:
            intermediate_path = output_path.parent / f"{output_path.stem}_gemini{output_path.suffix}"
            save_image(gemini_data_url, intermediate_path)
            print(f"  Saved intermediate: {intermediate_path}", file=sys.stderr)

        # Step 2: Convert to transparent with GPT-5 Image
        print("Step 2: Converting to transparent background with GPT-5 Image...", file=sys.stderr)
        transparent_images = client.convert_image_to_transparent(
            gemini_data_url,
            aspect_ratio=args.aspect,
            size=args.size
        )

        if not transparent_images:
            print("Error: No images generated by GPT-5 Image", file=sys.stderr)
            sys.exit(1)

        transparent_data_url = transparent_images[0]["image_url"]["url"]
        print("✓ Transparency conversion complete", file=sys.stderr)

        # Save final output
        save_image(transparent_data_url, output_path)
        print(f"✓ Saved final logo: {output_path}", file=sys.stderr)
        print(f"\nSuccess! High-quality transparent logo created at: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
