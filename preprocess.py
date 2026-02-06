"""
Image Preprocessing Module
Converts raw camera/uploaded images to clean, readable documents.
Uses only light preprocessing: grayscale + adaptive threshold.
NO edge detection, NO contour detection - keeps it simple and safe.
"""

import cv2
import numpy as np


class ImagePreprocessor:
    """Handles safe, lightweight image preprocessing for OCR."""
    
    def __init__(self):
        """Initialize preprocessor with safe default parameters."""
        self.block_size = 11  # Neighborhood size for adaptive threshold (must be odd)
        self.constant = 2     # Constant subtracted in adaptive threshold
    
    def preprocess(self, image):
        """
        Preprocess image for OCR extraction.
        
        SAFE PIPELINE (light preprocessing):
        1. Convert to grayscale
        2. Apply adaptive thresholding only
        
        NO hard edge detection, NO document scanning,
        NO forced contour detection - just clean the image gently.
        
        Args:
            image (ndarray): Input image in BGR format from OpenCV
        
        Returns:
            ndarray: Preprocessed binary image ready for OCR
        """
        try:
            if image is None:
                print("❌ ERROR: Input image is None")
                return None
            
            # Step 1: Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("✓ Converted to grayscale")
            
            # Step 2: Apply adaptive thresholding
            # ADAPTIVE_THRESH_GAUSSIAN_C: uses Gaussian-weighted sum of neighborhood
            # This works well for documents with varying lighting
            processed = cv2.adaptiveThreshold(
                gray,
                255,                                  # Maximum value (white)
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,       # Adaptive method
                cv2.THRESH_BINARY,                    # Thresholding method
                blockSize=self.block_size,            # Neighborhood size (must be odd)
                C=self.constant                       # Constant subtracted
            )
            print("✓ Applied adaptive thresholding")
            
            return processed
            
        except Exception as e:
            print(f"❌ ERROR during preprocessing: {e}")
            print("⚠ Returning original grayscale image as fallback")
            try:
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            except:
                return None
    
    def save_processed_image(self, image, output_path):
        """
        Save preprocessed image to disk.
        
        Args:
            image (ndarray): Processed image to save
            output_path (str): Path where to save the image
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            if image is None:
                print("❌ ERROR: Cannot save - image is None")
                return False
            
            success = cv2.imwrite(output_path, image)
            if success:
                print(f"✓ Processed image saved: {output_path}")
                return True
            else:
                print(f"❌ ERROR: Failed to save image to {output_path}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR saving processed image: {e}")
            return False
    
    @staticmethod
    def get_image_info(image):
        """
        Get basic information about an image.
        
        Args:
            image (ndarray): Image to analyze
            
        Returns:
            dict: Image information (height, width, channels)
        """
        if image is None:
            return None
        
        if len(image.shape) == 2:  # Grayscale
            height, width = image.shape
            channels = 1
        else:
            height, width, channels = image.shape
        
        info = {
            "width": width,
            "height": height,
            "channels": channels,
            "size_bytes": image.nbytes
        }
        
        print(f"📐 Image Info: {width}x{height} pixels, {channels} channel(s)")
        return info
