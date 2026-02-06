"""
Configuration Module
System-wide settings for Document Scanner.
"""

import os
from pathlib import Path


# ===== QUALITY & CONFIDENCE THRESHOLDS =====
OCR_CONFIDENCE_THRESHOLD = 60      # If average OCR confidence < 60%, ask user to re-scan
                                    # Only rule-based parser is used with high-quality OCR

# ===== PREPROCESSING PARAMETERS =====
ADAPTIVE_THRESHOLD_BLOCK_SIZE = 11  # Must be odd number
ADAPTIVE_THRESHOLD_CONSTANT = 2

# ===== POSITIONING THRESHOLDS =====
POSITION_THRESHOLD = 15             # Pixels - same line if within this
MIN_HORIZONTAL_GAP = 120            # Min gap between label and value
