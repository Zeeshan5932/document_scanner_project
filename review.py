"""
Review Module
Mandatory user review and correction interface.
Shows extracted fields with confidence, allows edits, prevents blind auto-saving.
"""

from typing import Dict, Optional
from datetime import datetime


class FieldReviewer:
    """Interactive review of extracted data with validation and correction."""
    
    @staticmethod
    def display_fields_for_review(extracted_data: Dict, parser_type: str = "Unknown") -> None:
        """
        Display extracted fields in user-friendly format.
        
        Args:
            extracted_data (dict): Extracted fields with values and confidence
            parser_type (str): Type of parser used ("Rule-Based" or "OpenAI")
        """
        print("\n" + "="*80)
        print("👀 PLEASE REVIEW THE EXTRACTED DATA")
        print("="*80)
        print(f"Parser used: {parser_type}")
        print()
        
        if not extracted_data:
            print("❌ No fields were extracted from the document")
            print("="*80)
            return
        
        # Sort fields by name for consistent display
        sorted_fields = sorted(extracted_data.items())
        
        for idx, (field_name, field_data) in enumerate(sorted_fields, 1):
            value = field_data.get("value", "")
            confidence = field_data.get("confidence", 0)
            
            # Visual indicator for confidence level
            if confidence >= 80:
                confidence_indicator = "✓✓ HIGH"
                marker = "✓"
            elif confidence >= 60:
                confidence_indicator = "✓ MEDIUM"
                marker = "⚠"
            else:
                confidence_indicator = "⚠ LOW"
                marker = "⚠"
            
            print(f"{marker} {idx}. {field_name}")
            print(f"   Value:      {value}")
            print(f"   Confidence: {confidence}% ({confidence_indicator})")
            print()
        
        print("="*80)
    
    @staticmethod
    def get_user_confirmation() -> str:
        """
        Ask user to accept, edit, or cancel.
        NEVER auto-save - always require explicit user action.
        
        Returns:
            str: 'accept', 'edit', or 'cancel'
        """
        while True:
            print("\nOptions:")
            print("  [A] Accept - Use extracted data as-is")
            print("  [E] Edit   - Modify specific fields")
            print("  [C] Cancel - Discard and start over")
            print()
            
            choice = input("Your choice (A/E/C): ").strip().upper()
            
            if choice == "A":
                print("✓ Confirmed - proceeding with data")
                return "accept"
            elif choice == "E":
                print("✓ Edit mode - select fields to modify")
                return "edit"
            elif choice == "C":
                print("⊘ Cancelled - discarding data")
                return "cancel"
            else:
                print("❌ Invalid choice. Please enter A, E, or C")
    
    @staticmethod
    def get_field_edits(extracted_data: Dict) -> Dict:
        """
        Allow user to edit specific fields interactively.
        
        Args:
            extracted_data (dict): Current extracted fields
        
        Returns:
            dict: Updated fields (with manually edited fields marked as 100% confidence)
        """
        updated_data = extracted_data.copy()
        
        while True:
            print("\n" + "-"*80)
            print("EDIT MODE - Select fields to modify")
            print("-"*80)
            
            # Display current fields with numbers
            sorted_fields = sorted(updated_data.items())
            for idx, (field_name, field_data) in enumerate(sorted_fields, 1):
                value = field_data.get("value", "")
                conf = field_data.get("confidence", 0)
                print(f"{idx}. {field_name}: {value} (confidence: {conf}%)")
            
            print(f"{len(sorted_fields) + 1}. Done editing")
            print()
            
            try:
                choice = input("Enter field number to edit (or Enter 'Done'): ").strip()
                
                if choice.lower() == "done" or choice == str(len(sorted_fields) + 1):
                    print("✓ Done editing")
                    break
                
                field_idx = int(choice) - 1
                if 0 <= field_idx < len(sorted_fields):
                    field_name = sorted_fields[field_idx][0]
                    
                    print(f"\nEditing: {field_name}")
                    current_value = updated_data[field_name].get("value", "")
                    print(f"Current value: {current_value}")
                    
                    new_value = input("Enter new value (or press Enter to skip): ").strip()
                    
                    if new_value:
                        updated_data[field_name]["value"] = new_value
                        # Mark manually edited fields with 100% confidence
                        updated_data[field_name]["confidence"] = 100
                        print(f"✓ Updated '{field_name}' to '{new_value}'")
                    else:
                        print("⊘ Skipped (no change)")
                else:
                    print("❌ Invalid field number")
                    
            except ValueError:
                print("❌ Please enter a valid number")
                continue
        
        return updated_data
    
    @staticmethod
    def get_output_format() -> Optional[str]:
        """
        Ask user to select output format.
        
        Returns:
            str: 'excel', 'json', 'csv', or None if cancelled
        """
        print("\n" + "="*80)
        print("📁 SELECT OUTPUT FORMAT")
        print("="*80)
        print("\nAvailable formats:")
        print("  [1] Excel (.xlsx) - Best for spreadsheet viewing")
        print("  [2] JSON (.json)  - Best for data interchange")
        print("  [3] CSV (.csv)    - Best for data analysis")
        print("  [0] Cancel - Don't save")
        print()
        
        while True:
            choice = input("Enter format number (1/2/3/0): ").strip()
            
            if choice == "1":
                print("✓ Selected: Excel format (.xlsx)")
                return "excel"
            elif choice == "2":
                print("✓ Selected: JSON format (.json)")
                return "json"
            elif choice == "3":
                print("✓ Selected: CSV format (.csv)")
                return "csv"
            elif choice == "0":
                print("⊘ Save cancelled")
                return None
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 0")
    
    @staticmethod
    def get_output_filename(default_name: str = "scanned_form") -> str:
        """
        Ask user for custom filename.
        
        Args:
            default_name (str): Default filename without extension
        
        Returns:
            str: Filename (without extension - will be added by saver)
        """
        print(f"\nDefault filename: {default_name}")
        custom_name = input("Enter custom filename (or press Enter for default): ").strip()
        
        if custom_name:
            # Remove any file extension if provided
            custom_name = custom_name.replace(".xlsx", "").replace(".json", "").replace(".csv", "")
            custom_name = custom_name.strip()
            if custom_name:
                return custom_name
        
        return default_name
    
    @staticmethod
    def print_final_summary(extracted_data: Dict, output_format: str, filename: str) -> None:
        """
        Print final summary before saving.
        This is the last confirmation point.
        
        Args:
            extracted_data (dict): Fields to be saved
            output_format (str): Output format selected
            filename (str): Output filename
        """
        print("\n" + "="*80)
        print("✓ FINAL SUMMARY - READY TO SAVE")
        print("="*80)
        print()
        
        print(f"Output Format:      {output_format.upper()}")
        print(f"Filename:           {filename}.{_get_extension(output_format)}")
        print(f"Fields to save:     {len(extracted_data)}")
        
        # Calculate average confidence
        if extracted_data:
            total_confidence = sum(f.get("confidence", 0) for f in extracted_data.values())
            avg_confidence = total_confidence / len(extracted_data)
            print(f"Average Confidence: {avg_confidence:.1f}%")
        
        print(f"Timestamp:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("="*80)


def _get_extension(format_type: str) -> str:
    """Get file extension for format."""
    extensions = {
        "excel": "xlsx",
        "json": "json",
        "csv": "csv"
    }
    return extensions.get(format_type.lower(), "txt")
