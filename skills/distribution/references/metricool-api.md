# Metricool API Reference

## Overview

Metricool provides a REST API for scheduling and publishing social media content.
The API supports LinkedIn, X/Twitter, Facebook, Instagram, TikTok, YouTube,
Threads, Bluesky, and Pinterest.

**Base URL:** `https://app.metricool.com/api`
**Documentation:** https://app.metricool.com/resources/apidocs/index.html
**PDF Guide:** https://static.metricool.com/API+DOC/API+English.pdf
**Plan Requirement:** Advanced or Custom (API not available on Free or Basic)

## Authentication

All API calls require the `X-Mc-Auth` header plus query parameters:

```
Header:  X-Mc-Auth: {METRICOOL_USER_TOKEN}
Params:  userId={METRICOOL_USER_ID}&blogId={METRICOOL_BLOG_ID}
```

### Getting Your Credentials

1. Log into Metricool at https://app.metricool.com
2. Go to **Settings → API**
3. Copy: User Token, User ID, Blog ID
4. Set environment variables:
   ```bash
   export METRICOOL_USER_TOKEN="your-token-here"
   export METRICOOL_USER_ID="your-user-id"
   export METRICOOL_BLOG_ID="your-blog-id"
   ```

## Endpoints

### List Profiles

Get all connected social media profiles and their provider IDs.

```
GET /api/admin/simpleProfiles
Headers: X-Mc-Auth: {token}
Params: userId={userId}
```

**Response:** Array of profile objects with `providerId`, `network`, `name`.
Extract the `providerId` for each network you want to schedule to.

### Schedule a Post

```
POST /api/v2/scheduler/posts
Headers:
  X-Mc-Auth: {token}
  Content-Type: application/json
Params: userId={userId}&blogId={blogId}
```

**Request Body — LinkedIn Text Post:**
```json
{
  "providers": [
    {
      "network": "linkedin",
      "providerId": "linkedin-provider-id"
    }
  ],
  "text": "Your post content here.\n\nShort paragraphs work best.\n\n#AIStrategy #CreativeLeadership",
  "scheduledDate": "2026-03-17T12:30:00Z",
  "media": []
}
```

**Request Body — LinkedIn Carousel (images):**
```json
{
  "providers": [
    {
      "network": "linkedin",
      "providerId": "linkedin-provider-id"
    }
  ],
  "text": "Swipe through to see the full framework →",
  "scheduledDate": "2026-03-17T12:30:00Z",
  "media": [
    { "url": "https://normalized-image-url-1.jpg" },
    { "url": "https://normalized-image-url-2.jpg" },
    { "url": "https://normalized-image-url-3.jpg" }
  ]
}
```

LinkedIn supports up to 20 images per carousel, plus video, GIF, and
document uploads (PDF, PPT, DOC).

**Request Body — X/Twitter Tweet:**
```json
{
  "providers": [
    {
      "network": "twitter",
      "providerId": "twitter-provider-id"
    }
  ],
  "text": "In Asia, 54% of creatives use AI daily. In the US, it's 44%.\n\nHere's what that 10-point gap teaches us about the future of creative work. 🧵",
  "scheduledDate": "2026-03-18T13:00:00Z",
  "media": []
}
```

**Request Body — X Thread:**
Threads are scheduled as multiple sequential posts. Schedule the first tweet,
then schedule replies chained to it. Check Metricool's thread support in their
scheduler — some implementations use a `thread` array in the request body.

**Request Body — Multi-Platform (LinkedIn + X simultaneously):**
```json
{
  "providers": [
    { "network": "linkedin", "providerId": "li-id" },
    { "network": "twitter", "providerId": "tw-id" }
  ],
  "text": "Shared text (will be posted to both platforms)",
  "scheduledDate": "2026-03-17T12:30:00Z",
  "media": []
}
```

**Important:** Do NOT use multi-platform posting for the same content.
The distribution skill requires adapted content per platform. Schedule
LinkedIn and X posts separately with platform-specific text.

**Response:** Returns post object with `id`, `scheduledDate`, `status`.

### Normalize Image URL

Before using images in scheduled posts, normalize them through Metricool:

```
POST /api/actions/normalize/image/url
Headers: X-Mc-Auth: {token}
Body: { "url": "https://your-image-url.jpg" }
```

**Response:** Returns normalized URL suitable for the scheduling endpoint.
Use this for all carousel images and image attachments.

## Rate Limits

Metricool inherits platform-specific rate limits:
- **LinkedIn:** No published per-day post limit via API, but excessive posting
  may trigger LinkedIn's spam detection
- **X/Twitter:** Subject to X's API rate limits (varies by X API tier)
- **General:** If you receive a 429 response, wait the time specified in the
  `Retry-After` header before retrying

**Recommendation:** When scheduling a full week (10+ posts), add a 1-second
delay between API calls to avoid rate limiting.

## MCP Server Alternative

Metricool offers an official MCP (Model Context Protocol) server for AI agent
integration:

**Repository:** https://github.com/metricool/mcp-metricool

**Installation:**
```bash
uvx mcp-metricool
```

**Configuration** (add to Claude Code MCP settings):
```json
{
  "mcpServers": {
    "metricool": {
      "command": "uvx",
      "args": ["mcp-metricool"],
      "env": {
        "METRICOOL_USER_TOKEN": "your-token",
        "METRICOOL_USER_ID": "your-user-id",
        "METRICOOL_BLOG_ID": "your-blog-id"
      }
    }
  }
}
```

The MCP server primarily provides access to metrics and analytics data.
For scheduling posts, the REST API described above is the primary integration.

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Post scheduled |
| 400 | Bad request | Check request body format |
| 401 | Unauthorized | Verify METRICOOL_USER_TOKEN |
| 403 | Forbidden | Check plan level (Advanced+ required) |
| 404 | Not found | Verify endpoint URL and provider IDs |
| 429 | Rate limited | Wait and retry per Retry-After header |
| 500 | Server error | Retry after 30 seconds; if persistent, use manual fallback |
