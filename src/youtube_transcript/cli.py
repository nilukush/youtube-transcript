"""CLI entry point for YouTube Transcript Fetcher."""

import sys
import json
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.syntax import Syntax

from youtube_transcript.models import init_db, get_session
from youtube_transcript.services import TranscriptOrchestrator
from youtube_transcript.utils.url_parser import extract_video_id


app = typer.Typer(
    name="ytt",
    help="YouTube Transcript Fetcher CLI - Fetch transcripts from YouTube videos",
    add_completion=True,
)

console = Console()

__version__ = "0.1.0"


def version_callback(value: bool) -> None:
    """Handle --version flag.

    Prints version and exits if --version flag is provided.
    Uses is_eager=True to process before command validation.

    Args:
        value: True if --version flag was provided
    """
    if value:
        typer.echo(f"ytt version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """YouTube Transcript Fetcher CLI.

    Fetch transcripts from any YouTube video with support for multiple languages,
    output formats, and file export options.
    """
    pass  # Version logic handled in callback


@app.command("fetch")
def fetch_transcript(
    url_or_id: str = typer.Argument(
        ...,
        help="YouTube video URL or video ID",
        show_default=False,
    ),
    languages: Optional[str] = typer.Option(
        None,
        "--lang",
        "-l",
        help="Preferred language codes in priority order (comma-separated). Returns the first available transcript. Example: 'en,es,fr' tries English first, then Spanish, then French.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (writes to file instead of stdout)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in JSON format instead of plain text",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed information about the fetch process",
    ),
):
    """Fetch a transcript from a YouTube video.

    Examples:

        Fetch by URL:
        $ ytt fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        Fetch by video ID:
        $ ytt fetch dQw4w9WgXcQ

        Fetch with language preference:
        $ ytt fetch dQw4w9WgXcQ --lang en

        Fetch and save to file:
        $ ytt fetch dQw4w9WgXcQ -o transcript.txt

        Fetch in JSON format:
        $ ytt fetch dQw4w9WgXcQ --json
    """
    # Initialize database
    if verbose:
        console.print("[dim]Initializing database...[/dim]")
    init_db()

    # Extract video ID
    if verbose:
        console.print(f"[dim]Parsing URL/ID: {url_or_id}[/dim]")

    video_id = extract_video_id(url_or_id)

    if not video_id:
        console.print("[red]Error:[/red] Invalid YouTube URL or video ID")
        console.print(f"[dim]Input: {url_or_id}[/dim]")
        console.print("\nExpected formats:")
        console.print("  • https://www.youtube.com/watch?v=VIDEO_ID")
        console.print("  • https://youtu.be/VIDEO_ID")
        console.print("  • VIDEO_ID (11-character alphanumeric)")
        raise typer.Exit(code=1)

    if verbose:
        console.print(f"[green]✓[/green] Extracted video ID: [cyan]{video_id}[/cyan]")

    # Parse languages
    lang_list = None
    if languages:
        lang_list = [l.strip() for l in languages.split(",")]
        if verbose:
            console.print(f"[dim]Language preference: {', '.join(lang_list)}[/dim]")

    # Fetch transcript
    if verbose:
        console.print("[dim]Fetching transcript...[/dim]")

    session_gen = get_session()
    session = next(session_gen)
    orchestrator = TranscriptOrchestrator(session=session)

    try:
        result = orchestrator.get_transcript(video_id, languages=lang_list)

        if not result:
            console.print(f"[red]Error:[/red] Transcript not found for video '{video_id}'")
            console.print("\nPossible reasons:")
            console.print("  • The video has no transcript/captions")
            console.print("  • The transcript is disabled by the uploader")
            console.print("  • The video ID is incorrect")
            console.print(f"\nVideo: https://www.youtube.com/watch?v={video_id}")
            raise typer.Exit(code=1)

        # Success!
        if verbose:
            console.print(f"[green]✓[/green] Transcript fetched successfully!")
            console.print(f"[dim]  Language: {result.language}[/dim]")
            console.print(f"[dim]  Type: {result.transcript_type}[/dim]")
            console.print(f"[dim]  Length: {len(result.transcript)} characters[/dim]")

        # Format output
        if json_output:
            output_data = {
                "video_id": result.video_id,
                "language": result.language,
                "transcript_type": result.transcript_type,
                "transcript": result.transcript,
                "url": f"https://www.youtube.com/watch?v={result.video_id}",
            }
            output_text = json.dumps(output_data, indent=2, ensure_ascii=False)
        else:
            output_text = result.transcript

        # Write output
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_text, encoding="utf-8")
            if verbose:
                console.print(f"[green]✓[/green] Written to [cyan]{output_path}[/cyan]")
        else:
            if json_output:
                # Pretty print JSON
                if verbose:
                    syntax = Syntax(output_text, "json", theme="monokai", line_numbers=True)
                    console.print(syntax)
                else:
                    typer.echo(output_text)
            else:
                typer.echo(output_text)

        return

    except typer.Exit:
        # Re-raise typer.Exit to allow proper exit
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        if verbose:
            import traceback
            console.print("\n[dim]Traceback:[/dim]")
            console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command("version")
def version_command():
    """Show version information."""
    typer.echo(f"ytt version {__version__}")


if __name__ == "__main__":
    app()
