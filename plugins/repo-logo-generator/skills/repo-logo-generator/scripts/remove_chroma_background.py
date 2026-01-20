#!/usr/bin/env python3
"""
Chroma Key Background Removal - Remove solid background using flood fill.

This script removes solid-colored backgrounds from images using OpenCV's flood fill
algorithm. Works with any solid background color by detecting and removing it from
the corners of the image.

Usage:
    uv run --with pillow --with opencv-python remove_chroma_background.py INPUT.png OUTPUT.png

    # With custom chroma color (magenta default)
    uv run --with pillow --with opencv-python remove_chroma_background.py INPUT.png OUTPUT.png \\
        --chroma-color 255 0 255 --tolerance 30

Dependencies: pillow, opencv-python
"""

import sys
import argparse
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
    import cv2
except ImportError as e:
    print(f"Error: Missing dependency - {e}", file=sys.stderr)
    print("Install with: pip install pillow opencv-python", file=sys.stderr)
    sys.exit(1)


def remove_chroma_background(image_path, output_path, chroma_color=None, tolerance=30):
    """
    Remove solid background using flood fill from corners.

    Args:
        image_path: Path to input image
        output_path: Path to save transparent PNG
        chroma_color: RGB tuple of expected background color (default: auto-detect from corners)
        tolerance: Color matching tolerance (default: 30)

    Returns:
        PIL.Image: RGBA image with transparency

    Raises:
        ValueError: If image cannot be loaded or no solid background detected
    """
    try:
        # Load image
        img_pil = Image.open(image_path).convert('RGB')
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise ValueError(f"Failed to load image: {e}")

    h, w = img.shape[:2]

    # Auto-detect chroma color from corners if not provided
    if chroma_color is None:
        # Sample all 4 corners
        corners = [
            img[0, 0],           # Top-left
            img[0, w-1],         # Top-right
            img[h-1, 0],         # Bottom-left
            img[h-1, w-1]        # Bottom-right
        ]

        # Check if corners are roughly the same color (solid background)
        corner_avg = np.mean(corners, axis=0)
        corner_std = np.std(corners, axis=0)

        if np.max(corner_std) > tolerance:
            raise ValueError(
                f"Corners have different colors (std: {corner_std}). "
                f"Cannot auto-detect solid background. Specify --chroma-color manually."
            )

        chroma_color = tuple(map(int, corner_avg))
        print(f"Auto-detected background color: RGB{chroma_color}", file=sys.stderr)

    # Convert chroma_color to BGR for OpenCV
    chroma_bgr = (chroma_color[2], chroma_color[1], chroma_color[0])

    # Create mask for flood fill (2px larger than image)
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Create working copy
    img_fill = img.copy()

    # Flood fill from all 4 corners
    # This ensures we catch the background even if it's not perfectly connected
    corners_to_fill = [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]

    for y, x in corners_to_fill:
        cv2.floodFill(
            img_fill,
            mask,
            (x, y),
            (0, 0, 0),  # Fill color (black, we only care about mask)
            loDiff=(tolerance, tolerance, tolerance),
            upDiff=(tolerance, tolerance, tolerance),
            flags=cv2.FLOODFILL_MASK_ONLY | (255 << 8)
        )

    # Extract the flood fill mask (remove 2px border)
    background_mask = mask[1:-1, 1:-1]

    # Invert to get foreground mask
    foreground_mask = 255 - background_mask

    # Convert original image to RGBA
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    rgba = np.dstack([img_rgb, foreground_mask])

    # Create PIL image
    result = Image.fromarray(rgba, mode='RGBA')

    # Save PNG with alpha channel
    result.save(output_path, 'PNG')
    print(f"✓ Created transparent PNG: {output_path}")

    return result


def validate_transparency(image_path, min_pct=5.0, min_corners=3, alpha_threshold=25):
    """
    Check if transparency meets quality criteria.

    Args:
        image_path: Path to PNG image to validate
        min_pct: Minimum percentage of transparent pixels (default: 5.0)
        min_corners: Minimum number of transparent corners (default: 3 out of 4)
        alpha_threshold: Alpha value below which pixel is considered transparent (default: 25)

    Returns:
        tuple: (bool, str) - (is_valid, message)
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        return False, f"Failed to load image: {e}"

    # 1. Must have alpha channel
    if img.mode != 'RGBA':
        return False, "No alpha channel found"

    # 2. Calculate transparent pixel percentage
    alpha = np.array(img.split()[3])
    transparent_pixels = np.sum(alpha < alpha_threshold)
    transparent_pct = (transparent_pixels / alpha.size) * 100

    if transparent_pct < min_pct:
        return False, f"Only {transparent_pct:.1f}% transparent (need {min_pct}%)"

    # 3. Check corner transparency (centered logo validation)
    h, w = alpha.shape
    corners = [
        alpha[0, 0],           # Top-left
        alpha[0, w-1],         # Top-right
        alpha[h-1, 0],         # Bottom-left
        alpha[h-1, w-1]        # Bottom-right
    ]
    corners_transparent = sum(1 for c in corners if c < alpha_threshold)

    if corners_transparent < min_corners:
        return False, f"Only {corners_transparent}/4 corners transparent (need {min_corners})"

    return True, f"Valid: {transparent_pct:.1f}% transparent, {corners_transparent}/4 corners clear"


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Remove solid background using chroma key flood fill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s logo.png output.png
  %(prog)s logo.png output.png --chroma-color 255 0 255 --tolerance 30
  %(prog)s logo.png output.png --skip-validation
        """
    )

    parser.add_argument('input', help='Path to input image')
    parser.add_argument('output', help='Path to save transparent PNG')
    parser.add_argument(
        '--chroma-color',
        type=int,
        nargs=3,
        metavar=('R', 'G', 'B'),
        default=None,
        help='Expected background RGB color (default: auto-detect from corners)'
    )
    parser.add_argument(
        '--tolerance',
        type=int,
        default=30,
        help='Color matching tolerance (default: 30)'
    )
    parser.add_argument(
        '--min-transparent-pct',
        type=float,
        default=5.0,
        help='Minimum percentage of transparent pixels for validation (default: 5.0)'
    )
    parser.add_argument(
        '--min-corners',
        type=int,
        default=3,
        help='Minimum number of transparent corners (default: 3)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip transparency validation after creation'
    )

    args = parser.parse_args()

    # Validate input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input image not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Convert chroma color to tuple if provided
    chroma_color = tuple(args.chroma_color) if args.chroma_color else None

    # Remove background
    try:
        result = remove_chroma_background(
            input_path,
            args.output,
            chroma_color=chroma_color,
            tolerance=args.tolerance
        )
    except Exception as e:
        print(f"Error removing background: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate transparency
    if not args.skip_validation:
        print("Validating transparency...", file=sys.stderr)
        is_valid, message = validate_transparency(
            args.output,
            min_pct=args.min_transparent_pct,
            min_corners=args.min_corners
        )

        if is_valid:
            print(f"✓ {message}", file=sys.stderr)
        else:
            print(f"✗ Validation failed: {message}", file=sys.stderr)
            sys.exit(1)

    print(f"Success! Transparent logo saved to: {args.output}")


if __name__ == '__main__':
    main()
