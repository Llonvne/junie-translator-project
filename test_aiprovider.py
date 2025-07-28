#!/usr/bin/env python3
"""
Test script for the AIProviderTranslator class.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import the translator module
    from junie_translator_project.translator import (
        TranslatorFactory, AIProviderTranslator, MockTranslator
    )
    logger.info("Successfully imported translator module")
    
    # Test loading the aiprovider.json file
    from junie_translator_project.translator import load_aiprovider_config
    providers_config = load_aiprovider_config()
    logger.info(f"Loaded providers config: {list(providers_config.keys())}")
    
    # Test creating a MockTranslator
    mock_translator = MockTranslator()
    logger.info("Successfully created MockTranslator")
    
    # Test translating with MockTranslator
    text = "Hello, world!"
    target_language = "Spanish"
    translated_text = mock_translator.translate(text, target_language)
    logger.info(f"Mock translation: '{text}' -> '{translated_text}'")
    
    # Test creating an AIProviderTranslator with mock provider
    ai_translator = AIProviderTranslator(provider="mock")
    logger.info("Successfully created AIProviderTranslator with mock provider")
    
    # Test translating with AIProviderTranslator
    translated_text = ai_translator.translate(text, target_language)
    logger.info(f"AIProviderTranslator translation: '{text}' -> '{translated_text}'")
    
    # Test creating a translator using TranslatorFactory
    factory_translator = TranslatorFactory.create_translator(service_type="mock")
    logger.info("Successfully created translator using TranslatorFactory")
    
    # Test translating with factory-created translator
    translated_text = factory_translator.translate(text, target_language)
    logger.info(f"Factory-created translator translation: '{text}' -> '{translated_text}'")
    
    logger.info("All tests passed!")
    
except Exception as e:
    logger.error(f"Error during testing: {e}", exc_info=True)
    sys.exit(1)