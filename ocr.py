"""
OCR Extraction Module
Uses EasyOCR for superior text detection including handwritten text.
EasyOCR Features:
- Excellent at both printed AND handwritten text
- Pure Python, no external binaries needed
- Returns text with confidence scores and bounding boxes
- Multi-language support
- High accuracy for mixed document types
"""

import numpy as np

try:
    import easyocr
    _HAS_EASYOCR = True
except Exception:
    _HAS_EASYOCR = False


class OCRExtractor:
    """Extracts text with positional and confidence data using EasyOCR."""

    def __init__(self):
        """Initialize OCR extractor with EasyOCR."""
        if not _HAS_EASYOCR:
            print("❌ easyocr not installed. Run: pip install easyocr")
            raise ImportError("easyocr is required")

        print("🔤 Initializing EasyOCR (may download model on first run)...")
        # Initialize reader for English language
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("✓ EasyOCR initialized successfully")

    def extract_ocr_data(self, preprocessed_image, mode="form"):
        """
        Extract text with positional and confidence data using EasyOCR.

        EasyOCR is superior for:
        - Handwritten text recognition
        - Mixed printed/handwritten documents
        - Text at various angles
        - Low-quality scans

        Args:
            preprocessed_image (ndarray): Preprocessed image from preprocess.py
            mode (str): Ignored for EasyOCR (kept for API compatibility)

        Returns:
            dict: OCR data dictionary with keys:
                - text: list of extracted words
                - left: list of x-coordinates (bounding box top-left)
                - top: list of y-coordinates (bounding box top-left)
                - width: list of bounding box widths
                - height: list of bounding box heights
                - confidence: list of confidence scores (0-100)
                - raw_data: raw EasyOCR output
        """
        try:
            if preprocessed_image is None:
                print("❌ ERROR: Preprocessed image is None")
                return self._empty_ocr_data()

            print("🔤 Extracting text with EasyOCR...")

            # Run EasyOCR detection
            # Returns list of [bbox, text, confidence]
            # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] (4 corners)
            results = self.reader.readtext(preprocessed_image)

            if not results:
                print("❌ No text detected in image")
                return self._empty_ocr_data()

            # Process results - extract text, positions, and confidence
            processed_data = {
                "text": [],
                "left": [],
                "top": [],
                "width": [],
                "height": [],
                "confidence": [],
            }

            # Sort by position (top-to-bottom, left-to-right) for consistency
            all_detections = []
            for bbox, text, conf in results:
                # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                xs = [point[0] for point in bbox]
                ys = [point[1] for point in bbox]

                x_min = int(min(xs))
                y_min = int(min(ys))
                x_max = int(max(xs))
                y_max = int(max(ys))

                width = x_max - x_min
                height = y_max - y_min

                # Convert confidence from 0-1 scale to 0-100%
                confidence = int(conf * 100)

                # Store detection info
                all_detections.append({
                    "text": text.strip(),
                    "left": x_min,
                    "top": y_min,
                    "width": width,
                    "height": height,
                    "confidence": confidence,
                })

            # Sort by position (top-to-bottom, left-to-right)
            all_detections.sort(key=lambda x: (x["top"], x["left"]))

            # Filter out low-confidence or empty detections
            for detection in all_detections:
                if detection["confidence"] > 0 and detection["text"]:
                    processed_data["text"].append(detection["text"])
                    processed_data["left"].append(detection["left"])
                    processed_data["top"].append(detection["top"])
                    processed_data["width"].append(detection["width"])
                    processed_data["height"].append(detection["height"])
                    processed_data["confidence"].append(detection["confidence"])

            processed_data["raw_data"] = results

            print(f"✓ OCR extraction complete: {len(processed_data['text'])} words detected")
            return processed_data

        except Exception as e:
            print(f"❌ ERROR during OCR extraction: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_ocr_data()

    def extract_plain_text(self, preprocessed_image, mode="form"):
        """
        Extract plain text without positional data.

        Args:
            preprocessed_image (ndarray): Preprocessed image
            mode (str): Ignored for EasyOCR

        Returns:
            str: Extracted text
        """
        try:
            ocr_data = self.extract_ocr_data(preprocessed_image, mode)
            text = " ".join(ocr_data.get("text", []))
            return text.strip()

        except Exception as e:
            print(f"❌ ERROR during text extraction: {e}")
            return ""

    @staticmethod
    def get_average_confidence(ocr_data):
        """
        Calculate average OCR confidence.

        Args:
            ocr_data (dict): OCR data dictionary

        Returns:
            float: Average confidence (0-100) or 0 if no data
        """
        if not ocr_data.get("confidence") or len(ocr_data["confidence"]) == 0:
            return 0

        return float(np.mean(ocr_data["confidence"]))

    @staticmethod
    def print_ocr_summary(ocr_data):
        """
        Print OCR extraction summary.

        Args:
            ocr_data (dict): OCR data dictionary
        """
        avg_conf = OCRExtractor.get_average_confidence(ocr_data)
        word_count = len(ocr_data["text"])
        preview_text = " ".join(ocr_data["text"][:5])

        print("\n" + "="*60)
        print("🔤 OCR EXTRACTION SUMMARY")
        print("="*60)
        print(f"Words detected:      {word_count}")
        print(f"Average confidence:  {avg_conf:.1f}%")
        print(f"Text preview:        {preview_text}...")
        print("="*60)

    @staticmethod
    def _empty_ocr_data():
        """Return empty OCR data structure."""
        return {
            "text": [],
            "left": [],
            "top": [],
            "width": [],
            "height": [],
            "confidence": [],
            "raw_data": None,
        }

