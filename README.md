# Junie Translator Project

A Python program for translating SRT subtitle files using AI services like OpenAI.

## Features

- Translate SRT subtitle files to any language using AI services
- Process one line at a time for accurate translations
- Display a progress bar showing translation progress
- Output well-named SRT files with source language, target language, and file hash in the filename
- Extensible architecture that supports different translation services
- Configuration file support for easy setup and reuse
- Lock file mechanism to avoid duplicate translations
- Batch processing of multiple SRT files in a directory
- Source language auto-detection or manual specification
- Asynchronous processing for improved performance with multiple files and entries
- Detailed runtime logging for better debugging
- GitHub Actions support for automatic testing with API keys from GitHub Secrets
- **Colorful, human-readable logs** for better readability and debugging
- **Chinese support** in comments, logs, and documentation
- **Customizable AI prompts** via prompts.json for different translation styles
- **JSON schema** for configuration validation and documentation

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for package management. Make sure you have uv installed before proceeding.

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/junie-translator-project.git
cd junie-translator-project

# Install the package
uv pip install .
```

### Install with development dependencies

```bash
uv pip install ".[dev]"
```

## Usage

### Command Line Interface

The package installs a command-line tool called `srt-translate` that uses a configuration file to translate SRT files.

```bash
# Use default config.json in current directory
srt-translate

# Specify a custom config file
srt-translate -c my-config.json

# Enable verbose logging
srt-translate -v
```

### Configuration File

You can use a configuration file to store your settings. The default file name is `config.json` in the current directory. Here's an example:

```json
{
  "from-language": "auto",
  "to-language": "Spanish",
  "ai-api-service": {
    "api-service-provider": "openai",
    "api-key": "your-api-key-here"
  },
  "output-directory": "./output",
  "model": "gpt-3.5-turbo",
  "prompt-style": "subtitle"
}
```

#### JSON Schema

A JSON schema is provided in `config.schema.json` to validate your configuration and provide documentation for all available options. You can use tools like Visual Studio Code with JSON schema support to get auto-completion and validation while editing your config file.

To associate the schema with your config file in VS Code, add this line at the top of your `config.json`:

```json
{
  "$schema": "./config.schema.json",
  "from-language": "auto",
  "to-language": "Spanish"
}
```

### Customizable AI Prompts

The translator supports customizable AI prompts through a `prompts.json` file in the project root. This allows you to define different translation styles and even support different languages for the prompts themselves.

Here's an example of the `prompts.json` structure:

```json
{
  "default": {
    "system": "You are a professional translator. Translate the text accurately while preserving the original meaning, tone, and formatting.",
    "user": "Translate the following text to {target_language}. Preserve any formatting and special characters:\n\n{text}"
  },
  "chinese": {
    "system": "你是一位专业翻译。请准确翻译文本，同时保留原始含义、语气和格式。",
    "user": "请将以下文本翻译成{target_language}。保留任何格式和特殊字符：\n\n{text}"
  },
  "subtitle": {
    "system": "You are a professional subtitle translator. Translate concisely while preserving the original meaning. Keep translations brief enough to be read quickly as subtitles.",
    "user": "Translate the following subtitle text to {target_language}. Keep the translation concise and easy to read quickly. Preserve the original meaning and any formatting:\n\n{text}"
  }
}
```

To use a specific prompt style, set the `prompt-style` field in your `config.json`:

```json
{
  "prompt-style": "subtitle"
}
```

Available prompt styles in the default `prompts.json`:
- `default`: Standard professional translation
- `chinese`: Translation prompts in Chinese
- `formal`: For formal and official documents
- `casual`: For casual and conversational content
- `technical`: For technical content with specialized terminology
- `subtitle`: Specifically for subtitle translation (concise and easy to read quickly)

### Colorful, Human-Readable Logs

The translator now supports colorful, human-readable logs for better readability and debugging. Different log levels are displayed in different colors:

- DEBUG: Cyan
- INFO: Green
- WARNING: Yellow
- ERROR: Red
- CRITICAL: Red with white background

To enable verbose logging with more detailed information:

```bash
srt-translate -v
```

### Chinese Support

The translator includes support for Chinese in comments, logs, and documentation. This includes:

- Chinese documentation in module docstrings
- Chinese log messages
- Chinese prompts in prompts.json
- Full support for translating to and from Chinese

### Environment Variables

You can set the following environment variables instead of passing them with command-line options or in the configuration file:

```bash
# For OpenAI
export OPENAI_API_KEY=your-openai-api-key

# For DeepSeek
export DEEPSEEK_API_KEY=your-deepseek-api-key
```

### Python API

You can also use the package as a Python library, with both synchronous and asynchronous APIs:

```python
# Synchronous API
from junie_translator_project.main import translate_srt

# Basic usage
output_path = translate_srt(
    input_path="input.srt",
    target_language="Spanish"
)
print(f"Translated file saved to: {output_path}")

# With additional options
output_path = translate_srt(
    input_path="input.srt",
    target_language="French",
    output_path="custom_output.srt",
    translator_type="openai",
    api_key="your-api-key",
    model="gpt-4",
    show_progress=True,
    from_language="English",  # Specify source language
    output_directory="./output",
    lock_file_path="my-lock-file.lock"
)

# Batch processing
from junie_translator_project.main import translate_directory

output_files = translate_directory(
    directory_path="./subtitles",
    target_language="German",
    translator_type="openai",
    file_pattern="*.srt"
)
print(f"Translated {len(output_files)} files")

# Using configuration file
from junie_translator_project.main import Config, main

# Load configuration
config = Config("config.json")
print(f"Target language: {config.get_to_language()}")
print(f"API service: {config.get_api_service_provider()}")

# Run with configuration
exit_code = main("config.json")

# Asynchronous API
import asyncio
from junie_translator_project.translator import TranslatorFactory
from junie_translator_project.main import SRTTranslator, LockFile

async def translate_async():
    # Create a translator service
    translator = TranslatorFactory.create_translator(
        service_type="openai",
        api_key="your-api-key",
        model="gpt-4"
    )
    
    # Create a lock file manager
    lock_file = LockFile("my-lock-file.lock")
    
    # Create an SRT translator
    srt_translator = SRTTranslator(
        translator_service=translator,
        show_progress=True,
        lock_file=lock_file,
        from_language="English",
        output_directory="./output"
    )
    
    # Translate a file asynchronously
    output_path = await srt_translator.translate_file_async(
        input_path="input.srt",
        target_language="French"
    )
    print(f"Translated file saved to: {output_path}")
    
    # Translate all files in a directory asynchronously
    output_files = await srt_translator.translate_directory_async(
        directory_path="./subtitles",
        target_language="Spanish",
        file_pattern="*.srt"
    )
    print(f"Translated {len(output_files)} files")

# Run the async function
asyncio.run(translate_async())

# Advanced usage with batch translation
from junie_translator_project.translator import OpenAITranslator

async def batch_translate_async():
    # Create a translator
    translator = OpenAITranslator(api_key="your-api-key", model="gpt-3.5-turbo")
    
    # Translate multiple texts concurrently
    texts = ["Hello world", "How are you?", "Good morning"]
    translated_texts = await translator.batch_translate_async(texts, "Spanish")
    
    for original, translated in zip(texts, translated_texts):
        print(f"{original} -> {translated}")

# Run the async batch translation
asyncio.run(batch_translate_async())
```

### GitHub Actions Support

The translator supports automatic testing with GitHub Actions and can extract API keys from GitHub Secrets.

#### Setting up GitHub Secrets

1. In your GitHub repository, go to Settings > Secrets and variables > Actions
2. Add your API keys as secrets:
   - `OPENAI_API_KEY` for OpenAI
   - `DEEPSEEK_API_KEY` for DeepSeek
   - Or a generic `API_KEY` that will be used for any service

#### Example GitHub Actions Workflow

```yaml
name: Test SRT Translation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install uv
        uv pip install ".[dev]"
    
    - name: Run translation test
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        srt-translate -v
```

## Extending the Translator

You can create your own translator service by implementing the `TranslatorService` interface. You'll need to implement both synchronous and asynchronous methods:

```python
import asyncio
from junie_translator_project.translator import TranslatorService
from typing import List

class MyCustomTranslator(TranslatorService):
    def __init__(self):
        # Initialize your translator
        pass
        
    def translate(self, text: str, target_language: str) -> str:
        # Implement your synchronous translation logic here
        translated_text = f"[{target_language}] {text}"  # Example implementation
        return translated_text
    
    def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
        # Implement your synchronous batch translation logic here
        return [self.translate(text, target_language) for text in texts]
        
    async def translate_async(self, text: str, target_language: str) -> str:
        # Implement your asynchronous translation logic here
        # If your API doesn't support async, you can use run_in_executor:
        loop = asyncio.get_event_loop()
        translated_text = await loop.run_in_executor(
            None, lambda: self.translate(text, target_language)
        )
        return translated_text
        
    async def batch_translate_async(self, texts: List[str], target_language: str) -> List[str]:
        # Implement your asynchronous batch translation logic here
        # For better performance, create tasks and run them concurrently:
        tasks = [self.translate_async(text, target_language) for text in texts]
        return await asyncio.gather(*tasks)

# Use your custom translator
from junie_translator_project.main import SRTTranslator

# Synchronous usage
translator = MyCustomTranslator()
srt_translator = SRTTranslator(translator_service=translator)
output_path = srt_translator.translate_file("input.srt", "Spanish")

# Asynchronous usage
async def translate_with_custom_translator():
    translator = MyCustomTranslator()
    srt_translator = SRTTranslator(translator_service=translator)
    output_path = await srt_translator.translate_file_async("input.srt", "Spanish")
    return output_path

# Run the async function
output_path = asyncio.run(translate_with_custom_translator())
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.