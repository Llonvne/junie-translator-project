#!/usr/bin/env python3
"""
Test script for the Junie Translator Project.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from junie_translator_project.main import Config, LockFile, SRTTranslator, translate_srt

def test_config():
    """Test loading configuration from config.json."""
    try:
        config = Config("config.json")
        print(f"Configuration loaded successfully:")
        print(f"  From language: {config.get_from_language()}")
        print(f"  To language: {config.get_to_language()}")
        print(f"  API service: {config.get_api_service_provider()}")
        print(f"  Output directory: {config.get_output_directory()}")
        return True
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False

def test_translation():
    """Test translating a sample SRT file."""
    try:
        output_path = translate_srt(
            input_path="sample.srt",
            target_language="Spanish",
            translator_type="mock",
            from_language="auto",
            output_directory="./output"
        )
        print(f"Translation completed successfully.")
        print(f"Output file: {output_path}")
        return True
    except Exception as e:
        print(f"Error translating file: {e}")
        return False

def test_lock_file():
    """Test the lock file mechanism."""
    try:
        # Create a lock file
        lock_file = LockFile("test.lock")
        
        # Generate a file ID
        file_id = LockFile.generate_file_id("sample.srt", "auto", "Spanish")
        
        # Mark the file as processed
        lock_file.mark_processed(file_id)
        
        # Check if the file is marked as processed
        is_processed = lock_file.is_processed(file_id)
        print(f"Lock file test: {'Passed' if is_processed else 'Failed'}")
        
        # Clean up
        os.remove("test.lock")
        return is_processed
    except Exception as e:
        print(f"Error testing lock file: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Testing Junie Translator Project ===")
    
    # Test configuration
    print("\n--- Testing Configuration ---")
    config_result = test_config()
    
    # Test translation
    print("\n--- Testing Translation ---")
    translation_result = test_translation()
    
    # Test lock file
    print("\n--- Testing Lock File ---")
    lock_file_result = test_lock_file()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Configuration: {'Passed' if config_result else 'Failed'}")
    print(f"Translation: {'Passed' if translation_result else 'Failed'}")
    print(f"Lock File: {'Passed' if lock_file_result else 'Failed'}")
    
    # Return exit code
    return 0 if all([config_result, translation_result, lock_file_result]) else 1

if __name__ == "__main__":
    sys.exit(main())