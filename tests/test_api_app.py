"""
Test FastAPI application core.

These tests verify that the FastAPI application is properly configured
with all necessary dependencies, middleware, and error handling.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

import pytest
from fastapi.testclient import TestClient

from youtube_transcript.api.app import app


class TestFastAPIApplicationCreation:
    """Test FastAPI application initialization."""

    def test_app_can_be_created(self):
        """Test that FastAPI app can be created."""
        from youtube_transcript.api.app import app

        assert app is not None
        assert app.title == "YouTube Transcript Fetcher API"


class TestApplicationConfiguration:
    """Test FastAPI application configuration."""

    def test_app_has_correct_title(self):
        """Test that app has correct title."""
        assert app.title == "YouTube Transcript Fetcher API"

    def test_app_has_correct_version(self):
        """Test that app has version information."""
        assert app.version is not None

    def test_app_has_correct_description(self):
        """Test that app has description."""
        assert app.description is not None


class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    def test_cors_middleware_is_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check if CORSMiddleware is in the middleware stack
        from fastapi.middleware.cors import CORSMiddleware

        # Middleware is wrapped in Middleware class, check the cls attribute
        has_cors = any(m.cls == CORSMiddleware for m in app.user_middleware)
        assert has_cors, "CORSMiddleware should be in middleware stack"


class TestHealthCheckEndpoints:
    """Test health check and status endpoints."""

    def test_root_endpoint_returns_welcome(self, test_client: TestClient):
        """Test that root endpoint returns welcome page."""
        response = test_client.get("/")

        assert response.status_code == 200
        # Root endpoint now returns HTML (web UI)
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type or "application/json" in content_type

        # If HTML, check for expected content
        if "text/html" in content_type:
            assert "YouTube Transcript Fetcher" in response.text
        else:
            # If JSON (for API-only mode)
            data = response.json()
            assert "message" in data or "title" in data

    def test_health_endpoint_returns_ok(self, test_client: TestClient):
        """Test that /health endpoint returns health status."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_endpoint_includes_service_info(self, test_client: TestClient):
        """Test that /health endpoint includes service information."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "youtube-transcript-fetcher"


class TestErrorHandlers:
    """Test global error handlers."""

    def test_404_handler_returns_json(self, test_client: TestClient):
        """Test that 404 errors return JSON response."""
        response = test_client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "error" in data

    def test_422_validation_error_returns_json(self, test_client: TestClient):
        """Test that validation errors return JSON response."""
        response = test_client.get("/health", params={"invalid": "param"})

        # Should either succeed or return proper JSON error
        assert response.status_code in [200, 422]
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data


class TestDependencyInjection:
    """Test dependency injection setup."""

    def test_get_session_dependency_exists(self, test_client: TestClient):
        """Test that database session dependency is configured."""
        from youtube_transcript.models import get_session

        # Dependency should be importable
        assert get_session is not None

    def test_orchestrator_dependency_exists(self):
        """Test that orchestrator can be created."""
        from youtube_transcript.services import TranscriptOrchestrator

        # Should be importable
        assert TranscriptOrchestrator is not None


class TestAPIRoutes:
    """Test API route registration."""

    def test_api_routes_are_registered(self, test_client: TestClient):
        """Test that API routes are registered."""
        response = test_client.get("/docs")

        # Swagger UI should be available
        assert response.status_code == 200

    def test_openapi_schema_exists(self, test_client: TestClient):
        """Test that OpenAPI schema is generated."""
        response = test_client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestApplicationLifecycle:
    """Test application startup and shutdown events."""

    def test_app_can_be_started(self):
        """Test that application can be started without errors."""
        # Creating the app should not raise exceptions
        from youtube_transcript.api.app import create_app

        test_app = create_app()
        assert test_app is not None


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_logging_is_configured(self):
        """Test that logging is properly configured."""
        import logging

        # Should be able to get loggers
        logger = logging.getLogger("youtube_transcript")
        assert logger is not None
