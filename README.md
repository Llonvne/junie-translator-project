# Junie Translator

A Python program to translate .srt subtitle files using AI services.

## Features

- Translate .srt subtitle files using OpenAI's API
- Process one line at a time for accurate translations
- Show progress bar during translation
- Output well-named translated .srt files
- Support for processing individual files or entire directories
- Extensible architecture for adding new translation services

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Clone the repository
git clone https://github.com/yourusername/junie-translator.git
cd junie-translator

# Install the package
uv pip install .
```

## Usage

### Basic Usage

```bash
# Translate a single .srt file from auto-detected language to Spanish
junie-translate path/to/subtitles.srt --target es

# Translate all .srt files in a directory from English to French
junie-translate path/to/subtitles/directory --source en --target fr
```

### Command-line Options

```
Usage: junie-translate [OPTIONS] FILE_PATH

  Translate .srt subtitle files using AI services.

Arguments:
  FILE_PATH  Path to the .srt file or directory containing .srt files to translate.  [required]

Options:
  -s, --source TEXT     Source language code (e.g., 'en', 'fr', 'auto' for auto-detection).  [default: auto]
  -t, --target TEXT     Target language code (e.g., 'en', 'fr', 'es').  [required]
  -k, --api-key TEXT    API key for the translation service. If not provided, will try to use OPENAI_API_KEY environment variable.
  -m, --model TEXT      Model to use for translation (for OpenAI).  [default: gpt-3.5-turbo]
  --service TEXT        Translation service to use (currently only 'openai' is supported).  [default: openai]
  -v, --version         Show version and exit.
  --help                Show this message and exit.
```

### Environment Variables

You can set the OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your-api-key-here
```

## Examples

### Translate a Single File

```bash
junie-translate subtitles.srt --target es
```

This will translate `subtitles.srt` to Spanish and save the result as `subtitles_es.srt`.

### Translate All Files in a Directory

```bash
junie-translate subtitles_directory --source en --target fr
```

This will translate all .srt files in `subtitles_directory` from English to French.

### Specify a Different Model

```bash
junie-translate subtitles.srt --target de --model gpt-4
```

This will translate `subtitles.srt` to German using the GPT-4 model.

## Extending the Translator

The translator is designed to be extensible. To add a new translation service:

1. Create a new class that inherits from `BaseTranslator` in `translator.py`
2. Implement the `translate` method
3. Add the new translator to the `TranslatorFactory`

## License

MIT