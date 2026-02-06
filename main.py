"""
Document Scanner - Main Orchestrator
Implements complete end-to-end pipeline:

1. INPUT: Capture (camera) or Upload (file)
2. PREPROCESS: Grayscale + Adaptive threshold
3. OCR: Extract text with positions and confidence
4. QUALITY CHECK: Average OCR confidence
5. CONFIDENCE VALIDATION:
   - If confidence >= 60% → Proceed to extraction
   - If confidence < 60% → ASK USER TO RE-SCAN (NO OpenAI fallback)
6. PARSER: Rule-based parser (position + content validation)
7. USER REVIEW: Show results, allow edits, prevent blind saving
8. OUTPUT FORMAT: Excel, JSON, or CSV
9. SAVE: Write file with timestamp

Usage:
    python main.py
"""

import sys
from pathlib import Path
from config import OCR_CONFIDENCE_THRESHOLD

from camera import CameraCapture
from file_uploader import FileUploader
from preprocess import ImagePreprocessor
from ocr import OCRExtractor
from roi_based_parser import ROIBasedParser  # NEW: ROI-based extraction (more accurate)
from review import FieldReviewer
from saver import DataSaver


class DocumentScannerPipeline:
    """Main orchestrator for document scanning pipeline."""
    
    def __init__(self):
        """Initialize all pipeline components."""
        print("\n" + "="*80)
        print("🖼️  DOCUMENT SCANNER SYSTEM - Complete Pipeline")
        print("="*80)
        print()
        
        # Initialize output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.camera = None
        self.preprocessor = ImagePreprocessor()
        self.ocr_extractor = OCRExtractor()
        self.roi_parser = ROIBasedParser(ocr_extractor=self.ocr_extractor)  # NEW: ROI-based parser
        self.reviewer = FieldReviewer()
        self.saver = DataSaver(str(self.output_dir))
    
    def show_input_menu(self) -> str:
        """
        Show input method menu and get user choice.
        
        Returns:
            str: 'camera', 'upload', or None if cancelled
        """
        print("\n" + "="*80)
        print("📸 INPUT METHOD")
        print("="*80)
        print("\nOptions:")
        print("  [1] Capture from camera (live preview)")
        print("  [2] Upload image from PC (file dialog)")
        print("  [3] Exit")
        print()
        
        while True:
            choice = input("Enter choice (1/2/3): ").strip()
            
            if choice == "1":
                print("✓ Selected: Camera capture")
                return "camera"
            elif choice == "2":
                print("✓ Selected: File upload")
                return "upload"
            elif choice == "3":
                print("👋 Exiting...")
                return None
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3")
    
    def capture_from_camera(self):
        """
        Capture image from camera.
        
        Returns:
            ndarray: Captured frame or None if cancelled
        """
        print("\n" + "-"*80)
        
        self.camera = CameraCapture(camera_id=0)
        
        if not self.camera.initialize():
            print("❌ ERROR: Could not initialize camera")
            return None
        
        frame = self.camera.capture_frame()
        self.camera.release()
        
        return frame
    
    def upload_from_file(self):
        """
        Upload image from file dialog.
        
        Returns:
            ndarray: Loaded image or None if cancelled
        """
        print("\n" + "-"*80)
        
        frame, file_path = FileUploader.upload_image()
        
        if frame is None:
            return None
        
        return frame
    
    def run_complete_pipeline(self, frame) -> bool:
        """
        Execute complete scanning pipeline.
        
        Pipeline steps:
        1. Preprocessing (grayscale + adaptive threshold)
        2. OCR extraction (text + positions + confidence)
        3. Quality check (calculate average confidence)
        4. Parser selection (rule-based vs OpenAI)
        5. User review (mandatory confirmation)
        6. Output selection (Excel, JSON, CSV)
        7. Save (with timestamp)
        
        Args:
            frame (ndarray): Input image
        
        Returns:
            bool: True if successful, False if cancelled
        """
        print("\n" + "="*80)
        print("🔄 PROCESSING PIPELINE")
        print("="*80)
        
        # Step 1: Preprocessing
        print("\n[Step 1/7] 🛠️  Image Preprocessing...")
        print("-" * 40)
        
        processed = self.preprocessor.preprocess(frame)
        
        if processed is None:
            print("❌ ERROR: Preprocessing failed")
            return False
        
        print("✓ Image preprocessed successfully")
        
        # IMPROVED: Skip full-image OCR, use ROI-based extraction instead
        # WHY: Each field extracted from fixed position → no shifting, better accuracy
        
        # Step 2: ROI-Based Field Extraction (NEW - replaces full-image OCR)
        print("\n[Step 2/7] 📍 ROI-Based Field Extraction...")
        print("-" * 40)
        print("Extracting fields using Region of Interest approach...")
        
        # Use ROI-based parser on the ORIGINAL image (not preprocessed)
        # WHY: ROI parser does its own preprocessing per field
        extracted_data = self.roi_parser.parse_form(frame, self.ocr_extractor)
        
        if not extracted_data:
            print("❌ ERROR: No fields could be extracted")
            return False
        
        # Step 3: Quality Check & Summary
        print("\n[Step 3/7] 📊 Quality Summary...")
        print("-" * 40)
        
        # Calculate average confidence from extracted fields
        confidences = [
            d.get("confidence", 0)
            for d in extracted_data.values()
            if d.get("confidence", 0) > 0
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        print(f"Average extraction confidence: {avg_confidence:.1f}%")
        
        # Check for fields that need review
        fields_need_review = [
            f for f, d in extracted_data.items()
            if d.get("require_review", False)
        ]
        
        if fields_need_review:
            print(f"⚠️  {len(fields_need_review)} field(s) need review: {', '.join(fields_need_review)}")
        
        # Step 4: Final data preparation
        print(f"\n[Step 4/7] ✓ Field Extraction Complete")
        print("-" * 40)
        
        # Convert to format expected by reviewer
        # (reviewer expects {"field": {"value": "...", "confidence": ...}})
        formatted_data = {}
        for field_name, field_info in extracted_data.items():
            formatted_data[field_name] = {
                "value": field_info.get("value", ""),
                "confidence": field_info.get("confidence", 0),
            }
        
        extracted_data = formatted_data
        
        # Step 5: User Review (MANDATORY)
        print(f"\n[Step 5/7] 👀 User Review & Confirmation...")
        print("-" * 40)
        
        while True:
            # Display fields for review
            self.reviewer.display_fields_for_review(extracted_data, "ROI-Based")
            
            # Get user action
            user_choice = self.reviewer.get_user_confirmation()
            
            if user_choice == "accept":
                print("✓ Data confirmed - proceeding to save")
                break
            elif user_choice == "edit":
                # User wants to edit
                extracted_data = self.reviewer.get_field_edits(extracted_data)
                print("✓ Fields updated - showing updated data...")
                continue
            elif user_choice == "cancel":
                print("⊘ Operation cancelled by user - starting over")
                return False
        
        # Step 6: Output Format Selection
        print(f"\n[Step 6/7] 📁 Output Format Selection...")
        print("-" * 40)
        
        output_format = self.reviewer.get_output_format()
        
        if output_format is None:
            print("⊘ Save cancelled by user")
            return False
        
        # Get filename
        filename = self.reviewer.get_output_filename("scanned_document")
        
        # Step 7: Save
        print(f"\n[Step 7/7] 💾 Saving Data...")
        print("-" * 40)
        
        # Show final summary
        self.reviewer.print_final_summary(extracted_data, output_format, filename)
        
        # Save data
        success = self.saver.save(extracted_data, filename, output_format)
        
        if success:
            print("\n✓✓✓ Data saved successfully! ✓✓✓")
            self.saver.list_output_files()
            return True
        else:
            print("\n❌ Failed to save data")
            return False
    
    def run(self):
        """Main application loop."""
        try:
            while True:
                # Get input method
                input_method = self.show_input_menu()
                
                if input_method is None:
                    break
                
                # Capture or upload image
                print()
                if input_method == "camera":
                    frame = self.capture_from_camera()
                else:  # upload
                    frame = self.upload_from_file()
                
                if frame is None:
                    print("\n⚠ No image obtained - please try again")
                    continue
                
                # Run complete pipeline
                success = self.run_complete_pipeline(frame)
                
                if success:
                    # Ask if user wants to scan another document
                    print("\n")
                    another = input("Scan another document? (y/n): ").strip().lower()
                    if another != "y":
                        print("\n" + "="*80)
                        print("👋 Thank you for using Document Scanner!")
                        print("="*80)
                        break
        
        except KeyboardInterrupt:
            print("\n\n❌ Application interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Entry point - Start the document scanner."""
    pipeline = DocumentScannerPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
