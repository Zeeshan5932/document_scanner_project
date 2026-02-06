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
from parser_rule_based import RuleBasedParser
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
        self.rule_based_parser = RuleBasedParser()
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
        
        # Step 2: OCR Extraction
        print("\n[Step 2/7] 🔤 OCR Extraction...")
        print("-" * 40)
        
        ocr_data = self.ocr_extractor.extract_ocr_data(processed, mode="form")
        
        if not ocr_data.get("text") or len(ocr_data["text"]) == 0:
            print("❌ ERROR: No text detected in image")
            return False
        
        self.ocr_extractor.print_ocr_summary(ocr_data)
        
        # Step 3: Quality Check & Parser Selection
        print("\n[Step 3/7] 📊 Quality Check & Parser Selection...")
        print("-" * 40)
        
        avg_confidence = self.ocr_extractor.get_average_confidence(ocr_data)
        print(f"Average OCR confidence: {avg_confidence:.1f}%")
        
        # Check confidence threshold - REJECT LOW CONFIDENCE
        if avg_confidence < OCR_CONFIDENCE_THRESHOLD:
            print(f"\n❌ CONFIDENCE TOO LOW")
            print(f"   Current: {avg_confidence:.1f}%")
            print(f"   Required: >= {OCR_CONFIDENCE_THRESHOLD}%")
            print("\nPossible solutions:")
            print("  1. Re-scan with better lighting")
            print("  2. Use higher resolution image")
            print("  3. Position document more carefully")
            print("  4. Clean smudged or faded documents")
            
            retry = input("\nRetry scanning? (y/n): ").strip().lower()
            if retry == "y":
                print("⊘ Returning to input menu for re-scan...")
                return False  # Return to input selection
            else:
                print("⊘ Operation cancelled due to low confidence")
                return False
        
        # Confidence is good - use rule-based parser
        print(f"✓ Confidence {avg_confidence:.1f}% >= threshold {OCR_CONFIDENCE_THRESHOLD}%")
        print("  → Using rule-based parser")
        parser_type = "Rule-Based"
        
        # Step 4: Field Extraction
        print(f"\n[Step 4/7] 📋 Field Extraction ({parser_type})...")
        print("-" * 40)
        
        # Use rule-based parser (only option now)
        extracted_data = self.rule_based_parser.parse(ocr_data)
        
        if not extracted_data:
            print("⚠ WARNING: No fields extracted")
            proceed = input("Continue to review anyway? (y/n): ").strip().lower()
            if proceed != "y":
                print("⊘ Processing cancelled")
                return False
        else:
            self.rule_based_parser.print_extraction_summary(extracted_data)
        
        # Step 5: User Review (MANDATORY)
        print(f"\n[Step 5/7] 👀 User Review & Confirmation...")
        print("-" * 40)
        
        while True:
            # Display fields for review
            self.reviewer.display_fields_for_review(extracted_data, parser_type)
            
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
