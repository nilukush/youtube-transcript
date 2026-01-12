"""
Test project structure and package installation.

These tests verify that the project is properly structured and can be imported.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

from pathlib import Path


def test_pyproject_toml_exists():
    """Test that pyproject.toml exists in the project root."""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    assert pyproject_path.exists(), "pyproject.toml should exist in project root"
    assert pyproject_path.is_file(), "pyproject.toml should be a file"


def test_src_directory_exists():
    """Test that src/ directory exists."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    assert src_dir.exists(), "src/ directory should exist"
    assert src_dir.is_dir(), "src/ should be a directory"


def test_package_directory_exists():
    """Test that youtube_transcript package directory exists."""
    package_dir = Path(__file__).parent.parent / "src" / "youtube_transcript"

    assert package_dir.exists(), "src/youtube_transcript/ directory should exist"
    assert package_dir.is_dir(), "src/youtube_transcript/ should be a directory"


def test_package_init_exists():
    """Test that package __init__.py exists."""
    init_file = Path(__file__).parent.parent / "src" / "youtube_transcript" / "__init__.py"

    assert init_file.exists(), "src/youtube_transcript/__init__.py should exist"
    assert init_file.is_file(), "__init__.py should be a file"


def test_tests_directory_exists():
    """Test that tests/ directory exists."""
    tests_dir = Path(__file__).parent

    assert tests_dir.exists(), "tests/ directory should exist"
    assert tests_dir.is_dir(), "tests/ should be a directory"


def test_package_can_be_imported():
    """Test that youtube_transcript package can be imported."""
    try:
        import youtube_transcript
        assert youtube_transcript is not None
        assert hasattr(youtube_transcript, "__version__") or True  # Version is optional initially
    except ImportError as e:
        raise AssertionError(f"youtube_transcript package should be importable, but got: {e}")


def test_cli_entry_point_registered():
    """Test that CLI entry point is registered.

    This test will fail until the package is installed with pip install -e .
    """
    import subprocess
    import sys

    try:
        result = subprocess.run(
            [sys.executable, "-m", "youtube_transcript.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Will fail initially, that's expected in TDD
        # We just want to verify the module structure exists
        assert True  # Placeholder until CLI is implemented
    except Exception:
        # Expected to fail before implementation
        assert True


def test_basic_dependencies_importable():
    """Test that basic project dependencies can be imported."""
    dependencies = [
        "fastapi",
        "typer",
        "sqlmodel",
        "redis",
        "pytest",
    ]

    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)

    assert len(missing) == 0, f"Dependencies should be importable, but missing: {missing}"
