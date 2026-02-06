"""
File uploader module for selecting images and PDFs from disk.
Provides file dialog interface for image/PDF selection with PDF-to-image conversion.
"""

import cv2
import numpy as np
from tkinter import Tk, filedialog
from pathlib import Path

try:
    from pdf2image import convert_from_path
    _HAS_PDF2IMAGE = True
except ImportError:
    _HAS_PDF2IMAGE = False


class FileUploader:
    """Handles file upload and image loading from disk (supports JPG, PNG, PDF, etc.)."""
    
    SUPPORTED_FORMATS = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.gif", "*.pdf")
    
    @staticmethod
    def upload_image():
        """
        Open file dialog to select an image or PDF and load it.
        
        Returns:
            tuple: (frame, file_path) where frame is the loaded image array
                   or (None, None) if upload was cancelled or failed
        """
        try:
            # Create and hide Tkinter root window
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            
            file_path = filedialog.askopenfilename(
                title="Select Document Image or PDF",
                filetypes=[
                    ("All Supported", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.pdf"),
                    ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                    ("PDF Files", "*.pdf"),
                    ("All Files", "*.*")
                ]
            )
            
            root.destroy()
            
            if not file_path:
                print("⊘ No file selected - upload cancelled")
                return None, None
            
            # Check if file exists
            if not Path(file_path).exists():
                print(f"❌ ERROR: File not found: {file_path}")
                return None, None
            
            # Handle PDF files
            if file_path.lower().endswith('.pdf'):
                return FileUploader._load_pdf(file_path)
            
            # Load image
            image = cv2.imread(file_path)
            
            if image is None:
                print(f"❌ ERROR: Failed to load image - unsupported format or corrupted file")
                print(f"   File: {file_path}")
                return None, None
            
            print(f"✓ Image loaded successfully: {file_path}")
            print(f"  Dimensions: {image.shape[1]} x {image.shape[0]} pixels")
            return image, file_path
            
        except Exception as e:
            print(f"❌ ERROR during file upload: {e}")
            return None, None
    
    @staticmethod
    def _load_pdf(file_path):
        """
        Convert PDF to image and load first page.
        
        Args:
            file_path (str): Path to PDF file
            
        Returns:
            tuple: (image, file_path) or (None, None) if failed
        """
        if not _HAS_PDF2IMAGE:
            print("❌ ERROR: pdf2image not installed")
            print("   Install with: pip install pdf2image")
            print("   Note: Also requires poppler-utils")
            return None, None
        
        try:
            print(f"📄 Converting PDF to image: {file_path}")
            
            # Convert only first page
            images = convert_from_path(file_path, first_page=1, last_page=1, dpi=300)
            
            if not images:
                print("❌ ERROR: PDF conversion failed - empty result")
                return None, None
            
            # Get first page as PIL image
            pil_image = images[0]
            
            # Convert PIL image to OpenCV format (BGR)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            print(f"✓ PDF loaded successfully: {file_path}")
            print(f"  Dimensions: {image.shape[1]} x {image.shape[0]} pixels (300 DPI)")
            return image, file_path
            
        except Exception as e:
            print(f"❌ ERROR during PDF conversion: {e}")
            print("   Make sure poppler is installed:")
            print("   - Windows: pip install python-poppler")
            print("   - Linux: sudo apt-get install poppler-utils")
            print("   - macOS: brew install poppler")
            return None, None
    
    @staticmethod
    def validate_image(frame):
        """
        Validate that an image frame is valid.
        
        Args:
            frame (ndarray): Image frame to validate
            
        Returns:
            bool: True if frame is valid, False otherwise
        """
        if frame is None:
            return False
        
        if not hasattr(frame, 'shape') or len(frame.shape) < 2:
            return False
        
        if frame.size == 0:
            return False
        
        return True
