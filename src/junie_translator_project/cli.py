"""
Command-Line Interface Module - Provides a CLI for the translator program.

This module provides a command-line interface for translating SRT files
using the functionality provided by the main module.
Only config.json configuration is supported.

支持中文注释、日志和文档。
"""

import argparse
import sys
import logging
import colorlog
import re
from typing import List, Optional, Dict, Any

try:
    from tqdm.contrib.logging import logging_redirect_tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from junie_translator_project.main import main as config_main


class HttpxLogFilter(logging.Filter):
    """
    Filter to transform httpx logs into more meaningful information.
    
    This filter intercepts logs from the httpx library and transforms them
    to show more useful information about the translation process.
    """
    
    def __init__(self):
        super().__init__()
        self.current_file = ""
        self.current_line = 0
        self.subtitle_count = 0
        self.processed_count = 0
        self.http_request_pattern = re.compile(r'HTTP Request: (POST|GET) (https://[^ ]+) "([^"]+)"')
    
    def set_context(self, file: str, line: int, subtitle_count: int):
        """Set context information for the current translation."""
        self.current_file = file
        self.current_line = line
        self.subtitle_count = subtitle_count
        self.processed_count = 0
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and transform httpx logs.
        
        Args:
            record: The log record to filter
            
        Returns:
            True to include the record, False to exclude it
        """
        # Only process httpx logs
        if record.name == 'httpx':
            # Extract information from the log message
            match = self.http_request_pattern.search(record.msg)
            if match:
                method, url, status = match.groups()
                
                # Increment processed count for POST requests to translation APIs
                if method == 'POST' and ('chat/completions' in url or 'translations' in url):
                    self.processed_count += 1
                    
                    # Transform the log message to show more meaningful information
                    api_name = url.split('//')[1].split('.')[0].upper()
                    record.msg = f"API Call ({self.processed_count}/{self.subtitle_count}): {api_name} - File: {self.current_file}, Line: {self.current_line}"
                    
                    # Add custom attributes for coloring
                    record.api_call = True
                    return True
                    
                return False  # Filter out other httpx logs
        
        # Add custom attributes for coloring
        if 'translat' in record.msg.lower():
            record.translation = True
        elif 'file' in record.msg.lower():
            record.file_operation = True
            
        return True  # Include all other logs


# Define custom colors for different types of information
LOG_COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}

# Define secondary colors for different types of information
SECONDARY_LOG_COLORS = {
    'translation': {
        'DEBUG': 'blue',
        'INFO': 'blue,bold',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    'file_operation': {
        'DEBUG': 'cyan',
        'INFO': 'cyan,bold',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    'api_call': {
        'DEBUG': 'magenta',
        'INFO': 'magenta,bold',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
}


class EnhancedColoredFormatter(colorlog.ColoredFormatter):
    """
    Enhanced colored formatter that uses secondary colors based on log content.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with appropriate colors.
        
        Args:
            record: The log record to format
            
        Returns:
            The formatted log message
        """
        # Choose the appropriate color based on log content
        if hasattr(record, 'api_call') and record.api_call:
            color_key = 'api_call'
        elif hasattr(record, 'translation') and record.translation:
            color_key = 'translation'
        elif hasattr(record, 'file_operation') and record.file_operation:
            color_key = 'file_operation'
        else:
            color_key = None
            
        # Use secondary colors if available
        if color_key and record.levelname in SECONDARY_LOG_COLORS.get(color_key, {}):
            record.log_color = self.log_colors.get(
                SECONDARY_LOG_COLORS[color_key][record.levelname],
                self.log_colors.get(record.levelname)
            )
        
        return super().format(record)


# Create and configure the httpx log filter
httpx_filter = HttpxLogFilter()

# Configure colorful logging
handler = colorlog.StreamHandler()
handler.setFormatter(EnhancedColoredFormatter(
    '%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s%(reset)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=LOG_COLORS,
    secondary_log_colors=SECONDARY_LOG_COLORS,
    style='%'
))

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)
root_logger.addFilter(httpx_filter)

# Configure httpx logger
httpx_logger = logging.getLogger('httpx')
httpx_logger.propagate = True  # Ensure logs are processed by root logger

# Remove any default handlers
for h in root_logger.handlers[:]:
    if not isinstance(h, colorlog.StreamHandler):
        root_logger.removeHandler(h)

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
        
        # Use tqdm-compatible logging if available
        if TQDM_AVAILABLE:
            with logging_redirect_tqdm():
                return config_main(parsed_args.config)
        else:
            return config_main(parsed_args.config)
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())