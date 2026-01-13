# Contributing to YouTube Transcript Fetcher

Thank you for your interest in contributing to YouTube Transcript Fetcher! This project is in **maintenance mode**, meaning all core features are complete and we're focused on bug fixes, improvements, and documentation.

## Project Status

- **Implementation**: ✅ Complete
- **Production**: 🟢 Live at https://youtube-transcript-zb5k.onrender.com
- **Tests**: ✅ 280 passing (74% coverage)
- **Mode**: Maintenance (bug fixes, documentation, optimization)

---

## Development Setup

### Prerequisites

- **Python**: 3.10 or higher
- **Git**: For cloning and version control
- **GitHub account**: For forks and pull requests

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork locally
git clone https://github.com/YOUR_USERNAME/youtube-transcript.git
cd youtube-transcript
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Development Dependencies

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
ytt --version
pytest --version
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=youtube_transcript --cov-report=html

# Run specific test file
pytest tests/test_cli.py
```

### 5. Run Development Server

```bash
# Without proxy (local testing)
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888

# With proxy (production-like testing)
export WEBSHARE_PROXY_USERNAME="your_username"
export WEBSHARE_PROXY_PASSWORD="your_password"
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888
```

**Note**: Use non-standard ports (e.g., 8888) to avoid conflicts.

---

## Code Standards

### Python Style

- **Type Hints**: Required for all functions (PEP 484)
- **Line Length**: 100 characters (configured in pyproject.toml)
- **Formatting**: Code should be clean and readable
- **Import Order**: Standard library, third-party, local

### Testing Standards

- **Coverage Goal**: Maintain 74%+ test coverage
- **Test Framework**: pytest
- **TDD Methodology**: Write tests before code when possible
- **Test Types**:
  - Unit tests for individual functions
  - Integration tests for service interactions
  - End-to-end tests for critical user flows

### Code Quality

- **Docstrings**: Google-style docstrings for functions
- **Error Handling**: Explicit exception handling with clear messages
- **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- **No Hardcoded Values**: Use environment variables for configuration

---

## Development Workflow

### 1. Create a Branch

```bash
# From main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write code following project standards
- Add tests for new functionality
- Update documentation if needed
- Run tests locally

```bash
# Run linting (if configured)
ruff check src/
black src/

# Run tests
pytest
```

### 3. Commit Changes

Follow conventional commit format:

```bash
# Features
git commit -m "feat: add support for YouTube shorts"

# Bug fixes
git commit -m "fix: handle timeout when transcript not available"

# Documentation
git commit -m "docs: update deployment guide with Render instructions"

# Refactoring
git commit -m "refactor: simplify proxy configuration logic"

# Tests
git commit -m "test: add regression test for language preference"
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Link to related issues if applicable
```

---

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass (280 tests)
- [ ] Test coverage maintained at 74%+
- [ ] Code follows project style standards
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventional format
- [ ] PR description clearly explains changes

### Pull Request Template

When creating a PR, include:

**Description**
- What does this PR do?
- Why is it needed?
- How does it solve the problem?

**Type of Change**
- [ ] Bug fix
- [ ] Feature
- [ ] Refactoring
- [ ] Documentation
- [ ] Tests
- [ ] Other (please describe)

**Testing**
- How did you test these changes?
- What test scenarios were covered?

**Checklist**
- [ ] Tests pass locally
- [ ] No new warnings introduced
- [ ] Documentation updated
- [ ] Backward compatibility maintained (if applicable)

**Related Issues**
- Closes #(issue number)
- Relates to #(issue number)

---

## Project Structure

```
youtube-transcript/
├── src/youtube_transcript/
│   ├── api/              # FastAPI endpoints & web routes
│   ├── cache/            # Redis caching service
│   ├── config/           # Proxy configuration
│   ├── models/           # SQLModel database models
│   ├── repository/       # Database repository layer
│   ├── services/         # Business logic
│   ├── utils/            # URL parsing
│   └── cli.py            # CLI entry point
├── tests/                # 280 tests
├── CLAUDE.md             # Architecture & design decisions
├── DEPLOYMENT.md         # Deployment guide
├── README.md             # User documentation
└── CONTRIBUTING.md       # This file
```

**Key Areas for Contribution**:
- **Bug fixes**: CLI, web UI, fetcher, caching
- **Tests**: Improve coverage, add edge cases
- **Documentation**: Examples, guides, API docs
- **Performance**: Optimization, caching improvements

---

## Architecture Principles

### Design Patterns Used

1. **Orchestrator Pattern**: `TranscriptOrchestrator` coordinates fetcher, cache, and repository
2. **Repository Pattern**: Database access abstracted through `TranscriptRepository`
3. **Strategy Pattern**: Multiple output formats (text, JSON)
4. **Dependency Injection**: FastAPI dependencies for session and orchestrator

### Key Design Decisions

- **12-Factor App**: All configuration via environment variables
- **Proxy Auto-Detection**: Transparent proxy support for production
- **Caching Strategy**: 7-day TTL with database persistence
- **URL Flexibility**: Support 100+ YouTube URL formats

See [CLAUDE.md](CLAUDE.md) for complete architecture documentation.

---

## Common Contribution Areas

### Bug Fixes

Most contributions are bug fixes. Examples:
- CLI output formatting issues
- URL parsing edge cases
- Error handling improvements
- Proxy connection failures

### Documentation

Always valuable:
- Usage examples
- Installation troubleshooting
- Deployment guides for new platforms
- Code comments and docstrings

### Tests

Improve test coverage:
- Edge cases in URL parsing
- Error scenarios in fetcher
- Integration tests for API endpoints
- CLI command combinations

### Performance

Optimization opportunities:
- Caching effectiveness
- Database query optimization
- API response time improvements
- Memory usage reduction

---

## Questions and Discussion

### Where to Ask Questions

1. **GitHub Issues**: Bug reports, feature requests
2. **GitHub Discussions**: Questions, ideas, community discussion
3. **Pull Requests**: Code changes, improvements

### Getting Help

- Read [README.md](README.md) for user documentation
- Read [CLAUDE.md](CLAUDE.md) for architecture details
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guide
- Search existing issues and discussions

### Issue Reporting

When reporting issues, use the bug report template and include:
- Python version
- Operating system
- Error messages or logs
- Steps to reproduce
- Expected vs. actual behavior

---

## Code Review Process

### What We Look For

1. **Correctness**: Does it work? Are there edge cases?
2. **Tests**: Are tests comprehensive? Do they cover edge cases?
3. **Documentation**: Is the code self-documenting? Are docstrings clear?
4. **Style**: Does it match project conventions?
5. **Performance**: Will this impact performance negatively?
6. **Security**: Are there any security implications?

### Review Timeline

- Initial review: 1-3 days
- Follow-up comments: Will be addressed as soon as possible
- Approval: Once all feedback is addressed

---

## Recognition

Contributors will be:
- Listed in the project's contributors section
- Credited in release notes for significant contributions
- Mentioned in relevant commit messages

Thank you for contributing to YouTube Transcript Fetcher! 🎉

---

## Additional Resources

- [Python Testing Best Practices](https://docs.pytest.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [TDD Methodology](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

**Quick Links**:
- [README.md](README.md) - User documentation
- [CLAUDE.md](CLAUDE.md) - Architecture reference
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
