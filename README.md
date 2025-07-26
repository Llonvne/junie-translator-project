# Junie Translator Project

A Python program for translating SRT subtitle files using AI services like OpenAI.

## Features

- Translate SRT subtitle files to any language using AI services
- Process one line at a time for accurate translations
- Display a progress bar showing translation progress
- Output well-named SRT files with the target language in the filename
- Extensible architecture that supports different translation services
- Command-line interface for easy usage

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

The package installs a command-line tool called `srt-translate` that you can use to translate SRT files:

```bash
# Basic usage
srt-translate input.srt Spanish

# Specify output file
srt-translate input.srt French -o output_french.srt

# Use a specific API key
srt-translate input.srt German -k your-api-key

# Use a different model
srt-translate input.srt Japanese -m gpt-4

# Disable progress bar
srt-translate input.srt Italian --no-progress

# Use mock translator for testing
srt-translate input.srt Chinese -t mock
```

### Environment Variables

You can set the `OPENAI_API_KEY` environment variable instead of passing it with the `-k` option:

```bash
export OPENAI_API_KEY=your-api-key
srt-translate input.srt Spanish
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

# Advanced usage
from junie_translator_project.translator import TranslatorFactory
from junie_translator_project.main import SRTTranslator

# Create a translator service
translator = TranslatorFactory.create_translator(
    service_type="openai",
    api_key="your-api-key",
    model="gpt-4"
)

# Create an SRT translator
srt_translator = SRTTranslator(
    translator_service=translator,
    show_progress=True
)

# Translate a file
output_path = srt_translator.translate_file(
    input_path="input.srt",
    target_language="French",
    output_path="custom_output.srt"
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