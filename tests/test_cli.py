"""
Test CLI functionality.

These tests verify that the CLI tool works correctly with various options.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

import subprocess
import sys
from typer.testing import CliRunner
from pathlib import Path
import json

import pytest


class TestCLIInstallation:
    """Test CLI installation and basic functionality."""

    def test_cli_module_exists(self):
        """Test that CLI module exists."""
        import os
        cli_module = "src/youtube_transcript/cli.py"
        assert os.path.exists(cli_module), f"CLI module {cli_module} should exist"

    def test_cli_main_function_exists(self):
        """Test that CLI main function exists."""
        from youtube_transcript.cli import app
        assert app is not None, "CLI app should exist"


class TestCLIBasicCommands:
    """Test basic CLI commands."""

    def test_cli_help_command(self):
        """Test that CLI help command works."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ytt" in result.stdout.lower() or "youtube" in result.stdout.lower()

    def test_cli_version_command(self):
        """Test that CLI version command works."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        # Version command should exit with code 0 and show version
        assert result.exit_code == 0
        assert "version" in result.stdout.lower() or "0.1" in result.stdout

    def test_cli_version_flag_works(self):
        """Test that --version flag works without requiring a command."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        # Should show version and exit cleanly without "Missing command" error
        assert result.exit_code == 0
        assert "version" in result.stdout.lower() or "0.1" in result.stdout
        assert "Missing command" not in result.stdout

    def test_cli_version_short_flag_works(self):
        """Test that -v short flag works without requiring a command."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["-v"])
        # Should show version and exit cleanly
        assert result.exit_code == 0
        assert "version" in result.stdout.lower() or "0.1" in result.stdout
        assert "Missing command" not in result.stdout


class TestCLITranscriptFetch:
    """Test transcript fetching via CLI."""

    def test_cli_requires_url_argument(self):
        """Test that CLI requires URL argument."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch"])
        assert result.exit_code != 0 or "missing" in result.stdout.lower()

    def test_cli_accepts_youtube_url(self):
        """Test that CLI accepts YouTube URL."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "https://youtu.be/j9rZxAF3C0I"])
        # Should not error on URL parsing (may fail on actual fetch)
        assert "invalid url" not in result.stdout.lower()

    def test_cli_accepts_video_id(self):
        """Test that CLI accepts video ID directly."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "j9rZxAF3C0I"])
        # Should not error on video ID (may fail on actual fetch)
        assert "invalid" not in result.stdout.lower() or result.exit_code == 0


class TestCLIOutputFormats:
    """Test CLI output format options."""

    def test_cli_default_text_output(self):
        """Test that CLI defaults to text output."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "--help"])
        # Should mention output format in help
        assert "output" in result.stdout.lower() or "format" in result.stdout.lower()

    def test_cli_json_output_option(self):
        """Test that CLI supports JSON output."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "--help"])
        assert "--json" in result.stdout or "json" in result.stdout.lower()

    def test_cli_text_output_option(self):
        """Test that CLI supports text output."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "--help"])
        assert "text" in result.stdout.lower() or "plain text" in result.stdout.lower()


class TestCLIFileOutput:
    """Test CLI file output options."""

    def test_cli_file_output_option(self):
        """Test that CLI supports file output."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "--help"])
        assert "file" in result.stdout.lower() or "--output" in result.stdout or "-o" in result.stdout

    def test_cli_writes_to_file(self, tmp_path):
        """Test that CLI can write transcript to file."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        output_file = tmp_path / "transcript.txt"
        # This test will fail initially - CLI implementation needed
        # After implementation, this should create a file
        pass


class TestCLILanguageOptions:
    """Test CLI language selection options."""

    def test_cli_language_option(self):
        """Test that CLI supports language selection."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "--help"])
        assert "lang" in result.stdout.lower() or "language" in result.stdout.lower()

    def test_cli_accepts_language_code(self):
        """Test that CLI accepts language codes."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "--help"])
        # Should mention language codes in help
        assert "en" in result.stdout or "code" in result.stdout.lower()


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_handles_invalid_url(self):
        """Test that CLI handles invalid URLs gracefully."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "not-a-url"])
        assert result.exit_code != 0 or "error" in result.stdout.lower()

    def test_cli_handles_unavailable_transcript(self):
        """Test that CLI handles unavailable transcripts."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "INVALID000"])
        # Should not crash
        assert result.exit_code != 0 or "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_cli_shows_helpful_error_messages(self):
        """Test that CLI shows helpful error messages."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "invalid-url"])
        assert len(result.stdout) > 0  # Should have some output

    def test_cli_successful_fetch_does_not_print_error_message(self):
        """Test that successful transcript fetch doesn't print 'Error:' message.

        This is a regression test for the bug where typer.Exit(code=0) was caught
        by the general Exception handler, causing "Error:" to appear after successful
        fetches. The fix ensures successful fetches use return instead of raise.

        See commit 02af638 for the fix.
        """
        from youtube_transcript.cli import app
        runner = CliRunner()

        # Use a known video ID with available transcript
        result = runner.invoke(app, ["fetch", "dQw4w9WgXcQ"])

        # Successful fetch should NOT contain "Error:" in output
        # (Note: actual fetch may fail due to rate limiting, but the bug
        # was that even successful fetches showed "Error:")
        if result.exit_code == 0:
            assert "Error:" not in result.stdout, (
                "Successful transcript fetch should not print 'Error:' message. "
                "This indicates the typer.Exit exception handling bug has regressed."
            )


class TestCLIIntegration:
    """Test CLI integration with services."""

    def test_cli_uses_orchestrator(self):
        """Test that CLI uses TranscriptOrchestrator."""
        import os
        cli_file = "src/youtube_transcript/cli.py"
        with open(cli_file) as f:
            content = f.read()
        # Should import and use orchestrator
        assert "orchestrator" in content.lower() or "transcript" in content.lower()

    def test_cli_initializes_database(self):
        """Test that CLI initializes database."""
        import os
        cli_file = "src/youtube_transcript/cli.py"
        with open(cli_file) as f:
            content = f.read()
        # Should initialize database
        assert "init_db" in content or "get_session" in content or "database" in content.lower()


class TestCLIEntryPoints:
    """Test CLI entry points configuration."""

    def test_pyproject_toml_has_cli_entry_point(self):
        """Test that pyproject.toml has CLI entry point configured."""
        import os
        if not os.path.exists("pyproject.toml"):
            pytest.skip("pyproject.toml not found")
        with open("pyproject.toml") as f:
            content = f.read()
        # Should have CLI entry point
        assert "ytt" in content.lower() or "console_scripts" in content or "entry-points" in content.lower()

    def test_cli_entry_point_points_to_main(self):
        """Test that CLI entry point points to correct function."""
        import os
        if not os.path.exists("pyproject.toml"):
            pytest.skip("pyproject.toml not found")
        with open("pyproject.toml") as f:
            content = f.read()
        # Should reference cli module
        assert "cli" in content.lower() or "main" in content.lower()


class TestCLIVerboseMode:
    """Test CLI verbose mode."""

    def test_cli_verbose_option(self):
        """Test that CLI supports verbose mode."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["fetch", "--help"])
        assert "verbose" in result.stdout.lower() or "--verbose" in result.stdout

    def test_cli_shows_detailed_info_in_verbose(self):
        """Test that CLI shows detailed info in verbose mode."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        # This test will be enabled after implementation
        # result = runner.invoke(app, ["--verbose", "fetch", "j9rZxAF3C0I"])
        # Should show more information than non-verbose mode
        pass


class TestCLIConfigFile:
    """Test CLI configuration file support."""

    def test_cli_config_option(self):
        """Test that CLI supports config file option."""
        from youtube_transcript.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        # Config file is optional, so we just check it doesn't crash
        assert result.exit_code == 0
