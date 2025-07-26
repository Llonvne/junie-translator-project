# Junie Translator

A tool for translating subtitle files using AI services.

## Features

- Translate subtitle files (.srt) to any language using OpenAI's API
- Progress bar showing translation progress
- Extensible architecture for adding support for other subtitle formats and translation services
- Command-line interface for easy use

## Installation

### Using uv (recommended)

```bash
uv pip install .
```

### Using pip

```bash
pip install .
```

## Usage

### Command-line Interface

```bash
junie-translator input.srt target_language [options]
```

#### Arguments

- `input.srt`: The subtitle file to translate
- `target_language`: The language code to translate to (e.g., 'es' for Spanish, 'fr' for French)

#### Options

- `-o, --output-file`: The path to write the translated subtitle file to (default: auto-generated)
- `-t, --translator`: The translator service to use (default: openai)
- `-k, --api-key`: The API key for the translator service (default: read from environment)
- `-m, --model`: The model to use for translation (default: gpt-3.5-turbo)
- `-d, --delay`: The delay between translation requests in seconds (default: 0.1)
- `--max-retries`: The maximum number of retries for failed translation requests (default: 3)
- `--retry-delay`: The initial delay between retries in seconds (default: 1.0)

### Environment Variables

- `OPENAI_API_KEY`: The API key for OpenAI

### Examples

#### Translate a subtitle file to Spanish

```bash
junie-translator subtitles.srt es
```

#### Translate a subtitle file to French with a custom output file

```bash
junie-translator subtitles.srt fr -o subtitles_french.srt
```

#### Translate a subtitle file to German using a specific API key

```bash
junie-translator subtitles.srt de -k your_api_key_here
```

#### Translate a subtitle file to Japanese using a specific model

```bash
junie-translator subtitles.srt ja -m gpt-4
```

## Extending the Translator

### Adding a New Translator

To add a new translator service, create a new class that implements the `BaseTranslator` interface:

```python
from junie_translator.translators.base import BaseTranslator

class MyTranslator(BaseTranslator):
    def __init__(self, api_key: str, **kwargs):
        # Initialize your translator
        pass
    
    def translate(self, text: str, target_language: str, **kwargs) -> str:
        # Implement translation logic
        pass
    
    def is_available(self) -> bool:
        # Check if the service is available
        pass
```

Then register it with the `TranslatorFactory`:

```python
from junie_translator.factory import TranslatorFactory
from my_module import MyTranslator

TranslatorFactory.register('my_translator', MyTranslator)
```

### Adding a New Parser

To add support for a new subtitle format, create a new class that implements the `BaseParser` interface:

```python
from junie_translator.parsers.base import BaseParser, SubtitleEntry

class MyParser(BaseParser):
    def parse(self, file_path: str) -> List[SubtitleEntry]:
        # Implement parsing logic
        pass
    
    def write(self, entries: List[SubtitleEntry], output_path: str) -> None:
        # Implement writing logic
        pass
    
    def get_extension(self) -> str:
        # Return the file extension
        pass
```

Then register it with the `ParserFactory`:

```python
from junie_translator.factory import ParserFactory
from my_module import MyParser

ParserFactory.register('.myext', MyParser)
```

## License

MIT