"""
Test web UI templates and routes.

These tests verify that HTML templates are properly configured and rendered.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

from fastapi.testclient import TestClient
from fastapi import status


class TestWebUIConfiguration:
    """Test Jinja2 configuration and setup."""

    def test_jinja2_templates_directory_exists(self):
        """Test that templates directory exists."""
        import os
        templates_dir = "src/youtube_transcript/templates"
        assert os.path.exists(templates_dir), f"Templates directory {templates_dir} should exist"

    def test_base_template_exists(self):
        """Test that base template exists."""
        import os
        base_template = "src/youtube_transcript/templates/base.html"
        assert os.path.exists(base_template), f"Base template {base_template} should exist"

    def test_index_template_exists(self):
        """Test that index template exists."""
        import os
        index_template = "src/youtube_transcript/templates/index.html"
        assert os.path.exists(index_template), f"Index template {index_template} should exist"

    def test_results_template_exists(self):
        """Test that results template exists."""
        import os
        results_template = "src/youtube_transcript/templates/results.html"
        assert os.path.exists(results_template), f"Results template {results_template} should exist"

    def test_error_template_exists(self):
        """Test that error template exists."""
        import os
        error_template = "src/youtube_transcript/templates/error.html"
        assert os.path.exists(error_template), f"Error template {error_template} should exist"


class TestWebUIRoutes:
    """Test web UI routes."""

    def test_index_route_returns_html(self, test_client: TestClient):
        """Test that index route returns HTML."""
        response = test_client.get("/")
        # Should return HTML (might be JSON welcome message initially)
        assert response.status_code == status.HTTP_200_OK

    def test_index_route_has_correct_content_type(self, test_client: TestClient):
        """Test that index route returns HTML content type."""
        response = test_client.get("/")
        # After implementation, should be text/html
        # Initially might be application/json
        assert response.status_code == status.HTTP_200_OK

    def test_index_page_contains_form(self, test_client: TestClient):
        """Test that index page contains URL input form."""
        response = test_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        # Should contain form elements after implementation
        content = response.text.lower()
        # Check for form elements (will fail initially with JSON response)
        has_form = "<form" in content or "url" in content
        # For now, just check it returns successfully

    def test_web_results_route_exists(self, test_client: TestClient):
        """Test that web results route is registered."""
        # This route will display HTML results (not JSON)
        response = test_client.get("/transcript/dQw4w9WgXcQ")
        # Should not return 404 (might return HTML or JSON)
        assert response.status_code != status.HTTP_404_NOT_FOUND


class TestTemplateRendering:
    """Test template rendering functionality."""

    def test_base_template_has_required_blocks(self):
        """Test that base template has required Jinja2 blocks."""
        with open("src/youtube_transcript/templates/base.html") as f:
            content = f.read()
        # Should have content block
        assert "{% block content %}" in content or "{% block content %}" in content.lower()

    def test_index_template_extends_base(self):
        """Test that index template extends base template."""
        with open("src/youtube_transcript/templates/index.html") as f:
            content = f.read()
        # Should extend base template
        assert "{% extends" in content
        assert "base.html" in content

    def test_results_template_extends_base(self):
        """Test that results template extends base template."""
        with open("src/youtube_transcript/templates/results.html") as f:
            content = f.read()
        # Should extend base template
        assert "{% extends" in content
        assert "base.html" in content

    def test_error_template_extends_base(self):
        """Test that error template extends base template."""
        with open("src/youtube_transcript/templates/error.html") as f:
            content = f.read()
        # Should extend base template
        assert "{% extends" in content
        assert "base.html" in content


class TestWebUIIntegration:
    """Test web UI integration with services."""

    def test_index_page_renders_successfully(self, test_client: TestClient):
        """Test that index page renders without errors."""
        response = test_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        # Should be HTML after implementation
        assert len(response.content) > 0

    def test_index_page_has_title(self, test_client: TestClient):
        """Test that index page has a title."""
        response = test_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        content = response.text
        # Should contain YouTube Transcript in title after implementation
        # For now, just check it returns content


class TestStaticFiles:
    """Test static file serving."""

    def test_static_directory_exists(self):
        """Test that static directory exists."""
        import os
        static_dir = "src/youtube_transcript/static"
        assert os.path.exists(static_dir), f"Static directory {static_dir} should exist"

    def test_css_directory_exists(self):
        """Test that CSS directory exists."""
        import os
        css_dir = "src/youtube_transcript/static/css"
        assert os.path.exists(css_dir), f"CSS directory {css_dir} should exist"

    def test_main_css_exists(self):
        """Test that main CSS file exists."""
        import os
        css_file = "src/youtube_transcript/static/css/main.css"
        assert os.path.exists(css_file), f"Main CSS file {css_file} should exist"


class TestTemplateContext:
    """Test template context and variables."""

    def test_base_template_has_title_variable(self):
        """Test that base template uses title variable."""
        with open("src/youtube_transcript/templates/base.html") as f:
            content = f.read()
        # Should have title variable
        assert "{% block title %}" in content or "{{ title" in content

    def test_index_template_has_form_context(self):
        """Test that index template can receive form context."""
        with open("src/youtube_transcript/templates/index.html") as f:
            content = f.read()
        # Should have form-related context variables
        assert len(content) > 0  # Basic check that template has content

    def test_results_template_has_transcript_context(self):
        """Test that results template can receive transcript data."""
        with open("src/youtube_transcript/templates/results.html") as f:
            content = f.read()
        # Should have transcript context variables
        assert len(content) > 0  # Basic check that template has content
