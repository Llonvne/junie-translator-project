#!/usr/bin/env python3
"""
Example script demonstrating how to use the Junie Translator programmatically.
"""
import os
import sys

from junie_translator.factory import TranslatorFactory, ParserFactory
from junie_translator.translator import SubtitleTranslator


def main():
    """
    Example of using the Junie Translator programmatically.
    """
    # Check if the API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it to your OpenAI API key.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")
        return 1
    
    # Check if the input file exists
    input_file = "sample.srt"
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return 1
    
    # Create the translator
    translator = TranslatorFactory.create(
        "openai",
        api_key=api_key,
        model="gpt-3.5-turbo",
        max_retries=3,
        retry_delay=1.0
    )
    
    # Create the parser
    parser = ParserFactory.create_from_file(input_file)
    
    # Create the subtitle translator
    subtitle_translator = SubtitleTranslator(parser, translator)
    
    # Translate the file to Spanish
    target_language = "es"
    output_file = subtitle_translator.translate_file(
        input_file,
        target_language,
        output_file=None,  # Auto-generate the output file name
        delay=0.1
    )
    
    print(f"Translation completed successfully. Output file: {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())