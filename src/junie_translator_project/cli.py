"""
Command-Line Interface Module - Provides a CLI for the translator program.

This module provides a command-line interface for translating SRT files
using the functionality provided by the main module.
Only config.json configuration is supported.
"""

import argparse
import sys
import logging
from typing import List, Optional

from junie_translator_project.main import main as config_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


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
        "-c", "--config",
        default="config.json",
        help="Path to the configuration file (default: config.json)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
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
        
        # Set logging level based on verbose flag
        if parsed_args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Verbose logging enabled")
        
        logger.info(f"Using configuration file: {parsed_args.config}")
        return config_main(parsed_args.config)
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())