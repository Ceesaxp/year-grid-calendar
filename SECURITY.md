# Security Policy

Security measures implemented in the Year Grid Calendar Generator.

## Overview

This application generates PDF calendars based on user input. While the functionality is relatively simple, we implement multiple layers of security to protect against common web vulnerabilities.

## Security Measures Implemented

### 1. Input Validation

#### Year Validation
- **Range**: 1900-2200
- **Type**: Integer only
- **Purpose**: Prevents overflow, unrealistic dates, and processing issues

#### Title Sanitization
- **Max Length**: 200 characters
- **Filtering**: Removes control characters, null bytes
- **XSS Protection**: Blocks `<script>`, `javascript:`, `onerror=`, `onclick=`
- **Normalization**: Strips to single line, removes excessive whitespace

#### Font Validation
- **Allowlist**: Only fonts discovered at startup are allowed
- **Path Traversal**: Blocks `../`, absolute paths
- **Basename Only**: Strips directory components

#### Events File Validation
- **Extension**: Must be `.txt`
- **Size Limit**: 1MB maximum
- **Encoding**: Must be valid UTF-8
- **Path Traversal**: Blocks suspicious filenames
- **Content**: Parsed safely with regex patterns

### 2. Rate Limiting

**Per IP Address:**
- 10 requests per 60 seconds on `/generate` endpoint
- Automatic cleanup of old request records
- 429 status code when exceeded

**Why:**
- Prevents abuse/DoS
- Protects server resources (PDF generation is CPU-intensive)
- Prevents spam/flooding

### 3. File Upload Security

**Checks:**
- ✅ File size limit (1MB)
- ✅ Extension validation (.txt only)
- ✅ UTF-8 encoding validation
- ✅ Filename sanitization
- ✅ Path traversal prevention
- ✅ Temporary file cleanup

**Safe Handling:**
- Files saved to temp directory with random names
- Automatic cleanup after processing
- No user-controlled file paths
- No arbitrary file execution

### 4. Security Headers

Applied to all responses:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

**Purpose:**
- Prevent MIME sniffing attacks
- Prevent clickjacking
- Enable browser XSS protection
- Control referrer information

### 5. Dependency Security

**Python Dependencies:**
- ReportLab: PDF generation (sandboxed, no code execution)
- FastAPI: Modern web framework with built-in protections
- Uvicorn: ASGI server with security best practices
- Python-multipart: Safe file upload handling

**Updates:**
- Regular dependency updates recommended
- Use `pip list --outdated` to check
- Monitor security advisories

### 6. Container Security

**Docker Best Practices:**
- ✅ Non-root user (`appuser`)
- ✅ Slim base image (minimal attack surface)
- ✅ No unnecessary packages
- ✅ Read-only font mounts
- ✅ Health checks for monitoring

### 7. Logging and Monitoring

**What's Logged:**
- Calendar generation requests (year, title)
- Font usage
- Events file uploads (count only, not content)
- Errors and exceptions
- Rate limit violations

**What's NOT Logged:**
- Event file contents (privacy)
- IP addresses in normal operation
- User-identifiable information

### 8. HTTPS/TLS

**Deployment:**
- Digital Ocean App Platform: Automatic HTTPS via Let's Encrypt
- Self-hosted: Automatic HTTPS via Caddy
- Local dev: HTTP only (not exposed to internet)

## Known Limitations

### What We DON'T Protect Against

1. **Advanced DDoS**: Rate limiting helps but isn't enterprise-grade
   - **Mitigation**: Use Cloudflare or similar CDN in front

2. **Resource Exhaustion**: Very large PDFs could consume memory
   - **Mitigation**: Instance size limits, monitoring

3. **Sophisticated Attacks**: Not designed for high-security environments
   - **Mitigation**: Don't use for sensitive/classified data

## Threat Model

### Attack Vectors Considered

| Attack | Protection | Severity |
|--------|------------|----------|
| XSS (Cross-Site Scripting) | Title sanitization, headers | Medium |
| Path Traversal | Filename validation | High |
| Code Injection | No eval/exec, safe parsing | High |
| File Upload Abuse | Size limits, type validation | Medium |
| DoS (Denial of Service) | Rate limiting | Medium |
| CSRF | Not applicable (no sessions) | Low |
| SQL Injection | Not applicable (no database) | N/A |

### What's NOT a Concern

- **SQL Injection**: No database
- **Authentication Bypass**: No authentication required
- **Session Hijacking**: No sessions
- **Password Attacks**: No passwords

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email security concerns to: andrei@ceesaxp.org
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

**Response Time:** Within 48 hours

## Security Best Practices for Deployment

### Production Deployment

1. **Use HTTPS**: Always deploy behind HTTPS/TLS
2. **Keep Updated**: Regular updates of dependencies
3. **Monitor Logs**: Watch for unusual patterns
4. **Set Limits**: Configure appropriate instance sizes
5. **Backup**: Regular backups of configuration

### Environment Variables

No secrets are currently required, but if adding API keys:

```bash
# GOOD - Use environment variables
export API_KEY=secret_value

# BAD - Never hardcode in code
API_KEY = "secret_value"  # Don't do this!
```

### Firewall Rules

**Recommended:**
- Allow only HTTPS (443) to public
- Block direct access to application port (8080)
- Use reverse proxy (Caddy/nginx/DO App Platform)

### Rate Limiting Enhancement

For high-traffic deployments, consider:
- Redis-backed rate limiting
- Per-user API keys with higher limits
- CAPTCHA for web interface
- IP allowlists for trusted clients

## Compliance

### Data Privacy

- **No PII Collected**: App doesn't store personal information
- **No Tracking**: No analytics, cookies, or tracking
- **Temporary Storage**: Uploaded files deleted after processing
- **Logs**: Contain only operational data

### GDPR Compliance

- ✅ No personal data stored
- ✅ No cookies or tracking
- ✅ Data minimization (only process what's needed)
- ✅ Right to erasure (nothing to erase)

## Security Checklist

Before deploying to production:

- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Log monitoring set up
- [ ] Dependencies updated
- [ ] Security headers verified
- [ ] File size limits appropriate
- [ ] Non-root user in container
- [ ] Backup strategy in place
- [ ] Incident response plan

## Updates

This security policy should be reviewed quarterly or:
- After major feature additions
- Following security incidents
- When new threats emerge
- Based on security audits

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [ReportLab Security](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)

## Version

- **Last Updated**: 2024-01-08
- **Version**: 1.0
- **Review Date**: 2024-04-08

---

**Remember**: Security is a process, not a product. Stay vigilant, keep updated, and monitor continuously.
