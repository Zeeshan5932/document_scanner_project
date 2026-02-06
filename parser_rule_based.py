"""
Rule-Based Parser Module
Uses label + position logic to extract structured data from OCR results.
For fixed/semi-fixed forms with printed labels.

STRATEGY:
- Printed labels (e.g., "Student Name", "Contact") appear on the LEFT
- Actual values appear to the RIGHT of labels
- Uses spatial positioning + content validation
- NEVER extracts labels as values
- Validates data type (names are alphabetic, phones are digits, etc.)
"""

import re
from typing import Dict, List, Tuple


class RuleBasedParser:
    """Extracts form data using label+position based rules."""
    
    # Define common form field labels and their variations
    FIELD_LABELS = {
        "Student Name": ["student", "name", "student name", "full name"],
        "Father Name": ["father", "father name", "father's name"],
        "Mother Name": ["mother", "mother name", "mother's name"],
        "Home Address": ["address", "home", "home address", "postal address"],
        "School": ["school", "institution", "college"],
        "Contact": ["contact", "phone", "mobile", "number", "telephone"],
        "Email": ["email", "e-mail", "email address"],
        "Date": ["date", "dob", "birth"],
        "Roll Number": ["roll", "enrollment", "roll number", "id"],
        "Marks": ["marks", "score", "points", "percentage"],
        "Group": ["group", "class", "section"],
        "City": ["city", "town"],
        "Province": ["province", "state", "district"],
    }
    
    def __init__(self):
        """Initialize parser with threshold parameters."""
        # Build set of all label keywords for quick filtering
        self.all_label_keywords = set()
        for keywords in self.FIELD_LABELS.values():
            for keyword in keywords:
                self.all_label_keywords.add(keyword.lower())
        
        # Positioning thresholds
        self.position_threshold = 15      # pixels - same line if within this
        self.min_horizontal_gap = 120     # Minimum gap between label and value
        self.confidence_threshold = 0     # Minimum OCR confidence
    
    def parse(self, ocr_data: Dict) -> Dict:
        """
        Parse OCR data into structured fields using rule-based approach.
        
        Args:
            ocr_data (dict): OCR data with keys: text, left, top, width, height, confidence
        
        Returns:
            dict: Extracted fields with structure:
                {
                    "Field Name": {
                        "value": "extracted_value",
                        "confidence": 85
                    }
                }
        """
        if not ocr_data.get("text") or len(ocr_data["text"]) == 0:
            print("⚠ WARNING: No OCR text to parse")
            return {}
        
        print("📋 Starting rule-based parsing...")
        extracted_fields = {}
        
        # For each field, try to find label + value pair
        for field_name, label_keywords in self.FIELD_LABELS.items():
            field_data = self._find_field_value(
                field_name,
                label_keywords,
                ocr_data
            )
            
            if field_data is not None:
                extracted_fields[field_name] = field_data
        
        print(f"✓ Rule-based parsing complete: {len(extracted_fields)} fields extracted")
        return extracted_fields
    
    def _find_field_value(self, field_name: str, label_keywords: List[str], 
                          ocr_data: Dict) -> Dict:
        """
        Find label and its corresponding value.
        
        Args:
            field_name (str): Name of field to extract
            label_keywords (list): Possible label keywords
            ocr_data (dict): OCR data
        
        Returns:
            dict: {"value": ..., "confidence": ...} or None
        """
        # Find label index
        label_index = self._find_label(label_keywords, ocr_data)
        
        if label_index is None:
            return None
        
        # Get label position and dimensions
        label_left = ocr_data["left"][label_index]
        label_top = ocr_data["top"][label_index]
        label_right = label_left + ocr_data["width"][label_index]
        
        # Find value to the right of the label
        value_text = None
        value_confidence = 0
        
        for i, text in enumerate(ocr_data["text"]):
            # Skip the label itself
            if i == label_index:
                continue
            
            # Check if on same line (within position_threshold)
            word_top = ocr_data["top"][i]
            if abs(word_top - label_top) > self.position_threshold:
                continue
            
            # Check if to the right of label with minimum gap
            word_left = ocr_data["left"][i]
            if word_left < (label_right + self.min_horizontal_gap):
                continue
            
            # Skip if word is a label keyword (ends with colon, or is a label)
            if self._is_label_text(text):
                continue
            
            # Validate value based on field type
            if self._validate_value(text, field_name):
                value_text = text
                value_confidence = ocr_data["confidence"][i]
                break
        
        if value_text is None:
            return None
        
        return {
            "value": value_text,
            "confidence": value_confidence
        }
    
    def _find_label(self, label_keywords: List[str], ocr_data: Dict) -> int:
        """
        Find the index of label text in OCR data.
        
        Args:
            label_keywords (list): Possible label keywords
            ocr_data (dict): OCR data
        
        Returns:
            int: Index of label or None
        """
        for i, text in enumerate(ocr_data["text"]):
            text_lower = text.lower()
            
            # Check if any label keyword matches
            for keyword in label_keywords:
                if keyword in text_lower:
                    # Ensure it's actually a label (high position or ends with colon)
                    if self._is_label_text(text):
                        return i
        
        return None
    
    def _is_label_text(self, text: str) -> bool:
        """
        Check if text is likely a label (not a value).
        
        Labels usually:
        - End with colon (:)
        - Are from the label keyword set
        - Are relatively short
        
        Args:
            text (str): Text to check
        
        Returns:
            bool: True if text looks like a label
        """
        # Ends with colon
        if text.endswith(":"):
            return True
        
        # In label keywords set
        if text.lower() in self.all_label_keywords:
            return True
        
        # Short text with mostly uppercase (likely label)
        if len(text) < 15 and text.isupper():
            return True
        
        return False
    
    def _validate_value(self, text: str, field_type: str) -> bool:
        """
        Validate extracted value based on field type.
        
        Args:
            text (str): Text to validate
            field_type (str): Type of field (e.g., "Student Name", "Contact")
        
        Returns:
            bool: True if value is valid
        """
        # Skip empty or whitespace-only text
        if not text or not text.strip():
            return False
        
        # Skip very short text (likely noise)
        if len(text.strip()) < 2:
            return False
        
        # Name fields - should be mostly alphabetic
        if "Name" in field_type:
            # Allow letters, spaces, hyphens, apostrophes
            if not re.search(r'^[a-zA-Z\s\-\']+$', text):
                return False
            return len(text) > 2
        
        # Phone/Contact fields - should be mostly digits
        if any(x in field_type.lower() for x in ["contact", "phone", "mobile", "number"]):
            # Allow digits, spaces, hyphens, parentheses, +
            if not re.search(r'^[0-9\s\-\+\(\)]+$', text):
                return False
            return len(re.findall(r'\d', text)) >= 7  # At least 7 digits
        
        # Email fields
        if "Email" in field_type:
            if '@' not in text or '.' not in text:
                return False
            return True
        
        # Date fields
        if "Date" in field_type or "Birth" in field_type:
            # Should contain digits and separators
            if not re.search(r'\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}', text):
                return False
            return True
        
        # Marks/Score fields - should be numeric or percentage
        if "Marks" in field_type or "Score" in field_type or "Percentage" in field_type:
            # Allow digits, decimal point, percentage sign
            if not re.search(r'^[\d\.%\s]+$', text):
                return False
            return len(re.findall(r'\d', text)) >= 1
        
        # Address, City, School, etc. - accept as is if not empty
        if any(x in field_type for x in ["Address", "City", "School", "Group"]):
            return len(text.strip()) > 1
        
        # For unknown types, accept if not all digits or all special chars
        if text and any(c.isalnum() for c in text):
            return True
        
        return False
    
    def print_extraction_summary(self, extracted_data: Dict):
        """Print summary of extracted fields."""
        print("\n" + "="*60)
        print("📋 RULE-BASED EXTRACTION SUMMARY")
        print("="*60)
        
        if not extracted_data:
            print("No fields extracted")
        else:
            for field, data in extracted_data.items():
                conf = data.get("confidence", 0)
                value = data.get("value", "")
                print(f"{field:20} -> {value:30} (confidence: {conf}%)")
        
        print("="*60)
