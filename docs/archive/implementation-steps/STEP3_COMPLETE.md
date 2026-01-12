# Step 3: Set Up Database Schema and ORM - COMPLETED

## Date: January 11, 2026

## Summary

Successfully implemented the Transcript database model using SQLModel, 
created database engine singleton, implemented init_db() function, and 
added get_session() dependency for FastAPI. All 11 model tests passing.

## What Was Accomplished

### 1. Created Transcript Model with SQLModel

**File**: `src/youtube_transcript/models/transcript.py`

**Model Fields**:
- `id: Optional[int]` - Primary key (auto-generated)
- `video_id: str` - YouTube video ID (unique, indexed, max 20 chars)
- `transcript_text: str` - Full transcript content (default: "")
- `language: str` - Language code (default: "en", max 10 chars)
- `transcript_type: str` - Type of transcript ("manual" or "auto", default: "auto")
- `created_at: datetime` - Creation timestamp (auto-set, UTC timezone)
- `updated_at: datetime` - Last update timestamp (auto-set, UTC timezone)
- `cache_key: Optional[str]` - Optional Redis cache key (max 100 chars)

**Features**:
- ✅ Unique constraint on video_id
- ✅ Index on video_id for fast lookups
- ✅ Automatic timestamp management
- ✅ Default values for language and transcript_type
- ✅ String representation (__repr__ and __str__)
- ✅ Timezone-aware datetime handling (UTC)
- ✅ Field validation (max_length constraints)

### 2. Created Database Engine and Functions

**File**: `src/youtube_transcript/models/database.py`

**Functions**:
- `engine` - SQLAlchemy engine singleton (SQLite)
- `init_db(session=None)` - Initialize database tables
- `get_session()` - FastAPI dependency for database sessions
- `get_engine()` - Get the database engine

**Features**:
- ✅ Engine singleton for application-wide use
- ✅ Thread-safe session creation
- ✅ Designed for FastAPI dependency injection
- ✅ Support for both in-memory (testing) and file-based (production) databases
- ✅ Automatic table creation with init_db()

### 3. Created Comprehensive Model Tests

**File**: `tests/test_models.py` (11 tests)

1. ✅ `test_transcript_model_can_be_created` - Model instantiation
2. ✅ `test_transcript_model_has_required_fields` - Field existence
3. ✅ `test_transcript_model_field_types` - Type validation
4. ✅ `test_transcript_model_timestamps_are_set` - Timestamp auto-generation
5. ✅ `test_transcript_model_default_values` - Default language
6. ✅ `test_transcript_model_can_be_saved_to_database` - Database CRUD
7. ✅ `test_transcript_model_video_id_is_unique` - Unique constraint
8. ✅ `test_transcript_model_string_representation` - __repr__/__str__
9. ✅ `test_transcript_model_long_transcript_text` - Long text handling
10. ✅ `test_transcript_model_empty_transcript` - Empty transcript handling
11. ✅ `test_transcript_model_special_characters` - Unicode/emoji support

### 4. Updated Test Infrastructure

**Modified**: `tests/conftest.py`

Updated `test_db` fixture to:
- Automatically create all tables using SQLModel.metadata.create_all()
- Support Transcript model (and future models)
- Provide fresh database for each test function

### 5. TDD Process Followed

✅ **Red Phase**: Wrote 11 failing tests first  
✅ **Green Phase**: Implemented Transcript model and database functions  
✅ **Refactor Phase**: Fixed deprecation warnings, improved code quality

## Test Results

**All tests passing**: 34/34 tests (11 new model tests + 23 existing)

```
============================== 34 passed in 0.56s ===============================
```

**No warnings** - All deprecation warnings fixed:
- ✅ Fixed `datetime.utcnow()` deprecation → `datetime.now(timezone.utc)`
- ✅ Fixed `session.query()` warning → `session.exec(select(...))`

## Code Quality Improvements

### 1. Timezone-Aware Datetimes

```python
# Before (deprecated)
created_at: datetime = Field(default_factory=datetime.utcnow)

# After (timezone-aware)
created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 2. SQLModel Query Style

```python
# Before (SQLAlchemy style, not recommended)
retrieved = session.query(Transcript).filter(Transcript.video_id == "test123").first()

# After (SQLModel style, recommended)
statement = select(Transcript).where(Transcript.video_id == "test123")
retrieved = session.exec(statement).first()
```

## Model Verification

**Import Test**:
```bash
$ python -c "from youtube_transcript.models import Transcript, init_db, get_session"
✓ Transcript model imported
✓ Database functions imported
Transcript table: transcripts
```

**Field Validation**:
```
Transcript Model Fields:
==================================================
id: Union[int, None] (primary key, auto-generated)
video_id: str (required, unique, indexed, max_length=20)
transcript_text: str (default="")
language: str (default="en", max_length=10)
transcript_type: str (default="auto", max_length=10)
created_at: datetime (auto-set, UTC timezone)
updated_at: datetime (auto-set, UTC timezone)
cache_key: Optional[str] (max_length=100)
```

## Usage Examples

### Creating a Transcript

```python
from youtube_transcript.models import Transcript

transcript = Transcript(
    video_id="dQw4w9WgXcQ",
    transcript_text="Never gonna give you up...",
    language="en",
    transcript_type="manual",
)
```

### Saving to Database

```python
from youtube_transcript.models import Transcript, get_session
from sqlmodel import select

# Get session (typically used as FastAPI dependency)
with get_session() as session:
    # Create transcript
    transcript = Transcript(video_id="abc", transcript_text="Hello")
    session.add(transcript)
    session.commit()
    session.refresh(transcript)
    
    # Retrieve transcript
    statement = select(Transcript).where(Transcript.video_id == "abc")
    result = session.exec(statement).first()
    print(result.video_id)  # "abc"
```

### Initializing Database

```python
from youtube_transcript.models import init_db

# Create all tables
init_db()
```

### Using with FastAPI (Future - Step 9)

```python
from fastapi import Depends
from sqlmodel import Session
from youtube_transcript.models import get_session, Transcript

@app.get("/transcripts/{video_id}")
def get_transcript(
    video_id: str,
    session: Session = Depends(get_session)
):
    statement = select(Transcript).where(Transcript.video_id == video_id)
    transcript = session.exec(statement).first()
    return transcript
```

## Database Schema

**Table**: `transcripts`

```sql
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(20) UNIQUE NOT NULL,
    transcript_text TEXT NOT NULL DEFAULT '',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    transcript_type VARCHAR(10) NOT NULL DEFAULT 'auto',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    cache_key VARCHAR(100)
);

CREATE INDEX ix_transcripts_video_id ON transcripts(video_id);
```

## Constraints and Validation

1. **Unique Constraint**: video_id must be unique (prevents duplicate transcripts)
2. **Index**: video_id is indexed for fast lookups
3. **Max Length Constraints**:
   - video_id: 20 characters (YouTube IDs are typically 11 chars)
   - language: 10 characters (ISO 639-1 codes are 2-3 chars)
   - transcript_type: 10 characters ("manual" or "auto")
   - cache_key: 100 characters

## Files Created/Modified

### New Files
- `src/youtube_transcript/models/transcript.py` - Transcript model
- `src/youtube_transcript/models/database.py` - Database engine and functions
- `tests/test_models.py` - Model tests (11 tests)

### Modified Files
- `src/youtube_transcript/models/__init__.py` - Export model and functions
- `tests/conftest.py` - Updated test_db fixture

### Project Structure
```
src/youtube_transcript/models/
├── __init__.py              # Exports: Transcript, init_db, get_session, get_engine
├── transcript.py             # Transcript model (SQLModel)
└── database.py               # Database engine and functions
```

## Dependencies

No new dependencies added - using existing:
- `sqlmodel >= 0.0.22` - ORM and models
- `sqlite3` (built-in) - Database

## Next Steps

Proceed to **Step 4: Implement YouTube URL Parser**

This will include:
- Create extract_video_id() function
- Support all 100+ YouTube URL formats
- Handle edge cases (missing protocol, extra params, etc.)
- Write URL parser tests (TDD)

## Acceptance Criteria Met

✅ Transcript model has all required fields  
✅ video_id has unique constraint  
✅ Model is Pydantic-compatible (for FastAPI)  
✅ Database tables can be created successfully  
✅ Model can be saved and retrieved from database  
✅ All 11 model tests pass  
✅ No deprecation warnings  
✅ Database engine singleton created  
✅ init_db() function implemented  
✅ get_session() dependency ready for FastAPI  
✅ Total: 34/34 tests passing (23 + 11 new)  

## Stop/Go Decision

**✅ GO** - Proceed to Step 4

The Transcript model is complete, well-tested, and ready for use.
The database infrastructure is in place for the repository layer.
