#!/usr/bin/env python3
"""
Example script demonstrating how to use the Junie Translator Project.

This script shows both basic and advanced usage of the translator program.
It includes examples of:
- Basic translation with default settings
- Advanced translation with custom settings
- Using the mock translator for testing
- Extending the translator with a custom translator service

To run this example, you need:
1. An SRT file to translate (example.srt)
2. An OpenAI API key (or use the mock translator)

Usage:
    python translate_example.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path if running the script directly
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from junie_translator_project.main import translate_srt, SRTTranslator
from junie_translator_project.translator import TranslatorService, TranslatorFactory
from typing import List


def create_example_srt():
    """Create a simple example SRT file for demonstration purposes."""
    example_content = """1
00:00:01,000 --> 00:00:04,000
Hello, welcome to this video.

2
00:00:05,000 --> 00:00:09,000
Today we're going to learn about translation.

3
00:00:10,000 --> 00:00:15,000
Translation is the process of converting text
from one language to another.
"""
    
    example_path = Path(script_dir) / "example.srt"
    with open(example_path, "w", encoding="utf-8") as f:
        f.write(example_content)
    
    return example_path


def basic_translation_example(srt_path):
    """Demonstrate basic translation with default settings."""
    print("\n=== Basic Translation Example ===")
    
    # Check if we have an API key or should use mock translator
    api_key = os.environ.get("OPENAI_API_KEY")
    translator_type = "openai" if api_key else "mock"
    
    if translator_type == "mock":
        print("No OpenAI API key found. Using mock translator.")
    
    # Translate the file
    output_path = translate_srt(
        input_path=str(srt_path),
        target_language="Spanish",
        translator_type=translator_type,
        api_key=api_key
    )
    
    print(f"Translation completed. Output file: {output_path}")
    
    # Print the first few lines of the translated file
    print("\nFirst few lines of the translated file:")
    with open(output_path, "r", encoding="utf-8") as f:
        print(f.read(200) + "...")


def advanced_translation_example(srt_path):
    """Demonstrate advanced translation with custom settings."""
    print("\n=== Advanced Translation Example ===")
    
    # Create a translator service with custom settings
    translator = TranslatorFactory.create_translator(
        service_type="mock",  # Using mock for demonstration
        api_key="dummy-key",
        model="gpt-4"
    )
    
    # Create an SRT translator with the custom translator service
    srt_translator = SRTTranslator(
        translator_service=translator,
        show_progress=True
    )
    
    # Translate the file
    output_path = srt_translator.translate_file(
        input_path=str(srt_path),
        target_language="French",
        output_path=str(Path(srt_path).with_name("custom_output_french.srt"))
    )
    
    print(f"Translation completed. Output file: {output_path}")


def custom_translator_example(srt_path):
    """Demonstrate extending the translator with a custom translator service."""
    print("\n=== Custom Translator Example ===")
    
    # Define a custom translator service
    class ReverseTranslator(TranslatorService):
        """A silly translator that reverses the text."""
        
        def translate(self, text: str, target_language: str) -> str:
            """Reverse the text as a 'translation'."""
            return f"[{target_language} Reversed] {text[::-1]}"
        
        def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
            """Reverse each text in the batch."""
            return [self.translate(text, target_language) for text in texts]
    
    # Create an SRT translator with the custom translator service
    custom_translator = ReverseTranslator()
    srt_translator = SRTTranslator(
        translator_service=custom_translator,
        show_progress=True
    )
    
    # Translate the file
    output_path = srt_translator.translate_file(
        input_path=str(srt_path),
        target_language="Reverse",
        output_path=str(Path(srt_path).with_name("custom_output_reverse.srt"))
    )
    
    print(f"Translation completed. Output file: {output_path}")
    
    # Print the first few lines of the translated file
    print("\nFirst few lines of the translated file:")
    with open(output_path, "r", encoding="utf-8") as f:
        print(f.read(200) + "...")


def main():
    """Run the example script."""
    print("Junie Translator Project - Example Script")
    
    # Create an example SRT file
    srt_path = create_example_srt()
    print(f"Created example SRT file: {srt_path}")
    
    # Run the examples
    basic_translation_example(srt_path)
    advanced_translation_example(srt_path)
    custom_translator_example(srt_path)
    
    print("\nAll examples completed successfully!")


if __name__ == "__main__":
    main()