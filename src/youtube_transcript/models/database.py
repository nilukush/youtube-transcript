"""Database engine and initialization."""

from sqlmodel import SQLModel, Session, create_engine, select
from youtube_transcript.models.transcript import Transcript

# Database URL (can be overridden by environment variable)
# Default: SQLite in-memory for testing, file-based for production
DATABASE_URL = "sqlite:///youtube_transcripts.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db(session: Session | None = None) -> None:
    """
    Initialize database tables.

    This function creates all tables defined in SQLModel metadata.
    If a session is provided, it will be used for table creation.
    Otherwise, a new connection will be created.

    Args:
        session: Optional SQLModel Session for table creation

    Example:
        >>> from youtube_transcript.models import init_db
        >>> init_db()  # Create all tables
    """
    # Create all tables
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    Get a database session.

    This function is designed to be used as a FastAPI dependency.
    It provides a new database session for each request.

    Yields:
        Session: SQLModel Session for database operations

    Example:
        >>> from fastapi import Depends
        >>> from youtube_transcript.models import get_session
        >>>
        >>> @app.get("/transcripts")
        >>> def get_transcripts(session: Session = Depends(get_session)):
        >>>     transcripts = session.exec(select(Transcript)).all()
        >>>     return transcripts
    """
    with Session(engine) as session:
        yield session


def get_engine():
    """
    Get the database engine.

    Returns:
        Engine: SQLAlchemy engine instance

    Example:
        >>> from youtube_transcript.models.database import get_engine
        >>> engine = get_engine()
    """
    return engine
