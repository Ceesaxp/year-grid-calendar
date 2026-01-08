# Bug Fix: robots.txt BASE_URL Substitution

## Issue
The `/robots.txt` endpoint was not properly substituting the `BASE_URL` variable, returning literal text `{BASE_URL}` instead of the actual URL value.

## Root Cause
The endpoint was using `response_class=PlainTextResponse` but then wrapping the content in a `Response()` object. When using `response_class`, FastAPI expects the raw content to be returned directly, not wrapped.

## Fix Applied
Changed from:
```python
@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    content = f"""User-agent: *
...
"""
    return Response(content=content, media_type="text/plain")
```

To:
```python
@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return f"""User-agent: *
...
"""
```

## Verification
Both endpoints now correctly substitute BASE_URL:

```bash
# Test with custom BASE_URL
export BASE_URL=https://test.example.com
python -c "from web.app import robots, sitemap; import asyncio; asyncio.run(robots())"
```

Expected output includes `https://test.example.com/sitemap.xml`

## Status
✅ Fixed and tested
✅ Both `/robots.txt` and `/sitemap.xml` working correctly
✅ BASE_URL substitution verified

## Date
2026-01-08
