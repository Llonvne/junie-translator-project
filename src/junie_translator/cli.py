"""
Command-line interface for the translator program.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel

from junie_translator import __version__
from junie_translator.srt_parser import SRTParser
from junie_translator.translator import TranslatorFactory, TranslationError
from junie_translator.progress import ProgressTracker

app = typer.Typer(
    help="Junie Translator - A Python program to translate .srt subtitle files using AI services.",
    add_completion=False,
)

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"Junie Translator version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, help="Show version and exit."
    ),
):
    """Junie Translator - A Python program to translate .srt subtitle files using AI services."""
    pass


@app.command()
def translate(
    file_path: str = typer.Argument(
        ..., help="Path to the .srt file or directory containing .srt files to translate."
    ),
    source_lang: str = typer.Option(
        "auto", "--source", "-s", help="Source language code (e.g., 'en', 'fr', 'auto' for auto-detection)."
    ),
    target_lang: str = typer.Option(
        ..., "--target", "-t", help="Target language code (e.g., 'en', 'fr', 'es')."
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="API key for the translation service. If not provided, will try to use OPENAI_API_KEY environment variable."
    ),
    model: str = typer.Option(
        "gpt-3.5-turbo", "--model", "-m", help="Model to use for translation (for OpenAI)."
    ),
    service: str = typer.Option(
        "openai", "--service", help="Translation service to use (currently only 'openai' is supported)."
    ),
):
    """
    Translate .srt subtitle files using AI services.
    """
    try:
        # Check if file_path exists
        path = Path(file_path)
        if not path.exists():
            console.print(f"[bold red]Error:[/bold red] Path '{file_path}' does not exist.")
            raise typer.Exit(1)

        # Create translator
        try:
            translator = TranslatorFactory.create_translator(
                service, api_key=api_key, model=model
            )
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(1)

        # Process files
        if path.is_file() and path.suffix.lower() == ".srt":
            files_to_process = [str(path)]
        elif path.is_dir():
            files_to_process = list(SRTParser.get_srt_files(str(path)))
            if not files_to_process:
                console.print(f"[bold yellow]Warning:[/bold yellow] No .srt files found in '{file_path}'.")
                raise typer.Exit(0)
        else:
            console.print(f"[bold red]Error:[/bold red] '{file_path}' is not a .srt file or a directory.")
            raise typer.Exit(1)

        # Process each file
        for srt_file in files_to_process:
            console.print(f"Processing file: [bold cyan]{srt_file}[/bold cyan]")
            
            # Parse the SRT file
            parser = SRTParser(srt_file)
            lines = parser.get_translatable_lines()
            
            # Translate each line with progress bar
            with ProgressTracker(total=len(lines), description=f"Translating") as progress:
                for index, text in lines:
                    try:
                        translated_text = translator.translate(text, source_lang, target_lang)
                        parser.update_line(index, translated_text)
                    except TranslationError as e:
                        console.print(f"[bold red]Error translating line {index + 1}:[/bold red] {str(e)}")
                        # Continue with next line
                    progress.update()
            
            # Save the translated file
            output_path = parser.save_translated_file(target_lang)
            console.print(f"Translated file saved to: [bold green]{output_path}[/bold green]")

        console.print(Panel.fit("Translation completed successfully!", title="Success", border_style="green"))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()