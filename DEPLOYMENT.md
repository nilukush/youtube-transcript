# Deployment Guide

## 🚀 Try it First!

**Before deploying**, experience the live demo: https://youtube-transcript-zb5k.onrender.com

Try the service in action to understand what you're deploying. See how it handles:
- YouTube URL parsing (100+ formats supported)
- Transcript fetching with language selection
- JSON and plain text output formats
- Smart proxy support for bypassing rate limits

---

## For Application Owners

This guide is for application owners who want to deploy the YouTube Transcript Fetcher as a production service.

## Architecture Overview

**User Experience**: End users visit the website, enter a YouTube URL, and get a transcript. No configuration required.

**Backend**: The application uses proxy servers (that you configure) to bypass YouTube rate limiting. Proxy configuration is entirely backend infrastructure via environment variables.

---

## Quick Start (Production)

### 1. Get WebShare Proxies

Sign up at [webshare.io](https://www.webshare.io/) and get:
- **WebShare Rotating Proxies** (recommended): Automatic IP rotation
- **Static Residential Proxies**: Fixed IP addresses
- **Datacenter Proxies**: Cheaper but more likely to be blocked

### 2. Set Environment Variables

Configure these in your production environment:

```bash
# WebShare Rotating Proxies (recommended)
WEBSHARE_PROXY_USERNAME=your_username
WEBSHARE_PROXY_PASSWORD=your_password
WEBSHARE_PROXY_LOCATIONS=US,CA,UK  # Optional: preferred countries
WEBSHARE_PROXY_RETRIES=10  # Optional: retry count when blocked

# OR Generic Proxy (if not using WebShare)
GENERIC_PROXY_HTTP_URL=http://proxy.example.com:8080
GENERIC_PROXY_HTTPS_URL=http://proxy.example.com:8080
```

### 3. Deploy

Choose your platform:

- **Render** (recommended): See Render section below
- **Railway**: See Railway section below
- **AWS/GCP**: Use Docker deployment
- **VPS/Custom**: See Docker Compose section

---

## Platform-Specific Deployment

### Render (Recommended)

**Free tier available!**

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set environment variables in Render dashboard:
   ```
   WEBSHARE_PROXY_USERNAME=your_username
   WEBSHARE_PROXY_PASSWORD=your_password
   ```
5. Deploy!

**Render Configuration:**
- Build Command: `pip install -e .`
- Start Command: `uvicorn youtube_transcript.api.app:create_app --host 0.0.0.0 --port $PORT`
- Instance Type: Free (256MB RAM) or Starter (512MB RAM)

### Railway

1. Fork this repository
2. Create a new project on Railway
3. Deploy from GitHub
4. Add environment variables in Railway dashboard
5. Railway automatically detects and deploys

**Railway Configuration:**
- Build Command: `pip install -e .`
- Start Command: `uvicorn youtube_transcript.api.app:create_app --host 0.0.0.0 --port $PORT`

### Docker Compose (VPS/Custom)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    image: python:3.11-slim
    working_dir: /app
    command: uvicorn youtube_transcript.api.app:create_app --host 0.0.0.0 --port 8888
    environment:
      - WEBSHARE_PROXY_USERNAME=${WEBSHARE_PROXY_USERNAME}
      - WEBSHARE_PROXY_PASSWORD=${WEBSHARE_PROXY_PASSWORD}
      - WEBSHARE_PROXY_LOCATIONS=${WEBSHARE_PROXY_LOCATIONS:-US,CA}
    ports:
      - "8888:8888"
    volumes:
      - .:/app
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

---

## Environment Variables Reference

### Required for Proxy Support

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `WEBSHARE_PROXY_USERNAME` | string | WebShare username | `abc123` |
| `WEBSHARE_PROXY_PASSWORD` | string | WebShare password | `xyz789` |

### Optional Proxy Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `WEBSHARE_PROXY_LOCATIONS` | string | `null` | Comma-separated country codes (e.g., `US,CA,UK`) |
| `WEBSHARE_PROXY_RETRIES` | int | `10` | Number of retries when blocked |
| `GENERIC_PROXY_HTTP_URL` | string | `null` | Generic HTTP proxy URL |
| `GENERIC_PROXY_HTTPS_URL` | string | `null` | Generic HTTPS proxy URL |

### Database Configuration (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | `sqlite:///youtube_transcript.db` | Database connection URL |

### Cache Configuration (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REDIS_URL` | string | `null` | Redis connection URL (for caching) |

---

## Proxy Configuration Options

### Option 1: WebShare Rotating Proxies (Recommended)

**Best for production - automatic IP rotation**

```bash
export WEBSHARE_PROXY_USERNAME="your_username"
export WEBSHARE_PROXY_PASSWORD="your_password"
```

The application automatically rotates through multiple proxy endpoints.

**Benefits**:
- Automatic IP rotation
- Higher success rate
- Less likely to be blocked

**Pricing**: ~$500/month for 10 ports (as of 2026)

### Option 2: Static Residential Proxies

**Fixed IP addresses from residential networks**

Use the same WebShare environment variables. The rotating proxy service automatically manages multiple IPs.

### Option 3: Generic Proxy

**If using a different proxy service**

```bash
export GENERIC_PROXY_HTTP_URL="http://proxy.example.com:8080"
export GENERIC_PROXY_HTTPS_URL="http://proxy.example.com:8080"
```

**Note**: Most generic proxies don't support HTTPS tunneling. Use HTTP for both URLs.

---

## Testing Proxy Configuration

Before deploying to production, test your proxy:

```bash
# Set environment variables
export WEBSHARE_PROXY_USERNAME="your_username"
export WEBSHARE_PROXY_PASSWORD="your_password"

# Run test script
python -c "
from youtube_transcript.config import get_proxy_config
config = get_proxy_config()
print(f'Proxy configured: {config}')
if config:
    print('✓ Proxy configuration successful')
else:
    print('✗ No proxy configured')
"

# Test fetching a transcript
python -m youtube_transcript.cli fetch "https://youtu.be/dQw4w9WgXcQ"
```

---

## Scaling Considerations

### Concurrent Users

**Free Tier (WebShare)**: ~10 concurrent users
**Paid Tier**: 100+ concurrent users per proxy port

**Recommendation**: Start with 10 ports and scale based on usage.

### Caching (Recommended for Production)

Enable Redis caching to reduce API calls:

```bash
export REDIS_URL="redis://localhost:6379/0"
```

**Benefits**:
- 80%+ cache hit rate for popular videos
- Reduced proxy usage
- Faster response times (< 500ms)

### Database

**Development**: SQLite (included)
**Production**: PostgreSQL (recommended for scaling)

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

---

## Monitoring and Logs

### Health Checks

Monitor these metrics:

- Transcript fetch success rate (> 95% target)
- Response times (p95 < 10s uncached, < 500ms cached)
- Proxy failures (rotate if > 10% failure rate)

### Logging

The application logs:
- Successful transcript fetches
- Proxy connection errors
- Rate limiting occurrences
- Missing transcripts

**View logs**:
```bash
# Render/Docker
docker-compose logs -f

# Railway
railway logs
```

---

## Troubleshooting

### High Rate of "Transcript Not Found"

**Causes**:
1. Proxy blocked by YouTube
2. Proxy location restriction
3. Video actually has no transcript

**Solutions**:
1. Try different proxy locations
2. Switch to residential proxies
3. Verify video has captions on YouTube

### Slow Response Times

**Causes**:
1. No caching enabled
2. Proxy network latency
3. Database not optimized

**Solutions**:
1. Enable Redis caching
2. Use geographically closer proxies
3. Switch to PostgreSQL

### Proxy Connection Errors

**Symptoms**:
- `ProxyConnectionError`
- `SSLError: EOF occurred in violation of protocol`

**Solutions**:
1. Verify proxy credentials
2. Check WebShare account status
3. Try generic proxy instead

---

## Cost Optimization

### Free Tier Options

- **Render**: Free tier (256MB RAM, 750 hours/month)
- **Railway**: $5 free credit/month
- **WebShare**: 10 free proxies (limited bandwidth)

### Paid Tier Estimates

**Monthly costs for 1000 daily users**:

| Service | Cost | Notes |
|---------|------|-------|
| Hosting (Render) | $7-20 | Starter or Pro plan |
| Proxies (WebShare) | $500 | 10 ports, rotating |
| Database (PostgreSQL) | $0-20 | Managed or self-hosted |
| Redis (optional) | $0-15 | For caching |
| **Total** | **~$500-550/month** | Without optimization |

**Cost Reduction Tips**:
1. Enable caching to reduce proxy usage
2. Use datacenter proxies (cheaper but less reliable)
3. Implement request rate limiting
4. Cache popular videos for 7+ days

---

## Security Best Practices

1. **Never commit proxy credentials** to git
2. **Use environment variables** for all secrets
3. **Rotate proxy passwords** regularly
4. **Monitor usage** for abuse
5. **Implement rate limiting** per IP
6. **Use HTTPS** in production

**Example `.env` file (gitignored)**:
```bash
WEBSHARE_PROXY_USERNAME=your_username
WEBSHARE_PROXY_PASSWORD=your_password
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

---

## Production Checklist

- [ ] Set up WebShare account and obtain credentials
- [ ] Configure environment variables in hosting platform
- [ ] Test proxy configuration locally
- [ ] Deploy to staging environment
- [ ] Test with multiple YouTube URLs
- [ ] Enable caching (Redis)
- [ ] Set up monitoring and alerts
- [ ] Configure backup for database
- [ ] Implement rate limiting
- [ ] Set up log aggregation
- [ ] Document runbooks for common issues
- [ ] Deploy to production

---

## Support

- **Deployment Issues**: [GitHub Issues](https://github.com/nilukush/youtube-transcript/issues)
- **WebShare Support**: [WebShare.io Support](https://www.webshare.io/support)
- **Proxy Issues**: Check WebShare dashboard for proxy status

---

## Architecture Note for Developers

**How It Works**:

1. User visits website and enters YouTube URL
2. Application creates `TranscriptOrchestrator`
3. Orchestrator auto-detects proxy from environment:
   ```python
   config = get_proxy_config()  # Reads WEBSHARE_PROXY_USERNAME
   fetcher = YouTubeTranscriptFetcher(proxy_config=config)
   ```
4. Fetcher uses proxy to bypass rate limits
5. Transcript returned to user

**No proxy configuration exposed to users** - it's entirely backend infrastructure!
