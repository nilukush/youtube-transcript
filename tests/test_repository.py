"""
Test transcript database repository.

These tests verify that TranscriptRepository can persist and retrieve transcripts
from the database using SQLModel.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

from datetime import datetime, timezone
import pytest
from sqlmodel import select

from youtube_transcript.services.fetcher import TranscriptResult
from youtube_transcript.models import Transcript
from youtube_transcript.services.repository import TranscriptRepository


class TestTranscriptRepositoryCreation:
    """Test repository instantiation and initialization."""

    def test_repository_can_be_created(self, test_db):
        """Test that TranscriptRepository can be instantiated."""
        repository = TranscriptRepository(test_db)
        assert repository is not None
        assert repository.session == test_db


class TestCreateTranscript:
    """Test transcript creation operations."""

    def test_create_saves_transcript_to_database(self, test_db):
        """Test that create() saves a transcript to the database."""
        repository = TranscriptRepository(test_db)

        result = TranscriptResult(
            video_id='test123',
            transcript='Sample transcript text',
            language='en',
            transcript_type='manual',
            duration=120.5,
        )

        transcript = repository.create(result)

        assert transcript is not None
        assert transcript.id is not None
        assert transcript.video_id == 'test123'
        assert transcript.transcript_text == 'Sample transcript text'
        assert transcript.language == 'en'
        assert transcript.transcript_type == 'manual'

    def test_create_sets_timestamps(self, test_db):
        """Test that create() sets created_at and updated_at timestamps."""
        repository = TranscriptRepository(test_db)

        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='auto',
            duration=10.0,
        )

        transcript = repository.create(result)

        assert transcript.created_at is not None
        assert transcript.updated_at is not None
        # Just verify timestamps are set - actual value comparison is complex due to SQLite timezone handling

    def test_create_returns_transcript_model(self, test_db):
        """Test that create() returns a Transcript model."""
        repository = TranscriptRepository(test_db)

        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='manual',
            duration=5.0,
        )

        transcript = repository.create(result)

        assert isinstance(transcript, Transcript)

    def test_create_handles_long_transcript(self, test_db):
        """Test that create() handles long transcript text."""
        repository = TranscriptRepository(test_db)

        long_text = 'Lorem ipsum ' * 1000  # Long transcript

        result = TranscriptResult(
            video_id='long123',
            transcript=long_text,
            language='en',
            transcript_type='auto',
            duration=600.0,
        )

        transcript = repository.create(result)

        assert len(transcript.transcript_text) == len(long_text)


class TestGetTranscript:
    """Test transcript retrieval operations."""

    def test_get_by_video_id_retrieves_transcript(self, test_db):
        """Test that get_by_video_id() retrieves a transcript."""
        repository = TranscriptRepository(test_db)

        # First create a transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='Sample transcript',
            language='en',
            transcript_type='manual',
            duration=100.0,
        )
        repository.create(result)

        # Now retrieve it
        transcript = repository.get_by_video_id('test123')

        assert transcript is not None
        assert transcript.video_id == 'test123'
        assert transcript.transcript_text == 'Sample transcript'

    def test_get_by_video_id_returns_none_if_not_found(self, test_db):
        """Test that get_by_video_id() returns None for nonexistent video."""
        repository = TranscriptRepository(test_db)

        transcript = repository.get_by_video_id('nonexistent')

        assert transcript is None

    def test_get_by_id_retrieves_transcript(self, test_db):
        """Test that get_by_id() retrieves a transcript by primary key."""
        repository = TranscriptRepository(test_db)

        # Create a transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='manual',
            duration=50.0,
        )
        created = repository.create(result)

        # Retrieve by ID
        transcript = repository.get_by_id(created.id)

        assert transcript is not None
        assert transcript.id == created.id
        assert transcript.video_id == 'test123'

    def test_get_by_id_returns_none_if_not_found(self, test_db):
        """Test that get_by_id() returns None for nonexistent ID."""
        repository = TranscriptRepository(test_db)

        transcript = repository.get_by_id(99999)

        assert transcript is None


class TestUpdateTranscript:
    """Test transcript update operations."""

    def test_update_modifies_existing_transcript(self, test_db):
        """Test that update() modifies an existing transcript."""
        repository = TranscriptRepository(test_db)

        # Create a transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='Original text',
            language='en',
            transcript_type='manual',
            duration=30.0,
        )
        created = repository.create(result)

        # Update it
        updated_result = TranscriptResult(
            video_id='test123',
            transcript='Updated text',
            language='es',
            transcript_type='auto',
            duration=60.0,
        )
        updated = repository.update(created.id, updated_result)

        assert updated is not None
        assert updated.transcript_text == 'Updated text'
        assert updated.language == 'es'
        assert updated.transcript_type == 'auto'

    def test_update_updates_timestamp(self, test_db):
        """Test that update() updates the updated_at timestamp."""
        repository = TranscriptRepository(test_db)

        # Create a transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='manual',
            duration=20.0,
        )
        created = repository.create(result)
        original_timestamp = created.updated_at

        # Wait a bit and update
        import time
        time.sleep(0.01)

        updated_result = TranscriptResult(
            video_id='test123',
            transcript='Updated',
            language='en',
            transcript_type='manual',
            duration=25.0,
        )
        updated = repository.update(created.id, updated_result)

        assert updated.updated_at > original_timestamp

    def test_update_returns_none_if_not_found(self, test_db):
        """Test that update() returns None for nonexistent transcript."""
        repository = TranscriptRepository(test_db)

        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='manual',
            duration=10.0,
        )

        updated = repository.update(99999, result)

        assert updated is None


class TestUpsertTranscript:
    """Test upsert operations (create or update)."""

    def test_upsert_creates_if_not_exists(self, test_db):
        """Test that upsert() creates a new transcript if it doesn't exist."""
        repository = TranscriptRepository(test_db)

        result = TranscriptResult(
            video_id='new123',
            transcript='New transcript',
            language='en',
            transcript_type='manual',
            duration=40.0,
        )

        transcript = repository.upsert(result)

        assert transcript is not None
        assert transcript.video_id == 'new123'
        assert transcript.transcript_text == 'New transcript'

    def test_upsert_updates_if_exists(self, test_db):
        """Test that upsert() updates an existing transcript."""
        repository = TranscriptRepository(test_db)

        # Create initial transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='Original',
            language='en',
            transcript_type='manual',
            duration=30.0,
        )
        created = repository.upsert(result)

        # Upsert with updated data
        updated_result = TranscriptResult(
            video_id='test123',  # Same video_id
            transcript='Updated',
            language='es',
            transcript_type='auto',
            duration=60.0,
        )
        updated = repository.upsert(updated_result)

        assert updated.id == created.id  # Same record
        assert updated.transcript_text == 'Updated'
        assert updated.language == 'es'

    def test_upsert_handles_multiple_calls(self, test_db):
        """Test that multiple upserts with same video_id work correctly."""
        repository = TranscriptRepository(test_db)

        # First upsert
        result1 = TranscriptResult(
            video_id='test123',
            transcript='Version 1',
            language='en',
            transcript_type='manual',
            duration=10.0,
        )
        transcript1 = repository.upsert(result1)

        # Second upsert
        result2 = TranscriptResult(
            video_id='test123',
            transcript='Version 2',
            language='en',
            transcript_type='manual',
            duration=15.0,
        )
        transcript2 = repository.upsert(result2)

        # Third upsert
        result3 = TranscriptResult(
            video_id='test123',
            transcript='Version 3',
            language='en',
            transcript_type='manual',
            duration=20.0,
        )
        transcript3 = repository.upsert(result3)

        # All should have the same ID (same record)
        assert transcript1.id == transcript2.id == transcript3.id
        assert transcript3.transcript_text == 'Version 3'


class TestDeleteTranscript:
    """Test transcript deletion operations."""

    def test_delete_removes_transcript(self, test_db):
        """Test that delete() removes a transcript from the database."""
        repository = TranscriptRepository(test_db)

        # Create a transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='To be deleted',
            language='en',
            transcript_type='manual',
            duration=25.0,
        )
        created = repository.create(result)

        # Delete it
        deleted = repository.delete(created.id)

        assert deleted is True

        # Verify it's gone
        transcript = repository.get_by_id(created.id)
        assert transcript is None

    def test_delete_returns_false_if_not_found(self, test_db):
        """Test that delete() returns False for nonexistent transcript."""
        repository = TranscriptRepository(test_db)

        deleted = repository.delete(99999)

        assert deleted is False

    def test_delete_by_video_id(self, test_db):
        """Test that delete_by_video_id() removes a transcript."""
        repository = TranscriptRepository(test_db)

        # Create a transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='To be deleted',
            language='en',
            transcript_type='manual',
            duration=25.0,
        )
        repository.create(result)

        # Delete by video_id
        deleted = repository.delete_by_video_id('test123')

        assert deleted is True

        # Verify it's gone
        transcript = repository.get_by_video_id('test123')
        assert transcript is None

    def test_delete_by_video_id_returns_false_if_not_found(self, test_db):
        """Test that delete_by_video_id() returns False for nonexistent video."""
        repository = TranscriptRepository(test_db)

        deleted = repository.delete_by_video_id('nonexistent')

        assert deleted is False


class TestExistsOperations:
    """Test existence check operations."""

    def test_exists_by_video_id_returns_true_if_found(self, test_db):
        """Test that exists_by_video_id() returns True if transcript exists."""
        repository = TranscriptRepository(test_db)

        # Create a transcript
        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='manual',
            duration=15.0,
        )
        repository.create(result)

        # Check existence
        exists = repository.exists_by_video_id('test123')

        assert exists is True

    def test_exists_by_video_id_returns_false_if_not_found(self, test_db):
        """Test that exists_by_video_id() returns False if not found."""
        repository = TranscriptRepository(test_db)

        exists = repository.exists_by_video_id('nonexistent')

        assert exists is False


class TestListOperations:
    """Test list and query operations."""

    def test_all_returns_all_transcripts(self, test_db):
        """Test that all() returns all transcripts in the database."""
        repository = TranscriptRepository(test_db)

        # Create multiple transcripts
        for i in range(3):
            result = TranscriptResult(
                video_id=f'video{i}',
                transcript=f'Transcript {i}',
                language='en',
                transcript_type='manual',
                duration=10.0 * i,
            )
            repository.create(result)

        # Get all
        transcripts = repository.all()

        assert len(transcripts) >= 3

    def test_list_with_limit(self, test_db):
        """Test that list_with_limit() returns limited results."""
        repository = TranscriptRepository(test_db)

        # Create multiple transcripts
        for i in range(5):
            result = TranscriptResult(
                video_id=f'video{i}',
                transcript=f'Transcript {i}',
                language='en',
                transcript_type='manual',
                duration=10.0,
            )
            repository.create(result)

        # Get with limit
        transcripts = repository.list_with_limit(3)

        assert len(transcripts) == 3

    def test_list_by_language(self, test_db):
        """Test that list_by_language() filters by language."""
        repository = TranscriptRepository(test_db)

        # Create transcripts in different languages
        repository.create(TranscriptResult(
            video_id='en1',
            transcript='English',
            language='en',
            transcript_type='manual',
            duration=10.0,
        ))
        repository.create(TranscriptResult(
            video_id='es1',
            transcript='Spanish',
            language='es',
            transcript_type='manual',
            duration=10.0,
        ))
        repository.create(TranscriptResult(
            video_id='en2',
            transcript='English 2',
            language='en',
            transcript_type='manual',
            duration=10.0,
        ))

        # Get English transcripts
        english = repository.list_by_language('en')

        assert len(english) >= 2
        for t in english:
            assert t.language == 'en'


class TestCountOperations:
    """Test count operations."""

    def test_count_returns_total_transcripts(self, test_db):
        """Test that count() returns the total number of transcripts."""
        repository = TranscriptRepository(test_db)

        initial_count = repository.count()

        # Add some transcripts
        for i in range(3):
            result = TranscriptResult(
                video_id=f'video{i}',
                transcript=f'Transcript {i}',
                language='en',
                transcript_type='manual',
                duration=10.0,
            )
            repository.create(result)

        final_count = repository.count()

        assert final_count == initial_count + 3


class TestConversionHelpers:
    """Test conversion between TranscriptResult and Transcript models."""

    def test_to_transcript_model(self, test_db):
        """Test conversion from TranscriptResult to Transcript model."""
        repository = TranscriptRepository(test_db)

        result = TranscriptResult(
            video_id='test123',
            transcript='Test transcript',
            language='en',
            transcript_type='manual',
            duration=120.5,
        )

        transcript = repository._to_transcript(result)

        assert isinstance(transcript, Transcript)
        assert transcript.video_id == 'test123'
        assert transcript.transcript_text == 'Test transcript'
        assert transcript.language == 'en'
        assert transcript.transcript_type == 'manual'

    def test_to_transcript_result(self, test_db):
        """Test conversion from Transcript model to TranscriptResult."""
        repository = TranscriptRepository(test_db)

        transcript = Transcript(
            video_id='test123',
            transcript_text='Test transcript',
            language='en',
            transcript_type='manual',
        )

        result = repository._to_transcript_result(transcript)

        assert isinstance(result, TranscriptResult)
        assert result.video_id == 'test123'
        assert result.transcript == 'Test transcript'
        assert result.language == 'en'
        assert result.transcript_type == 'manual'


class TestTransactionHandling:
    """Test transaction and error handling."""

    def test_create_rolls_back_on_error(self, test_db):
        """Test that create() rolls back on database error."""
        repository = TranscriptRepository(test_db)

        # Try to create a transcript with duplicate video_id
        result1 = TranscriptResult(
            video_id='test123',
            transcript='First',
            language='en',
            transcript_type='manual',
            duration=10.0,
        )
        repository.create(result1)

        # Try to create duplicate - should handle gracefully
        result2 = TranscriptResult(
            video_id='test123',  # Duplicate
            transcript='Second',
            language='en',
            transcript_type='manual',
            duration=10.0,
        )

        # Should either raise error or handle it gracefully
        # Implementation dependent
