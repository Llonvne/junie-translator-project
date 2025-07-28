#!/usr/bin/env python3
"""
Test file for async translator functionality.
This file tests the async methods added to the translator.
"""

import asyncio
import unittest
import logging
from pathlib import Path

from junie_translator_project.translator import MockTranslator
from junie_translator_project.main import SRTTranslator, LockFile, Config
from junie_translator_project.srt_parser import SRTParser, SubtitleEntry

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TestAsyncTranslator(unittest.TestCase):
    """Test cases for async translator functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a mock translator for testing
        self.translator = MockTranslator()
        
        # Create a lock file in a temporary location
        self.lock_file = LockFile("test_lock_file.lock")
        
        # Create an SRT translator
        self.srt_translator = SRTTranslator(
            translator_service=self.translator,
            show_progress=False,
            lock_file=self.lock_file,
            from_language="auto",
            output_directory="./test_output"
        )
        
        # Create test directory if it doesn't exist
        Path("./test_output").mkdir(exist_ok=True)
        
        # Create a sample SRT entry
        self.sample_entry = SubtitleEntry(
            index=1,
            start_time="00:00:01,000",
            end_time="00:00:05,000",
            content=["Hello world", "This is a test"]
        )
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove lock file if it exists
        if Path("test_lock_file.lock").exists():
            Path("test_lock_file.lock").unlink()
    
    def test_sync_translate(self):
        """Test synchronous translation of a single text."""
        result = self.translator.translate("Hello", "Spanish")
        self.assertEqual(result, "[Spanish] Hello")
    
    def test_sync_batch_translate(self):
        """Test synchronous batch translation."""
        texts = ["Hello", "World"]
        results = self.translator.batch_translate(texts, "Spanish")
        self.assertEqual(results, ["[Spanish] Hello", "[Spanish] World"])
    
    async def async_test_translate(self):
        """Test asynchronous translation of a single text."""
        result = await self.translator.translate_async("Hello", "Spanish")
        self.assertEqual(result, "[Spanish] Hello")
    
    async def async_test_batch_translate(self):
        """Test asynchronous batch translation."""
        texts = ["Hello", "World"]
        results = await self.translator.batch_translate_async(texts, "Spanish")
        self.assertEqual(results, ["[Spanish] Hello", "[Spanish] World"])
    
    async def async_test_translate_entries(self):
        """Test asynchronous translation of subtitle entries."""
        entries = [self.sample_entry]
        results = await self.srt_translator._translate_entries_async(entries, "Spanish")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, ["[Spanish] Hello world", "[Spanish] This is a test"])
    
    def test_async_translate(self):
        """Run async test for translate_async."""
        asyncio.run(self.async_test_translate())
    
    def test_async_batch_translate(self):
        """Run async test for batch_translate_async."""
        asyncio.run(self.async_test_batch_translate())
    
    def test_async_translate_entries(self):
        """Run async test for _translate_entries_async."""
        asyncio.run(self.async_test_translate_entries())
    
    def test_github_secrets(self):
        """Test GitHub Secrets API key extraction."""
        from junie_translator_project.main import get_api_key_from_github_secrets
        
        # Test with no environment variables set
        self.assertIsNone(get_api_key_from_github_secrets("openai"))
        
        # Set a test environment variable
        import os
        os.environ["GITHUB_OPENAI_API_KEY"] = "test_key"
        
        # Test with environment variable set
        self.assertEqual(get_api_key_from_github_secrets("openai"), "test_key")
        
        # Clean up
        del os.environ["GITHUB_OPENAI_API_KEY"]

if __name__ == "__main__":
    unittest.main()