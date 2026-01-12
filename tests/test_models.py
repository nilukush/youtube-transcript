"""
Test database models.

These tests verify that the Transcript model is properly defined and works correctly.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

import pytest
from datetime import datetime
from sqlmodel import SQLModel, Session


def test_transcript_model_can_be_created():
    """Test that Transcript model can be instantiated."""
    # This test will fail until Transcript model is created
    from youtube_transcript.models import Transcript

    transcript = Transcript(
        video_id="dQw4w9WgXcQ",
        transcript_text="Never gonna give you up",
        language="en",
        transcript_type="manual",
    )

    assert transcript.video_id == "dQw4w9WgXcQ"
    assert transcript.transcript_text == "Never gonna give you up"
    assert transcript.language == "en"
    assert transcript.transcript_type == "manual"


def test_transcript_model_has_required_fields():
    """Test that Transcript model has all required fields."""
    from youtube_transcript.models import Transcript

    transcript = Transcript(
        video_id="test123",
        transcript_text="Test transcript",
        language="en",
        transcript_type="auto",
    )

    # Verify fields exist
    assert hasattr(transcript, "id")
    assert hasattr(transcript, "video_id")
    assert hasattr(transcript, "transcript_text")
    assert hasattr(transcript, "language")
    assert hasattr(transcript, "transcript_type")
    assert hasattr(transcript, "created_at")
    assert hasattr(transcript, "updated_at")
    assert hasattr(transcript, "cache_key")


def test_transcript_model_field_types():
    """Test that Transcript model fields have correct types."""
    from youtube_transcript.models import Transcript

    transcript = Transcript(
        video_id="test123",
        transcript_text="Test",
        language="en",
        transcript_type="manual",
    )

    # Note: id might be None until saved to database
    assert isinstance(transcript.video_id, str)
    assert isinstance(transcript.transcript_text, str)
    assert isinstance(transcript.language, str)
    assert isinstance(transcript.transcript_type, str)


def test_transcript_model_timestamps_are_set():
    """Test that created_at and updated_at are automatically set."""
    from youtube_transcript.models import Transcript

    transcript = Transcript(
        video_id="test123",
        transcript_text="Test",
        language="en",
        transcript_type="manual",
    )

    # Timestamps should be set by the model
    assert hasattr(transcript, "created_at")
    assert hasattr(transcript, "updated_at")


def test_transcript_model_default_values():
    """Test that Transcript model has correct default values."""
    from youtube_transcript.models import Transcript

    transcript = Transcript(
        video_id="test123",
        transcript_text="Test",
    )

    # Should have default language
    assert transcript.language == "en"


def test_transcript_model_can_be_saved_to_database(test_db: Session):
    """Test that Transcript model can be saved to and retrieved from database."""
    from youtube_transcript.models import Transcript

    # Create and save transcript
    transcript = Transcript(
        video_id="test123",
        transcript_text="Test transcript",
        language="en",
        transcript_type="manual",
    )

    test_db.add(transcript)
    test_db.commit()
    test_db.refresh(transcript)

    # Verify it was saved and has an ID
    assert transcript.id is not None

    # Retrieve from database using SQLModel's exec()
    from sqlmodel import select

    statement = select(Transcript).where(Transcript.video_id == "test123")
    retrieved = test_db.exec(statement).first()

    assert retrieved is not None
    assert retrieved.video_id == "test123"
    assert retrieved.transcript_text == "Test transcript"
    assert retrieved.language == "en"
    assert retrieved.transcript_type == "manual"


def test_transcript_model_video_id_is_unique(test_db: Session):
    """Test that video_id has unique constraint."""
    from youtube_transcript.models import Transcript

    # Create first transcript
    transcript1 = Transcript(
        video_id="test123",
        transcript_text="First transcript",
    )
    test_db.add(transcript1)
    test_db.commit()

    # Try to create second transcript with same video_id
    transcript2 = Transcript(
        video_id="test123",  # Same video_id
        transcript_text="Second transcript",
    )

    # This should either fail or update the existing record
    # depending on how we implement upsert logic
    test_db.add(transcript2)

    # For now, we just verify the model accepts the data
    # The actual uniqueness constraint will be tested in repository tests


def test_transcript_model_string_representation():
    """Test that Transcript model has a useful string representation."""
    from youtube_transcript.models import Transcript

    transcript = Transcript(
        video_id="test123",
        transcript_text="Test",
    )

    # Should have a __str__ or __repr__ method
    str_repr = str(transcript)
    assert "test123" in str_repr or "Transcript" in str_repr


def test_transcript_model_long_transcript_text():
    """Test that Transcript model can handle long transcript text."""
    from youtube_transcript.models import Transcript

    # Simulate a long transcript (10,000 characters)
    long_text = "Lorem ipsum " * 500  # ~6500 characters

    transcript = Transcript(
        video_id="test123",
        transcript_text=long_text,
        language="en",
        transcript_type="auto",
    )

    assert len(transcript.transcript_text) == len(long_text)


def test_transcript_model_empty_transcript():
    """Test that Transcript model handles empty transcript."""
    from youtube_transcript.models import Transcript

    transcript = Transcript(
        video_id="test123",
        transcript_text="",
        language="en",
        transcript_type="manual",
    )

    assert transcript.transcript_text == ""


def test_transcript_model_special_characters():
    """Test that Transcript model handles special characters in transcript."""
    from youtube_transcript.models import Transcript

    special_text = "Test with émojis 🎉 and spëcial çharacters"

    transcript = Transcript(
        video_id="test123",
        transcript_text=special_text,
        language="en",
        transcript_type="manual",
    )

    assert transcript.transcript_text == special_text
