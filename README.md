# Junie Translator Project

A Python program for translating SRT subtitle files using AI services like OpenAI.

## Features

- Translate SRT subtitle files to any language using AI services
- Process one line at a time for accurate translations
- Display a progress bar showing translation progress
- Output well-named SRT files with source language, target language, and file hash in the filename
- Extensible architecture that supports different translation services
- Command-line interface with multiple operation modes
- Configuration file support for easy setup and reuse
- Lock file mechanism to avoid duplicate translations
- Batch processing of multiple SRT files in a directory
- Source language auto-detection or manual specification

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

The package installs a command-line tool called `srt-translate` that you can use to translate SRT files. The tool has three operation modes:

1. **Config Mode**: Use a configuration file to translate all SRT files in the current directory
2. **File Mode**: Translate a single SRT file
3. **Directory Mode**: Translate all SRT files in a directory

#### Config Mode

```bash
# Use default config.json in current directory
srt-translate config

# Specify a custom config file
srt-translate config -c my-config.json
```

#### File Mode

```bash
# Basic usage
srt-translate file input.srt Spanish

# Specify output file
srt-translate file input.srt French -o output_french.srt

# Specify source language (default is auto-detect)
srt-translate file input.srt German -f English

# Use a specific API key
srt-translate file input.srt Japanese -k your-api-key

# Use a different model
srt-translate file input.srt Italian -m gpt-4

# Specify output directory
srt-translate file input.srt Chinese -d ./output

# Specify lock file path
srt-translate file input.srt Russian -l my-lock-file.lock

# Disable progress bar
srt-translate file input.srt Korean --no-progress

# Use mock translator for testing
srt-translate file input.srt Portuguese -t mock
```

#### Directory Mode

```bash
# Translate all SRT files in a directory
srt-translate dir ./subtitles Spanish

# Specify file pattern (default is *.srt)
srt-translate dir ./subtitles French -p "*.en.srt"

# Specify source language
srt-translate dir ./subtitles German -f English

# Specify output directory
srt-translate dir ./subtitles Japanese -d ./output

# Use a specific translator service
srt-translate dir ./subtitles Italian -t openai
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
  "model": "gpt-3.5-turbo"
}
```

### Environment Variables

You can set the following environment variables instead of passing them with command-line options or in the configuration file:

```bash
# For OpenAI
export OPENAI_API_KEY=your-openai-api-key

# For DeepSeek
export DEEPSEEK_API_KEY=your-deepseek-api-key
```

### Python API

You can also use the package as a Python library:

```python
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

# Advanced usage
from junie_translator_project.translator import TranslatorFactory
from junie_translator_project.main import SRTTranslator, LockFile

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

# Translate a file
output_path = srt_translator.translate_file(
    input_path="input.srt",
    target_language="French"
)

# Translate all files in a directory
output_files = srt_translator.translate_directory(
    directory_path="./subtitles",
    target_language="Spanish",
    file_pattern="*.srt"
)
```

## Extending the Translator

You can create your own translator service by implementing the `TranslatorService` interface:

```python
from junie_translator_project.translator import TranslatorService
from typing import List

class MyCustomTranslator(TranslatorService):
    def translate(self, text: str, target_language: str) -> str:
        # Implement your translation logic here
        return translated_text
    
    def batch_translate(self, texts: List[str], target_language: str) -> List[str]:
        # Implement your batch translation logic here
        return [self.translate(text, target_language) for text in texts]

# Use your custom translator
from junie_translator_project.main import SRTTranslator

translator = MyCustomTranslator()
srt_translator = SRTTranslator(translator_service=translator)
output_path = srt_translator.translate_file("input.srt", "Spanish")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.