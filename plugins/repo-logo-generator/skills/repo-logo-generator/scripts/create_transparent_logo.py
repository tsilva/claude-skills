#!/usr/bin/env python3
"""
Difference Matting - Create transparent PNG from black and white background pairs.

This script uses the difference matting technique to extract perfect transparency
from two versions of the same logo rendered on black and white backgrounds.

Based on alpha compositing principles:
- white_img = foreground * alpha + 255 * (1 - alpha)
- black_img = foreground * alpha + 0 * (1 - alpha) = foreground * alpha

Solving for alpha and foreground:
- alpha = 1 - (white_img - black_img) / 255
- foreground = black_img / alpha (when alpha > threshold)

Usage:
    uv run --with pillow --with numpy create_transparent_logo.py BLACK.png WHITE.png OUTPUT.png

    # With custom validation thresholds
    uv run --with pillow --with numpy create_transparent_logo.py BLACK.png WHITE.png OUTPUT.png \\
        --min-transparent-pct 5.0 --min-corners 3 --alpha-threshold 0.01

Dependencies: pillow, numpy
"""

import sys
import argparse
from pathlib import Path
try:
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"Error: Missing dependency - {e}", file=sys.stderr)
    print("Install with: pip install pillow numpy", file=sys.stderr)
    sys.exit(1)


def create_transparent_logo(black_path, white_path, output_path, alpha_threshold=0.01):
    """
    Create transparent logo from black and white background versions.

    Args:
        black_path: Path to logo with black background
        white_path: Path to logo with white background
        output_path: Path to save transparent PNG
        alpha_threshold: Minimum alpha value to avoid division by zero (default: 0.01)

    Returns:
        PIL.Image: RGBA image with transparency

    Raises:
        AssertionError: If images have different dimensions
        ValueError: If images cannot be loaded
    """
    try:
        black = Image.open(black_path).convert('RGB')
        white = Image.open(white_path).convert('RGB')
    except Exception as e:
        raise ValueError(f"Failed to load images: {e}")

    # Ensure same dimensions
    if black.size != white.size:
        raise AssertionError(
            f"Images must have same dimensions. "
            f"Black: {black.size}, White: {white.size}"
        )

    # Convert to numpy arrays for vectorized operations
    black_arr = np.array(black, dtype=np.float32)
    white_arr = np.array(white, dtype=np.float32)

    # Calculate alpha channel from difference
    # alpha = 1 - |white - black| / 255
    # Use max of RGB channels for alpha (most conservative estimate)
    diff = np.abs(white_arr - black_arr)
    alpha = 1.0 - (np.max(diff, axis=2) / 255.0)

    # Extract foreground color from black background image
    # foreground = black / alpha (avoid division by very small alpha)
    foreground = np.zeros_like(black_arr)
    for c in range(3):  # RGB channels
        mask = alpha > alpha_threshold
        foreground[:, :, c] = np.where(
            mask,
            np.clip(black_arr[:, :, c] / np.maximum(alpha, alpha_threshold), 0, 255),
            black_arr[:, :, c]  # For nearly transparent pixels, use black background value
        )

    # Create RGBA image
    rgba = np.dstack([foreground, alpha * 255]).astype(np.uint8)
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


def check_similarity(black_path, white_path, threshold=0.90):
    """
    Check if two logos have similar composition (structure alignment).

    Uses structural similarity on grayscale versions to verify the logos
    are identical except for background color.

    Args:
        black_path: Path to logo with black background
        white_path: Path to logo with white background
        threshold: Minimum similarity score (0-1, default: 0.90)

    Returns:
        tuple: (bool, float) - (is_similar, similarity_score)
    """
    try:
        # Try to use scikit-image SSIM if available
        from skimage.metrics import structural_similarity as ssim

        black = Image.open(black_path).convert('L')  # Grayscale
        white = Image.open(white_path).convert('L')

        black_arr = np.array(black)
        white_arr = np.array(white)

        similarity = ssim(black_arr, white_arr)
        is_similar = similarity >= threshold

        return is_similar, similarity

    except ImportError:
        # Fallback: Use simple pixel difference if scikit-image not available
        print("Warning: scikit-image not available, using simple similarity check", file=sys.stderr)

        black = Image.open(black_path).convert('L')
        white = Image.open(white_path).convert('L')

        black_arr = np.array(black, dtype=np.float32)
        white_arr = np.array(white, dtype=np.float32)

        # Calculate normalized difference (inverted to be similarity)
        diff = np.abs(black_arr - white_arr)
        mean_diff = np.mean(diff) / 255.0
        similarity = 1.0 - mean_diff

        is_similar = similarity >= threshold
        return is_similar, similarity


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create transparent PNG from black and white background pairs using difference matting.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s logo_black.png logo_white.png output.png
  %(prog)s logo_black.png logo_white.png output.png --min-transparent-pct 10 --min-corners 4
  %(prog)s logo_black.png logo_white.png output.png --check-similarity
        """
    )

    parser.add_argument('black_bg', help='Path to logo with black background')
    parser.add_argument('white_bg', help='Path to logo with white background')
    parser.add_argument('output', help='Path to save transparent PNG')
    parser.add_argument(
        '--alpha-threshold',
        type=float,
        default=0.01,
        help='Minimum alpha value to avoid division by zero (default: 0.01)'
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
        '--check-similarity',
        action='store_true',
        help='Check if input images have similar composition before processing'
    )
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.90,
        help='Minimum similarity score for composition check (default: 0.90)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip transparency validation after creation'
    )

    args = parser.parse_args()

    # Validate input files exist
    black_path = Path(args.black_bg)
    white_path = Path(args.white_bg)

    if not black_path.exists():
        print(f"Error: Black background image not found: {black_path}", file=sys.stderr)
        sys.exit(1)

    if not white_path.exists():
        print(f"Error: White background image not found: {white_path}", file=sys.stderr)
        sys.exit(1)

    # Optional similarity check
    if args.check_similarity:
        print("Checking image similarity...", file=sys.stderr)
        is_similar, similarity = check_similarity(
            black_path,
            white_path,
            threshold=args.similarity_threshold
        )
        print(f"Similarity score: {similarity:.3f}", file=sys.stderr)

        if not is_similar:
            print(
                f"Warning: Images may have different compositions (similarity: {similarity:.3f})",
                file=sys.stderr
            )
            print("This may result in poor transparency extraction.", file=sys.stderr)

    # Create transparent logo
    try:
        result = create_transparent_logo(
            black_path,
            white_path,
            args.output,
            alpha_threshold=args.alpha_threshold
        )
    except Exception as e:
        print(f"Error creating transparent logo: {e}", file=sys.stderr)
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
