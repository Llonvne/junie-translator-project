"""
Command-line interface for the translator program.
"""
import argparse
import os
import sys
from typing import List, Optional

from junie_translator.factory import TranslatorFactory, ParserFactory
from junie_translator.translator import SubtitleTranslator


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments. If None, sys.argv[1:] will be used.
        
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Translate subtitle files using AI services.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="The subtitle file to translate."
    )
    
    parser.add_argument(
        "target_language",
        help="The language code to translate to (e.g., 'es' for Spanish, 'fr' for French)."
    )
    
    parser.add_argument(
        "-o", "--output-file",
        help="The path to write the translated subtitle file to. "
             "If not provided, a default name will be generated."
    )
    
    parser.add_argument(
        "-t", "--translator",
        default="openai",
        choices=list(TranslatorFactory._translators.keys()),
        help="The translator service to use."
    )
    
    parser.add_argument(
        "-k", "--api-key",
        help="The API key for the translator service. "
             "If not provided, it will be read from the environment."
    )
    
    parser.add_argument(
        "-m", "--model",
        default="gpt-3.5-turbo",
        help="The model to use for translation (for OpenAI)."
    )
    
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=0.1,
        help="The delay between translation requests in seconds."
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="The maximum number of retries for failed translation requests."
    )
    
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=1.0,
        help="The initial delay between retries in seconds."
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the translator program.
    
    Args:
        args: Command-line arguments. If None, sys.argv[1:] will be used.
        
    Returns:
        The exit code.
    """
    try:
        # Parse command-line arguments
        parsed_args = parse_args(args)
        
        # Check if the input file exists
        if not os.path.exists(parsed_args.input_file):
            print(f"Error: Input file not found: {parsed_args.input_file}", file=sys.stderr)
            return 1
        
        # Create the translator
        translator = TranslatorFactory.create(
            parsed_args.translator,
            api_key=parsed_args.api_key,
            model=parsed_args.model,
            max_retries=parsed_args.max_retries,
            retry_delay=parsed_args.retry_delay
        )
        
        # Create the parser
        parser = ParserFactory.create_from_file(parsed_args.input_file)
        
        # Create the subtitle translator
        subtitle_translator = SubtitleTranslator(parser, translator)
        
        # Translate the file
        output_file = subtitle_translator.translate_file(
            parsed_args.input_file,
            parsed_args.target_language,
            output_file=parsed_args.output_file,
            delay=parsed_args.delay
        )
        
        print(f"Translation completed successfully. Output file: {output_file}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())