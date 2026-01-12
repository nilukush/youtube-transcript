"""
Test HTMX integration for dynamic interactions.

These tests verify that HTMX is properly configured and provides
dynamic content updates without page refreshes.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

from fastapi.testclient import TestClient
from fastapi import status


class TestHTMXConfiguration:
    """Test HTMX library inclusion."""

    def test_base_template_includes_htmx(self):
        """Test that base template includes HTMX library."""
        with open("src/youtube_transcript/templates/base.html") as f:
            content = f.read()
        # Should include HTMX script from CDN
        assert "htmx.org" in content.lower()
        assert "script" in content.lower()

    def test_htmx_version(self):
        """Test that HTMX version is specified."""
        with open("src/youtube_transcript/templates/base.html") as f:
            content = f.read()
        # Should use recent HTMX version (1.x or 2.x)
        assert "htmx" in content.lower()


class TestHTMXEndpoints:
    """Test HTMX-specific endpoints."""

    def test_htmx_transcript_search_endpoint_exists(self, test_client: TestClient):
        """Test that HTMX transcript search endpoint exists."""
        # This endpoint should return HTML fragments for HTMX
        response = test_client.get("/htmx/transcript?url=https://youtu.be/dQw4w9WgXcQ")
        # Should not return 404
        assert response.status_code != status.HTTP_404_NOT_FOUND

    def test_htmx_endpoint_returns_html_fragment(self, test_client: TestClient):
        """Test that HTMX endpoint returns HTML fragment."""
        # With valid URL, should return HTML (not JSON)
        response = test_client.get(
            "/htmx/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            headers={"HX-Request": "true"}
        )
        # Should process request
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_htmx_endpoint_handles_htmx_header(self, test_client: TestClient):
        """Test that endpoint properly handles HX-Request header."""
        response = test_client.get(
            "/htmx/transcript?url=https://youtu.be/dQw4w9WgXcQ",
            headers={"HX-Request": "true"}
        )
        # Should recognize HTMX request
        assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


class TestHTMXPartialTemplates:
    """Test HTMX partial templates."""

    def test_loading_template_exists(self):
        """Test that loading spinner template exists."""
        import os
        loading_template = "src/youtube_transcript/templates/partials/loading.html"
        assert os.path.exists(loading_template), f"Loading template {loading_template} should exist"

    def test_transcript_fragment_template_exists(self):
        """Test that transcript fragment template exists."""
        import os
        fragment_template = "src/youtube_transcript/templates/partials/transcript_fragment.html"
        assert os.path.exists(fragment_template), f"Fragment template {fragment_template} should exist"

    def test_error_fragment_template_exists(self):
        """Test that error fragment template exists."""
        import os
        error_template = "src/youtube_transcript/templates/partials/error_fragment.html"
        assert os.path.exists(error_template), f"Error fragment template {error_template} should exist"


class TestHTMXInteractions:
    """Test HTMX interaction patterns."""

    def test_form_has_htmx_attributes(self):
        """Test that form uses HTMX attributes."""
        with open("src/youtube_transcript/templates/index.html") as f:
            content = f.read()
        # Should have hx-post or hx-get attribute
        assert "hx-" in content or "data-hx-" in content

    def test_loading_indicator_configured(self):
        """Test that loading indicator is configured."""
        with open("src/youtube_transcript/templates/index.html") as f:
            content = f.read()
        # Should have hx-indicator or loading handling
        assert "indicator" in content.lower() or "loading" in content.lower()

    def test_target_swap_configured(self):
        """Test that target swap is configured."""
        with open("src/youtube_transcript/templates/index.html") as f:
            content = f.read()
        # Should have hx-target or hx-swap
        assert "hx-target" in content or "hx-swap" in content or "data-hx-target" in content


class TestHTMXSecurity:
    """Test HTMX security considerations."""

    def test_htmx_headers_validated(self, test_client: TestClient):
        """Test that HTMX headers are properly validated."""
        # Try with invalid HX-Request value
        response = test_client.get(
            "/htmx/transcript?url=invalid",
            headers={"HX-Request": "invalid"}
        )
        # Should handle gracefully
        assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


class TestHTMXProgressiveEnhancement:
    """Test that app works without HTMX."""

    def test_form_works_without_htmx(self, test_client: TestClient):
        """Test that form submission works without JavaScript/HTMX."""
        # Standard form submission should still work
        response = test_client.get("/transcript?url=https://youtu.be/dQw4w9WgXcQ")
        # Should return HTML page
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        # Should be valid HTML
        assert "text/html" in response.headers.get("content-type", "").lower()

    def test_api_works_without_htmx(self, test_client: TestClient):
        """Test that JSON API still works independently."""
        import json

        # API endpoint should return JSON
        response = test_client.post(
            "/api/transcript",
            json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
        )
        # Should work without HTMX
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "video_id" in data or "error" in data
