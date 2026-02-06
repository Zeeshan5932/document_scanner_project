"""
Complete Document Scanner System - Test Suite
Verifies that all modules import correctly and system is functional
"""

import sys
import traceback
import os

# Handle Windows console encoding issues
if sys.platform == "win32":
    os.system("chcp 65001 > nul")  # Set UTF-8 mode on Windows


def test_imports():
    """Test all module imports"""
    print("=" * 80)
    print("🔧 TESTING MODULE IMPORTS")
    print("=" * 80)

    modules = [
        ("preprocess", "ImagePreprocessor"),
        ("ocr", "OCRExtractor"),
        ("parser_rule_based", "RuleBasedParser"),
        ("review", "FieldReviewer"),
        ("saver", "DataSaver"),
        ("camera", "CameraCapture"),
        ("file_uploader", "FileUploader"),
    ]

    failed = []

    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                print(f"✓ {module_name:20} → {class_name}")
            else:
                print(f"❌ {module_name:20} → {class_name} NOT FOUND")
                failed.append(f"{module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name:20} → IMPORT ERROR: {str(e)}")
            failed.append(module_name)

    print("=" * 80)

    if failed:
        print(f"\n❌ {len(failed)} import(s) failed:")
        for item in failed:
            print(f"   • {item}")
        return False
    else:
        print("\n✓ All imports successful!")
        return True


def test_ocr_extractor():
    """Test OCR extractor initialization"""
    print("\n" + "=" * 80)
    print("🔧 TESTING OCR EXTRACTOR (PaddleOCR)")
    print("=" * 80)

    try:
        from ocr import OCRExtractor

        print("📥 Initializing OCRExtractor...")
        ocr = OCRExtractor()
        print(f"✓ OCRExtractor initialized successfully")
        print(f"  - Engine: PaddleOCR")
        print(f"  - Language: English")
        print(f"  - Angle detection: Enabled")
        print("=" * 80)
        return True
    except Exception as e:
        print(f"❌ OCRExtractor test failed: {str(e)}")
        traceback.print_exc()
        print("=" * 80)
        return False


def test_parser():
    """Test rule-based field parser initialization"""
    print("\n" + "=" * 80)
    print("🔧 TESTING RULE-BASED FIELD PARSER")
    print("=" * 80)

    try:
        from parser_rule_based import RuleBasedParser

        parser = RuleBasedParser()
        print(f"✓ RuleBasedParser initialized")
        print(f"  - Fields defined: {len(parser.FIELD_LABELS)}")
        print(f"  - Position threshold: {parser.position_threshold}px")
        print(f"  - Minimum horizontal gap: {parser.min_horizontal_gap}px")

        for field, keywords in list(parser.FIELD_LABELS.items())[:3]:
            print(f"    • {field}: {keywords}")

        print("=" * 80)
        return True
    except Exception as e:
        print(f"❌ RuleBasedParser test failed: {str(e)}")
        traceback.print_exc()
        print("=" * 80)
        return False


def test_saver():
    """Test data saver initialization"""
    print("\n" + "=" * 80)
    print("🔧 TESTING DATA SAVER")
    print("=" * 80)

    try:
        from saver import DataSaver
        from pathlib import Path

        saver = DataSaver("output")
        print(f"✓ DataSaver initialized")
        print(f"  - Output directory: {saver.output_dir}")
        print(f"  - Output dir exists: {saver.output_dir.exists()}")
        print(f"  - Timestamp: {saver.timestamp}")

        print("=" * 80)
        return True
    except Exception as e:
        print(f"❌ DataSaver test failed: {str(e)}")
        traceback.print_exc()
        print("=" * 80)
        return False


def test_preprocessor():
    """Test image preprocessor initialization"""
    print("\n" + "=" * 80)
    print("🔧 TESTING IMAGE PREPROCESSOR")
    print("=" * 80)

    try:
        from preprocess import ImagePreprocessor

        preprocessor = ImagePreprocessor()
        print(f"✓ ImagePreprocessor initialized")
        print(f"  - Block size: {preprocessor.block_size}")
        print(f"  - Constant: {preprocessor.constant}")

        print("=" * 80)
        return True
    except Exception as e:
        print(f"❌ ImagePreprocessor test failed: {str(e)}")
        traceback.print_exc()
        print("=" * 80)
        return False


def run_all_tests():
    """Run all tests"""
    print("\n\n")
    print("=" * 80)
    print(" COMPLETE DOCUMENT SCANNER SYSTEM - TEST SUITE ".center(80))
    print("=" * 80)

    tests = [
        ("Module Imports", test_imports),
        ("Image Preprocessor", test_preprocessor),
        ("OCR Extractor", test_ocr_extractor),
        ("Field Parser", test_parser),
        ("Data Saver", test_saver),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {str(e)}")
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")

    print("=" * 80)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED - SYSTEM IS READY! ✓✓✓")
        print("\nRun: python main.py")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
