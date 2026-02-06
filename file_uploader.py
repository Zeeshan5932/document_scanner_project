"""
File uploader module for selecting images from disk.
Provides file dialog interface for image selection.
"""

import cv2
from tkinter import Tk, filedialog
from pathlib import Path


class FileUploader:
    """Handles file upload and image loading from disk."""
    
    SUPPORTED_FORMATS = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.gif")
    
    @staticmethod
    def upload_image():
        """
        Open file dialog to select an image and load it using OpenCV.
        
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
                title="Select Document Image",
                filetypes=[
                    ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                    ("All Files", "*.*")
                ]
            )
            
            root.destroy()
            
            if not file_path:
                print("⊘ No image selected - upload cancelled")
                return None, None
            
            # Check if file exists
            if not Path(file_path).exists():
                print(f"❌ ERROR: File not found: {file_path}")
                return None, None
            
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
