"""YouTube transcript fetcher service."""

from typing import Optional
from dataclasses import dataclass

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    VideoUnavailable,
    NoTranscriptFound,
    YouTubeTranscriptApiException,
)


@dataclass
class TranscriptResult:
    """
    Result of fetching a YouTube transcript.

    Attributes:
        video_id: YouTube video ID
        transcript: Full transcript text (all segments concatenated)
        language: Language code of the transcript
        transcript_type: Type of transcript ('manual' or 'auto')
        duration: Total duration in seconds
    """

    video_id: str
    transcript: str
    language: str
    transcript_type: str
    duration: float

    def __repr__(self) -> str:
        return f"TranscriptResult(video_id='{self.video_id}', language='{self.language}', type='{self.transcript_type}')"


class TranscriptFetchError(Exception):
    """Exception raised when transcript fetching fails."""

    pass


class TranscriptUnavailableError(Exception):
    """Exception raised when transcript is not available for a video."""

    pass


class VideoUnavailableError(Exception):
    """Exception raised when a video is unavailable (private, deleted, etc.)."""

    pass


class YouTubeTranscriptFetcher:
    """
    Fetch transcripts from YouTube videos.

    This service uses the youtube-transcript-api library to fetch transcripts
    from YouTube videos. It handles various error conditions and returns
    structured transcript data.

    Attributes:
        api: YouTubeTranscriptAPI instance

    Example:
        >>> fetcher = YouTubeTranscriptFetcher()
        >>> result = fetcher.fetch_transcript('dQw4w9WgXcQ')
        >>> print(result.transcript)
        'Never gonna give you up...'
    """

    def __init__(self, proxy_config=None):
        """
        Initialize the fetcher with a YouTube transcript API instance.

        Args:
            proxy_config: Optional proxy configuration (WebshareProxyConfig or GenericProxyConfig)
                        If provided, all API requests will be routed through the proxy.
                        Use get_proxy_config() to load from environment variables.

        Example:
            >>> # Without proxy
            >>> fetcher = YouTubeTranscriptFetcher()
            >>>
            >>> # With proxy from environment
            >>> from youtube_transcript.config import get_proxy_config
            >>> fetcher = YouTubeTranscriptFetcher(proxy_config=get_proxy_config())
        """
        if proxy_config is not None:
            self.api = YouTubeTranscriptApi(proxy_config=proxy_config)
        else:
            self.api = YouTubeTranscriptApi()

    def fetch_transcript(
        self,
        video_id: str,
        languages: Optional[list[str]] = None,
    ) -> Optional[TranscriptResult]:
        """
        Fetch transcript for a YouTube video.

        This method attempts to fetch the transcript for the given video ID.
        It returns None if no transcript is available.

        Args:
            video_id: YouTube video ID (11 characters)
            languages: Optional list of language codes to try (e.g., ['en', 'es'])

        Returns:
            TranscriptResult if transcript is available, None otherwise

        Raises:
            TranscriptFetchError: If fetching fails for reasons other than
                transcript unavailability (network errors, etc.)

        Example:
            >>> fetcher = YouTubeTranscriptFetcher()
            >>> result = fetcher.fetch_transcript('dQw4w9WgXcQ')
            >>> print(result.transcript)
            'Never gonna give you up...'
        """
        try:
            # Fetch transcript data from YouTube using new API (v1.0+)
            fetched = self.api.fetch(video_id, languages=languages or ('en',))

            if not fetched or not fetched.snippets:
                return None

            # Extract snippets from FetchedTranscript object
            transcript_list = fetched.snippets

            # Parse transcript data
            transcript_text = self._concatenate_transcript(transcript_list)
            language = self._extract_language_from_fetched(fetched)
            transcript_type = self._determine_transcript_type_from_fetched(fetched)
            duration = self._calculate_duration(transcript_list)

            return TranscriptResult(
                video_id=video_id,
                transcript=transcript_text,
                language=language,
                transcript_type=transcript_type,
                duration=duration,
            )

        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
            # These are expected cases - video just doesn't have a transcript
            return None

        except YouTubeTranscriptApiException as e:
            # This can include rate limiting, request blocked, etc. - handle gracefully
            return None

        except Exception as e:
            # Unexpected error - wrap in our custom exception
            raise TranscriptFetchError(
                f"Failed to fetch transcript for video '{video_id}': {str(e)}"
            ) from e

    def _concatenate_transcript(self, transcript_list: list) -> str:
        """
        Concatenate transcript segments into full text.

        Args:
            transcript_list: List of transcript segments from YouTube API

        Returns:
            Concatenated transcript text with spaces between segments
        """
        segments = [segment.text for segment in transcript_list]
        return ' '.join(segments)

    def _extract_language(self, transcript_list: list) -> str:
        """
        Extract language from transcript data.

        Args:
            transcript_list: List of transcript segments

        Returns:
            Language code (default: 'en' if not found)
        """
        if transcript_list and hasattr(transcript_list[0], 'language'):
            return transcript_list[0].language
        return 'en'

    def _extract_language_from_fetched(self, fetched) -> str:
        """
        Extract language from FetchedTranscript object.

        Args:
            fetched: FetchedTranscript object from new API

        Returns:
            Language code (default: 'en' if not found)
        """
        if hasattr(fetched, 'language_code'):
            return fetched.language_code
        return 'en'

    def _determine_transcript_type(self, transcript_list: list) -> str:
        """
        Determine if transcript is manual or auto-generated.

        Args:
            transcript_list: List of transcript segments

        Returns:
            'manual' or 'auto'
        """
        if transcript_list and hasattr(transcript_list[0], 'generated'):
            is_generated = transcript_list[0].generated
            return 'auto' if is_generated else 'manual'
        return 'auto'  # Default to auto if we can't determine

    def _determine_transcript_type_from_fetched(self, fetched) -> str:
        """
        Determine if transcript is manual or auto-generated from FetchedTranscript.

        Args:
            fetched: FetchedTranscript object from new API

        Returns:
            'manual' or 'auto'
        """
        if hasattr(fetched, 'is_generated'):
            return 'auto' if fetched.is_generated else 'manual'
        return 'auto'  # Default to auto if we can't determine

    def _calculate_duration(self, transcript_list: list) -> float:
        """
        Calculate total duration of transcript.

        Args:
            transcript_list: List of transcript segments

        Returns:
            Total duration in seconds
        """
        total_duration = 0.0
        for segment in transcript_list:
            if hasattr(segment, 'duration') and segment.duration:
                total_duration += segment.duration
        return total_duration
