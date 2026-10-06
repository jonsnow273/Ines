"""
Smart screen capture engine for Ines Digital Memory.
Performs fast screen capture, pixel difference evaluation (skips static screens),
image downscaling, and high-efficiency JPEG compression.
"""

import io
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageChops, ImageStat

from core import logger


class ScreenCaptureEngine:
    """Handles screen capture, change detection, and compressed storage."""

    def __init__(
        self,
        diff_threshold_percent: float = 5.0,
        max_width: int = 1280,
        jpeg_quality: int = 75,
    ):
        self.diff_threshold = diff_threshold_percent
        self.max_width = max_width
        self.jpeg_quality = jpeg_quality
        self.last_thumbnail: Optional[Image.Image] = None
        self._has_mss = self._check_mss()

    def _check_mss(self) -> bool:
        try:
            import mss
            return True
        except ImportError:
            return False

    def grab_raw_screen(self) -> Optional[Image.Image]:
        """Capture the primary display into a PIL Image."""
        try:
            if self._has_mss:
                import mss
                with mss.mss() as sct:
                    # Monitor 1 is the primary display
                    mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                    sct_img = sct.grab(mon)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    return img
            else:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                return img.convert("RGB")
        except Exception as e:
            logger.error(f"Screen grab failed: {e}")
            return None

    def calculate_diff_percent(self, current_img: Image.Image) -> float:
        """
        Compare current frame against previous frame using downsampled grayscale thumbnails.
        Returns a percentage difference (0.0 to 100.0).
        """
        # Downsample to 64x64 grayscale for ultra-fast difference check (<1ms)
        thumb = current_img.resize((64, 64), Image.Resampling.BILINEAR).convert("L")

        if self.last_thumbnail is None:
            self.last_thumbnail = thumb
            return 100.0  # First capture always counts as new

        diff = ImageChops.difference(self.last_thumbnail, thumb)
        stat = ImageStat.Stat(diff)
        # stat.mean[0] is in range 0 - 255
        diff_pct = (stat.mean[0] / 255.0) * 100.0

        # Update cached thumbnail only when change is acknowledged
        if diff_pct >= self.diff_threshold:
            self.last_thumbnail = thumb

        return round(diff_pct, 2)

    def optimize_image(self, img: Image.Image) -> Image.Image:
        """Downscale wide screens (4K/1440p) down to max_width to conserve storage."""
        width, height = img.size
        if width > self.max_width:
            new_height = int(height * (self.max_width / width))
            return img.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
        return img

    def capture_if_changed(
        self,
        output_dir: Path,
        force: bool = False,
    ) -> Tuple[Optional[Path], float, Dict[str, Any]]:
        """
        Captures the screen and saves it ONLY if significant pixel change is detected.
        Returns: (saved_path, diff_pct, metadata_dict)
        """
        img = self.grab_raw_screen()
        if img is None:
            return (None, 0.0, {"error": "Failed to grab screen"})

        diff_pct = self.calculate_diff_percent(img)

        # Skip if below threshold and not forced
        if not force and diff_pct < self.diff_threshold:
            return (None, diff_pct, {"skipped": True, "reason": "Change below threshold"})

        # Optimize and save
        optimized = self.optimize_image(img)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screen_{timestamp_str}.jpg"
        save_path = output_dir / filename

        # Avoid filename collisions in rapid captures
        counter = 1
        while save_path.exists():
            save_path = output_dir / f"screen_{timestamp_str}_{counter}.jpg"
            counter += 1

        optimized.save(save_path, "JPEG", quality=self.jpeg_quality, optimize=True)

        meta = {
            "timestamp": datetime.now().isoformat(),
            "dimensions": f"{optimized.width}x{optimized.height}",
            "diff_percent": diff_pct,
            "size_bytes": save_path.stat().st_size,
        }
        return (save_path, diff_pct, meta)
