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

from junie_translator_project.main import translate_srt, translate_directory, main as config_main


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
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    
    # Config mode - use configuration file
    config_parser = subparsers.add_parser(
        "config", 
        help="Use configuration file to translate all SRT files in current directory"
    )
    config_parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to the configuration file (default: config.json)"
    )
    
    # File mode - translate a single file
    file_parser = subparsers.add_parser(
        "file", 
        help="Translate a single SRT file"
    )
    file_parser.add_argument(
        "input_file",
        help="Path to the input SRT file"
    )
    file_parser.add_argument(
        "target_language",
        help="Target language code or name (e.g., 'Spanish', 'fr', 'German')"
    )
    file_parser.add_argument(
        "-o", "--output",
        help="Path to the output SRT file (if not provided, will be generated)"
    )
    file_parser.add_argument(
        "-f", "--from-language",
        default="auto",
        help="Source language code or name (default: auto-detect)"
    )
    file_parser.add_argument(
        "-t", "--translator",
        default="auto",
        choices=["auto", "openai", "deepseek", "mock"],
        help="Translator service to use ('auto' will detect based on available API keys)"
    )
    file_parser.add_argument(
        "-k", "--api-key",
        help="API key for the translator service (if not provided, will try to get from environment)"
    )
    file_parser.add_argument(
        "-m", "--model",
        help="Model to use for translation (defaults to gpt-3.5-turbo for OpenAI, deepseek-v3 for DeepSeek)"
    )
    file_parser.add_argument(
        "-d", "--output-dir",
        help="Directory for output files"
    )
    file_parser.add_argument(
        "-l", "--lock-file",
        default="junie-translator.lock",
        help="Path to the lock file (default: junie-translator.lock)"
    )
    file_parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )
    
    # Directory mode - translate all files in a directory
    dir_parser = subparsers.add_parser(
        "dir", 
        help="Translate all SRT files in a directory"
    )
    dir_parser.add_argument(
        "directory",
        help="Path to the directory containing SRT files"
    )
    dir_parser.add_argument(
        "target_language",
        help="Target language code or name (e.g., 'Spanish', 'fr', 'German')"
    )
    dir_parser.add_argument(
        "-p", "--pattern",
        default="*.srt",
        help="File pattern to match SRT files (default: *.srt)"
    )
    dir_parser.add_argument(
        "-f", "--from-language",
        default="auto",
        help="Source language code or name (default: auto-detect)"
    )
    dir_parser.add_argument(
        "-t", "--translator",
        default="auto",
        choices=["auto", "openai", "deepseek", "mock"],
        help="Translator service to use ('auto' will detect based on available API keys)"
    )
    dir_parser.add_argument(
        "-k", "--api-key",
        help="API key for the translator service (if not provided, will try to get from environment)"
    )
    dir_parser.add_argument(
        "-m", "--model",
        help="Model to use for translation (defaults to gpt-3.5-turbo for OpenAI, deepseek-v3 for DeepSeek)"
    )
    dir_parser.add_argument(
        "-d", "--output-dir",
        help="Directory for output files"
    )
    dir_parser.add_argument(
        "-l", "--lock-file",
        default="junie-translator.lock",
        help="Path to the lock file (default: junie-translator.lock)"
    )
    dir_parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )
    
    # If no arguments are provided, default to config mode
    if len(sys.argv) == 1:
        return parser.parse_args(["config"])
    
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
        
        # Config mode - use configuration file
        if parsed_args.mode == "config":
            return config_main(parsed_args.config)
            
        # File mode - translate a single file
        elif parsed_args.mode == "file":
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
                show_progress=not parsed_args.no_progress,
                from_language=parsed_args.from_language,
                output_directory=parsed_args.output_dir,
                lock_file_path=parsed_args.lock_file
            )
            
            print(f"Translation completed successfully. Output file: {output_path}")
            return 0
            
        # Directory mode - translate all files in a directory
        elif parsed_args.mode == "dir":
            # Check if directory exists
            if not os.path.isdir(parsed_args.directory):
                print(f"Error: Directory not found: {parsed_args.directory}", file=sys.stderr)
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
            
            # Translate all files in the directory
            output_files = translate_directory(
                directory_path=parsed_args.directory,
                target_language=parsed_args.target_language,
                translator_type=parsed_args.translator,
                api_key=api_key,
                model=parsed_args.model,
                show_progress=not parsed_args.no_progress,
                from_language=parsed_args.from_language,
                output_directory=parsed_args.output_dir,
                lock_file_path=parsed_args.lock_file,
                file_pattern=parsed_args.pattern
            )
            
            if output_files:
                print(f"Translation completed successfully. {len(output_files)} files translated:")
                for output_file in output_files:
                    print(f"  - {output_file}")
                return 0
            else:
                print("No files were translated.")
                return 1
        
        else:
            print("Error: No operation mode specified. Use 'config', 'file', or 'dir'.", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())