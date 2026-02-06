"""
Camera module for capturing images using OpenCV.
Provides live preview and frame capture functionality.
"""

import cv2
import os
from pathlib import Path


class CameraCapture:
    """Handles camera initialization, preview, and image capture."""
    
    def __init__(self, camera_id=0):
        """
        Initialize camera capture.
        
        Args:
            camera_id (int): Camera device ID (default: 0 for primary camera)
        """
        self.camera_id = camera_id
        self.cap = None
        self.frame_width = 1280
        self.frame_height = 720
        
    def initialize(self):
        """
        Initialize the camera device.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print("❌ ERROR: Cannot open camera. Check if camera is connected and not in use.")
                return False
            
            # Set camera resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            
            print("✓ Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ ERROR initializing camera: {e}")
            return False
    
    def capture_frame(self):
        """
        Capture a single frame from camera with live preview.
        
        Returns:
            ndarray: Captured frame or None if capture failed
        """
        if self.cap is None:
            print("❌ ERROR: Camera not initialized")
            return None
        
        try:
            print("\n" + "="*60)
            print("📷 CAMERA PREVIEW")
            print("="*60)
            print("Instructions:")
            print("  • Press SPACE to capture frame")
            print("  • Press Q or ESC to cancel")
            print("="*60 + "\n")
            
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("❌ ERROR: Failed to capture frame from camera")
                    return None
                
                # Add instructions overlay
                overlay_frame = frame.copy()
                cv2.putText(overlay_frame, "Press SPACE to capture | Q to cancel", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Document Scanner - Camera", overlay_frame)
                
                # Wait for key press (1 ms timeout)
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord(' '):  # Space to capture
                    cv2.destroyAllWindows()
                    print("✓ Frame captured successfully")
                    return frame
                    
                elif key == ord('q') or key == 27:  # Q or ESC to cancel
                    cv2.destroyAllWindows()
                    print("⊘ Camera capture cancelled by user")
                    return None
                    
        except Exception as e:
            print(f"❌ ERROR during frame capture: {e}")
            cv2.destroyAllWindows()
            return None
    
    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            print("✓ Camera released")
    
    def save_frame(self, frame, output_path="captured_image.png"):
        """
        Save captured frame to file.
        
        Args:
            frame (ndarray): Frame to save
            output_path (str): Path to save the frame
            
        Returns:
            str: Path to saved image or None if save failed
        """
        try:
            # Create directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            success = cv2.imwrite(output_path, frame)
            if success:
                print(f"✓ Frame saved to: {output_path}")
                return output_path
            else:
                print(f"❌ ERROR: Failed to save frame to {output_path}")
                return None
                
        except Exception as e:
            print(f"❌ ERROR saving frame: {e}")
            return None
