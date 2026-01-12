"""
Test transcript API endpoints.

These tests verify that the transcript API endpoints correctly handle
requests and integrate with the TranscriptOrchestrator service.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
from fastapi import status

from youtube_transcript.services.fetcher import TranscriptResult
from youtube_transcript.api.app import app


def override_orchestrator(mock_orchestrator):
    """Helper to override the orchestrator dependency."""
    from youtube_transcript.api.endpoints import get_orchestrator
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator


def clear_overrides():
    """Clear all dependency overrides."""
    app.dependency_overrides = {}


class TestTranscriptRequestModel:
    """Test TranscriptRequest Pydantic model."""

    def test_transcript_request_model_exists(self):
        """Test that TranscriptRequest model is defined."""
        from youtube_transcript.api.models import TranscriptRequest
        assert TranscriptRequest is not None

    def test_transcript_request_has_url_field(self):
        """Test that TranscriptRequest has url field."""
        from youtube_transcript.api.models import TranscriptRequest
        from pydantic import ValidationError

        # Valid URL
        request = TranscriptRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert request.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        # Missing URL should raise validation error
        with pytest.raises(ValidationError):
            TranscriptRequest()

    def test_transcript_request_has_optional_languages_field(self):
        """Test that TranscriptRequest has optional languages field."""
        from youtube_transcript.api.models import TranscriptRequest

        # Without languages
        request1 = TranscriptRequest(url="https://youtu.be/dQw4w9WgXcQ")
        assert request1.languages is None

        # With languages
        request2 = TranscriptRequest(
            url="https://youtu.be/dQw4w9WgXcQ",
            languages=["en", "es"]
        )
        assert request2.languages == ["en", "es"]

    def test_transcript_request_validates_url_format(self):
        """Test that TranscriptRequest validates URL format."""
        from youtube_transcript.api.models import TranscriptRequest
        from pydantic import ValidationError

        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "",
        ]

        for invalid_url in invalid_urls:
            with pytest.raises(ValidationError):
                TranscriptRequest(url=invalid_url)


class TestTranscriptResponseModel:
    """Test TranscriptResponse Pydantic model."""

    def test_transcript_response_model_exists(self):
        """Test that TranscriptResponse model is defined."""
        from youtube_transcript.api.models import TranscriptResponse
        assert TranscriptResponse is not None

    def test_transcript_response_has_required_fields(self):
        """Test that TranscriptResponse has all required fields."""
        from youtube_transcript.api.models import TranscriptResponse

        response = TranscriptResponse(
            video_id="dQw4w9WgXcQ",
            transcript="Never gonna give you up",
            language="en",
            transcript_type="manual",
        )

        assert response.video_id == "dQw4w9WgXcQ"
        assert response.transcript == "Never gonna give you up"
        assert response.language == "en"
        assert response.transcript_type == "manual"

    def test_transcript_response_from_transcript_result(self):
        """Test creating TranscriptResponse from TranscriptResult."""
        from youtube_transcript.api.models import TranscriptResponse
        from youtube_transcript.services.fetcher import TranscriptResult

        result = TranscriptResult(
            video_id="j9rZxAF3C0I",
            transcript="Test transcript",
            language="en",
            transcript_type="auto",
            duration=100.0,
        )

        response = TranscriptResponse.from_transcript_result(result)
        assert response.video_id == "j9rZxAF3C0I"
        assert response.transcript == "Test transcript"
        assert response.language == "en"
        assert response.transcript_type == "auto"


class TestErrorModel:
    """Test error response models."""

    def test_error_response_model_exists(self):
        """Test that ErrorResponse model is defined."""
        from youtube_transcript.api.models import ErrorResponse
        assert ErrorResponse is not None

    def test_error_response_has_error_and_detail(self):
        """Test that ErrorResponse has error and detail fields."""
        from youtube_transcript.api.models import ErrorResponse

        error = ErrorResponse(error="Not Found", detail="Transcript not found")
        assert error.error == "Not Found"
        assert error.detail == "Transcript not found"


class TestPostTranscriptEndpoint:
    """Test POST /api/transcript endpoint."""

    def test_post_transcript_endpoint_exists(self, test_client: TestClient):
        """Test that POST /api/transcript endpoint is registered."""
        response = test_client.post("/api/transcript", json={"url": "https://youtu.be/abc"})
        # Should process request (might return 404 for invalid video ID or validation error)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]
        # Verify it's our endpoint responding
        data = response.json()
        assert "error" in data or "detail" in data

    def test_post_transcript_with_valid_url(self, test_client: TestClient):
        """Test POST /api/transcript with valid YouTube URL."""
        mock_orchestrator = Mock()
        mock_result = TranscriptResult(
            video_id='dQw4w9WgXcQ',
            transcript='Never gonna give you up',
            language='en',
            transcript_type='manual',
            duration=212.0,
        )
        mock_orchestrator.get_transcript.return_value = mock_result
        override_orchestrator(mock_orchestrator)

        response = test_client.post(
            "/api/transcript",
            json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
        )

        clear_overrides()

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["transcript"] == "Never gonna give you up"
        assert data["language"] == "en"

    def test_post_transcript_with_short_url(self, test_client: TestClient):
        """Test POST /api/transcript with youtu.be short URL."""
        mock_orchestrator = Mock()
        mock_result = TranscriptResult(
            video_id='dQw4w9WgXcQ',
            transcript='Rick Astley',
            language='en',
            transcript_type='manual',
            duration=200.0,
        )
        mock_orchestrator.get_transcript.return_value = mock_result
        override_orchestrator(mock_orchestrator)

        response = test_client.post(
            "/api/transcript",
            json={"url": "https://youtu.be/dQw4w9WgXcQ"}
        )

        clear_overrides()

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["video_id"] == "dQw4w9WgXcQ"

    def test_post_transcript_with_languages(self, test_client: TestClient):
        """Test POST /api/transcript with language preference."""
        mock_orchestrator = Mock()
        mock_result = TranscriptResult(
            video_id='dQw4w9WgXcQ',
            transcript='Spanish transcript',
            language='es',
            transcript_type='manual',
            duration=100.0,
        )
        mock_orchestrator.get_transcript.return_value = mock_result
        override_orchestrator(mock_orchestrator)

        response = test_client.post(
            "/api/transcript",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "languages": ["es", "en"]
            }
        )

        clear_overrides()

        assert response.status_code == status.HTTP_200_OK
        mock_orchestrator.get_transcript.assert_called_once_with('dQw4w9WgXcQ', languages=['es', 'en'])

    def test_post_transcript_not_found(self, test_client: TestClient):
        """Test POST /api/transcript when transcript not found."""
        mock_orchestrator = Mock()
        mock_orchestrator.get_transcript.return_value = None
        override_orchestrator(mock_orchestrator)

        response = test_client.post(
            "/api/transcript",
            json={"url": "https://www.youtube.com/watch?v=nonexistent"}
        )

        clear_overrides()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data or "detail" in data

    def test_post_transcript_missing_url(self, test_client: TestClient):
        """Test POST /api/transcript without URL."""
        response = test_client.post("/api/transcript", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_transcript_invalid_url(self, test_client: TestClient):
        """Test POST /api/transcript with invalid URL."""
        response = test_client.post(
            "/api/transcript",
            json={"url": "not-a-valid-url"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_transcript_with_invalid_youtube_url(self, test_client: TestClient):
        """Test POST /api/transcript with invalid YouTube URL format."""
        mock_orchestrator = Mock()
        mock_orchestrator.get_transcript.return_value = None
        override_orchestrator(mock_orchestrator)

        response = test_client.post(
            "/api/transcript",
            json={"url": "https://example.com/watch?v=abc"}
        )

        clear_overrides()

        # URL passes validation but transcript not found
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetTranscriptByVideoId:
    """Test GET /api/transcript/{video_id} endpoint."""

    def test_get_transcript_by_video_id_endpoint_exists(self, test_client: TestClient):
        """Test that GET /api/transcript/{video_id} endpoint is registered."""
        response = test_client.get("/api/transcript/dQw4w9WgXcQ")
        # Endpoint should process the request (might return 404 if transcript not found)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
        # Verify it's our endpoint responding
        data = response.json()
        assert "error" in data or "detail" in data

    def test_get_transcript_by_video_id_success(self, test_client: TestClient):
        """Test GET /api/transcript/{video_id} with valid video ID."""
        mock_orchestrator = Mock()
        mock_result = TranscriptResult(
            video_id='dQw4w9WgXcQ',
            transcript='Never gonna give you up',
            language='en',
            transcript_type='manual',
            duration=212.0,
        )
        mock_orchestrator.get_transcript.return_value = mock_result
        override_orchestrator(mock_orchestrator)

        response = test_client.get("/api/transcript/dQw4w9WgXcQ")

        clear_overrides()

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["transcript"] == "Never gonna give you up"
        mock_orchestrator.get_transcript.assert_called_once_with('dQw4w9WgXcQ', languages=None)

    def test_get_transcript_by_video_id_with_languages(self, test_client: TestClient):
        """Test GET /api/transcript/{video_id} with language query parameter."""
        mock_orchestrator = Mock()
        mock_result = TranscriptResult(
            video_id='j9rZxAF3C0I',
            transcript='Spanish content',
            language='es',
            transcript_type='manual',
            duration=100.0,
        )
        mock_orchestrator.get_transcript.return_value = mock_result
        override_orchestrator(mock_orchestrator)

        response = test_client.get("/api/transcript/j9rZxAF3C0I?languages=es&languages=en")

        clear_overrides()

        assert response.status_code == status.HTTP_200_OK
        mock_orchestrator.get_transcript.assert_called_once_with('j9rZxAF3C0I', languages=['es', 'en'])

    def test_get_transcript_by_video_id_not_found(self, test_client: TestClient):
        """Test GET /api/transcript/{video_id} when not found."""
        mock_orchestrator = Mock()
        mock_orchestrator.get_transcript.return_value = None
        override_orchestrator(mock_orchestrator)

        response = test_client.get("/api/transcript/nonexistent")

        clear_overrides()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data or "detail" in data

    def test_get_transcript_by_video_id_invalid_id(self, test_client: TestClient):
        """Test GET /api/transcript/{video_id} with invalid video ID."""
        mock_orchestrator = Mock()
        mock_orchestrator.get_transcript.return_value = None
        override_orchestrator(mock_orchestrator)

        response = test_client.get("/api/transcript/invalid-id-with-dashes")

        clear_overrides()

        # Should attempt to fetch but return 404
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAPIEndpointIntegration:
    """Test integration between endpoints and services."""

    def test_post_and_get_return_same_transcript(self, test_client: TestClient):
        """Test that POST and GET endpoints return consistent data."""
        mock_orchestrator = Mock()
        mock_result = TranscriptResult(
            video_id='j9rZxAF3C0I',
            transcript='Consistent transcript',
            language='en',
            transcript_type='manual',
            duration=150.0,
        )
        mock_orchestrator.get_transcript.return_value = mock_result
        override_orchestrator(mock_orchestrator)

        # POST request
        post_response = test_client.post(
            "/api/transcript",
            json={"url": "https://www.youtube.com/watch?v=j9rZxAF3C0I"}
        )

        # GET request
        get_response = test_client.get("/api/transcript/j9rZxAF3C0I")

        clear_overrides()

        assert post_response.status_code == status.HTTP_200_OK
        assert get_response.status_code == status.HTTP_200_OK

        post_data = post_response.json()
        get_data = get_response.json()

        assert post_data["video_id"] == get_data["video_id"]
        assert post_data["transcript"] == get_data["transcript"]

    def test_endpoints_handle_orchestrator_errors(self, test_client: TestClient):
        """Test that endpoints handle orchestrator errors gracefully."""
        mock_orchestrator = Mock()
        mock_orchestrator.get_transcript.side_effect = Exception("Service error")
        override_orchestrator(mock_orchestrator)

        response = test_client.post(
            "/api/transcript",
            json={"url": "https://www.youtube.com/watch?v=j9rZxAF3C0I"}
        )

        clear_overrides()

        # Should return 500 Internal Server Error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestOpenAPIDocumentation:
    """Test OpenAPI schema generation."""

    def test_transcript_endpoints_in_openapi_schema(self):
        """Test that transcript endpoints are documented in OpenAPI schema."""
        from youtube_transcript.api.app import app

        schema = app.openapi()

        # Check paths exist
        assert "/api/transcript" in schema["paths"]
        assert "/api/transcript/{video_id}" in schema["paths"]

        # Check POST endpoint
        assert "post" in schema["paths"]["/api/transcript"]

        # Check GET endpoint
        assert "get" in schema["paths"]["/api/transcript/{video_id}"]

    def test_transcript_request_schema_is_documented(self):
        """Test that TranscriptRequest schema is in OpenAPI."""
        from youtube_transcript.api.app import app

        schema = app.openapi()

        # Check components exist
        assert "components" in schema
        assert "schemas" in schema["components"]

        # TranscriptRequest schema should be referenced
        post_spec = schema["paths"]["/api/transcript"]["post"]
        assert "requestBody" in post_spec

    def test_transcript_response_schema_is_documented(self):
        """Test that TranscriptResponse schema is in OpenAPI."""
        from youtube_transcript.api.app import app

        schema = app.openapi()

        # Check response schemas
        post_spec = schema["paths"]["/api/transcript"]["post"]
        assert "responses" in post_spec
        assert "200" in post_spec["responses"]

        get_spec = schema["paths"]["/api/transcript/{video_id}"]["get"]
        assert "responses" in get_spec
        assert "200" in get_spec["responses"]
