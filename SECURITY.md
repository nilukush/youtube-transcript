# Security Policy

## Supported Versions

Currently, only the latest version of YouTube Transcript Fetcher is supported.

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: Yes |

## Reporting Security Vulnerabilities

### How to Report

If you discover a security vulnerability, please **do not** open a public issue. Instead, send an email to: **nilesh.kumar@usezenith.ai**

### What to Include

Please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if known)

### Response Timeline

- **Initial response**: Within 48 hours
- **Investigation**: Within 7 days
- **Resolution**: As soon as feasible based on severity

### What Happens Next

1. We will acknowledge receipt of your report
2. We will investigate the vulnerability
3. We will determine severity and impact
4. We will develop a fix
5. We will coordinate disclosure if needed
6. We will release a security update

---

## Security Scope

### In Scope

The following security issues are **in scope** for this policy:

- **Authentication & Authorization**: Bypassing access controls
- **Injection**: SQL injection, command injection, code injection
- **Cross-Site Scripting (XSS)**: Reflected or stored XSS
- **Data Exposure**: Unauthorized access to transcripts or data
- **Denial of Service (DoS)**: Resource exhaustion attacks
- **Configuration**: Security misconfigurations
- **Cryptography**: Weak encryption or hashing
- **Proxy Issues**: Proxy credential exposure or misuse

### Out of Scope

The following are **out of scope** (unless they demonstrate a serious vulnerability):

- Typos or minor UI bugs
- Issues affecting unsupported versions
- Reports without proof-of-concept or reproduction steps
- Theoretical vulnerabilities without practical impact

---

## Security Best Practices

### For Users

1. **Proxy Credentials**: Store securely in environment variables, never in code
2. **Deployment**: Use environment variables for all sensitive configuration
3. **Updates**: Keep the application updated to the latest version
4. **Network**: Deploy behind HTTPS/TLS in production
5. **Database**: Use strong database passwords and restrict access

### For Contributors

1. **No Secrets**: Never commit API keys, passwords, or credentials
2. **Dependencies**: Keep dependencies updated
3. **Input Validation**: Always validate and sanitize user input
4. **Error Messages**: Don't expose sensitive information in errors
5. **Dependencies**: Review third-party dependencies before adding

---

## Known Security Considerations

### Proxy Credentials

The application uses WebShare rotating proxies for bypassing YouTube rate limiting:
- Credentials are loaded from environment variables
- Never stored in code or configuration files
- `.env.example` shows required variables without actual values

### Database

- SQLite for development (local file)
- PostgreSQL for production (if configured)
- No sensitive user data stored
- Transcripts are cached from public YouTube videos

### API Endpoints

- `/api/transcript` - Public endpoint for fetching transcripts
- Input validation on all endpoints
- Rate limiting via proxy rotation
- No authentication required (transcripts are public data)

### Dependencies

Key security-related dependencies:
- `fastapi` - Web framework with built-in security features
- `pydantic` - Input validation and serialization
- `sqlmodel` - Database ORM with parameterized queries
- `youtube-transcript-api` - Transcript fetching

---

## Security Updates

### How Updates Are Released

Security updates will be:
- Released as patch version updates (0.1.x → 0.1.y)
- Announced in the release notes
- Tagged with `security` label in releases
- Deployed to production as soon as possible

### Staying Informed

To stay informed about security updates:
- Watch this repository on GitHub
- Subscribe to release notifications
- Check the release notes regularly
- Update to the latest version promptly

---

## Disclosure Policy

### Vulnerability Disclosure Process

1. **Report**: Vulnerability reported privately
2. **Acknowledge**: We confirm receipt within 48 hours
3. **Investigate**: We investigate and validate the issue
4. **Develop**: We develop a fix
5. **Test**: We test the fix thoroughly
6. **Release**: We release a security update
7. **Announce**: We announce the vulnerability (if applicable)

### Coordinated Disclosure

For serious vulnerabilities, we follow coordinated disclosure:
- Fix is developed first
- Users are given time to update
- Public disclosure after update is available
- Credit given to reporter (if desired)

---

## Security Contact

For security questions or concerns:
- **Email**: nilesh.kumar@usezenith.ai
- **PGP Key**: [Available on request]
- **Response Time**: Within 48 hours

Please do **not** use GitHub issues for security reports.

---

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Vulnerabilities](https://cwe.mitre.org/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Python Security](https://docs.python.org/3/library/security_warnings.html)

---

## Policy Version

This security policy was last updated: January 13, 2026

We may update this policy from time to time. The latest version will always be available in this file.
