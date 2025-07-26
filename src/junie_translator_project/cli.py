"""
Command-Line Interface Module - Provides a CLI for the translator program.

This module provides a command-line interface for translating SRT files
using the functionality provided by the main module.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from junie_translator_project.main import translate_srt


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments (if None, sys.argv[1:] will be used)
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Translate SRT subtitle files using AI services.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the input SRT file"
    )
    
    parser.add_argument(
        "target_language",
        help="Target language code or name (e.g., 'Spanish', 'fr', 'German')"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Path to the output SRT file (if not provided, will be generated)"
    )
    
    parser.add_argument(
        "-t", "--translator",
        default="auto",
        choices=["auto", "openai", "deepseek", "mock"],
        help="Translator service to use ('auto' will detect based on available API keys)"
    )
    
    parser.add_argument(
        "-k", "--api-key",
        help="API key for the translator service (if not provided, will try to get from environment)"
    )
    
    parser.add_argument(
        "-m", "--model",
        help="Model to use for translation (defaults to gpt-3.5-turbo for OpenAI, deepseek-v3 for DeepSeek)"
    )
    
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (if None, sys.argv[1:] will be used)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        parsed_args = parse_args(args)
        
        # Check if input file exists
        if not os.path.exists(parsed_args.input_file):
            print(f"Error: Input file not found: {parsed_args.input_file}", file=sys.stderr)
            return 1
        
        # Get API key from environment if not provided
        api_key = parsed_args.api_key
        
        # For explicit service types, check for the appropriate API key
        if not api_key:
            if parsed_args.translator == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    print(
                        "Error: OpenAI API key is required. "
                        "Either provide it with --api-key or set the OPENAI_API_KEY environment variable.",
                        file=sys.stderr
                    )
                    return 1
            elif parsed_args.translator == "deepseek":
                api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not api_key:
                    print(
                        "Error: DeepSeek API key is required. "
                        "Either provide it with --api-key or set the DEEPSEEK_API_KEY environment variable.",
                        file=sys.stderr
                    )
                    return 1
            # For auto mode, the TranslatorFactory will handle API key detection
        
        # Translate the file
        output_path = translate_srt(
            input_path=parsed_args.input_file,
            target_language=parsed_args.target_language,
            output_path=parsed_args.output,
            translator_type=parsed_args.translator,
            api_key=api_key,
            model=parsed_args.model,
            show_progress=not parsed_args.no_progress
        )
        
        print(f"Translation completed successfully. Output file: {output_path}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())