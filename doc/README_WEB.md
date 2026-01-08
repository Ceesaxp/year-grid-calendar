# Year Grid Calendar - Web Application

This directory contains the web interface for the Year Grid Calendar Generator, built with FastAPI and optimized for SEO and social media sharing.

## 🌟 Features

- **Beautiful Web UI**: Modern, responsive interface with gradient design
- **PDF Generation**: Create custom A1-sized yearly calendar PDFs
- **Font Customization**: Choose from bundled fonts or standard PDF fonts
- **Event Support**: Upload events file for personalized calendars
- **SEO Optimized**: Full meta tags, Open Graph, Twitter Cards, and structured data
- **Social Media Ready**: Rich previews when sharing on Facebook, Twitter, LinkedIn
- **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation
- **PWA Support**: Progressive Web App with offline capabilities
- **Rate Limiting**: Built-in protection against abuse
- **Health Checks**: Monitoring endpoint for deployment

## 📁 Directory Structure

```
web/
├── app.py                      # Main FastAPI application
├── Dockerfile                  # Docker container configuration
├── static/                     # Static assets (icons, manifest)
│   ├── favicon.ico
│   ├── android-chrome-*.png
│   ├── apple-touch-icon*.png
│   └── manifest.json
├── SEO_IMPROVEMENTS.md         # Complete SEO documentation
├── SEO_QUICK_REFERENCE.md      # Quick reference card
├── SUMMARY.md                  # Executive summary
├── DEPLOYMENT_CHECKLIST.md     # Deployment guide
├── test_seo.py                 # SEO test suite
├── CHANGES.txt                 # Change summary
└── README_WEB.md               # This file
```

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   cd ..  # Go to project root
   uv sync
   # or
   pip install -r requirements.txt
   ```

2. **Run the web server:**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the application:**
   ```
   http://localhost:8000
   ```

### Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t year-grid-calendar .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 -e BASE_URL=https://your-domain.com year-grid-calendar
   ```

3. **Access the application:**
   ```
   http://localhost:8000
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Production domain URL (no trailing slash) | `https://yeargridcalendar.com` |

**Example:**
```bash
export BASE_URL=https://your-domain.com
uvicorn app:app
```

**Docker:**
```bash
docker run -e BASE_URL=https://your-domain.com year-grid-calendar
```

**Docker Compose:**
```yaml
services:
  web:
    image: year-grid-calendar
    environment:
      - BASE_URL=https://your-domain.com
    ports:
      - "8000:8000"
```

### Rate Limiting

Default configuration (can be modified in `app.py`):
- **Requests**: 10 per window
- **Window**: 60 seconds
- **Scope**: Per IP address

## 🌐 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page with calendar generation form |
| `/generate` | POST | Generate and download calendar PDF |
| `/health` | GET | Health check endpoint |
| `/robots.txt` | GET | Search engine crawling instructions |
| `/sitemap.xml` | GET | XML sitemap for search engines |
| `/static/*` | GET | Static files (icons, manifest) |

## 🔍 SEO Features

### Meta Tags
- ✅ SEO-optimized title with keywords
- ✅ Compelling 160-character meta description
- ✅ Relevant keywords
- ✅ Canonical URL
- ✅ Robots directive (index, follow)

### Social Media
- ✅ Open Graph tags (Facebook, LinkedIn)
- ✅ Twitter Card tags
- ✅ Preview images (512x512)
- ✅ Rich sharing experience

### Structured Data
- ✅ JSON-LD Schema.org markup
- ✅ WebApplication type
- ✅ Feature list for rich snippets
- ✅ Pricing information (free)

### Technical SEO
- ✅ robots.txt for crawler guidance
- ✅ sitemap.xml for efficient indexing
- ✅ Semantic HTML (header, main, footer)
- ✅ ARIA labels for accessibility

**Documentation:**
- Complete guide: `SEO_IMPROVEMENTS.md`
- Quick reference: `SEO_QUICK_REFERENCE.md`
- Deployment checklist: `DEPLOYMENT_CHECKLIST.md`

## 🧪 Testing

### Manual Testing

```bash
# Start the server
uvicorn app:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/robots.txt
curl http://localhost:8000/sitemap.xml

# View page source
open http://localhost:8000/
```

### SEO Testing

```bash
# Run SEO test suite (requires httpx)
pip install httpx
python test_seo.py
```

### Online Validators

- **Facebook Sharing**: https://developers.facebook.com/tools/debug/
- **Twitter Cards**: https://cards-dev.twitter.com/validator
- **Rich Results**: https://search.google.com/test/rich-results
- **Schema.org**: https://validator.schema.org/
- **Lighthouse**: Chrome DevTools → Lighthouse tab

## 📦 Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **ReportLab**: PDF generation
- **Python 3.10+**: Required Python version

Optional:
- **httpx**: For running test suite
- **Pillow**: For regenerating icons

## 🎨 Customization

### Colors

Edit the gradient in `app.py` (home function):
```python
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Fonts

Add custom fonts to `../fonts/` directory. The application will automatically discover `.ttf` files.

### Icons

Regenerate icons with custom emoji/colors:
```bash
cd static
python generate-icons.py
```

### Meta Tags

Edit meta tags in `app.py` (home function, lines ~305-350):
- Change title, description, keywords
- Update social media preview text
- Customize structured data

## 🚢 Deployment

### Pre-Deployment Checklist

1. Set `BASE_URL` environment variable
2. Test all endpoints locally
3. Validate social media previews
4. Run Lighthouse audit
5. Check error logs

### Post-Deployment

1. Submit sitemap to Google Search Console
2. Test social sharing on Facebook/Twitter
3. Verify robots.txt is accessible
4. Monitor application logs
5. Set up uptime monitoring

**Complete checklist:** `DEPLOYMENT_CHECKLIST.md`

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "bundled_fonts": 10,
  "total_fonts": 16
}
```

### Logs

View application logs:
```bash
# Docker
docker logs <container-id>

# Systemd
journalctl -u year-grid-calendar -f

# Direct
tail -f /var/log/year-grid-calendar.log
```

## 🔒 Security

- Rate limiting enabled by default (10 requests per 60 seconds)
- Input validation for all user inputs
- File size limits (1MB for events file)
- UTF-8 encoding validation
- Temporary file cleanup
- No sensitive data stored

## 🐛 Troubleshooting

### Application won't start

```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | grep -E "fastapi|uvicorn|reportlab"

# Check port availability
lsof -i :8000
```

### Fonts not loading

```bash
# Check fonts directory
ls -la ../fonts/

# Download fonts
cd ../fonts
./download_fonts.sh
```

### Rate limit errors

Adjust rate limiting in `app.py`:
```python
RATE_LIMIT_REQUESTS = 20  # Increase limit
RATE_LIMIT_WINDOW = 60     # Time window in seconds
```

### SEO features not working

```bash
# Verify BASE_URL is set
echo $BASE_URL

# Test endpoints
curl http://localhost:8000/robots.txt
curl http://localhost:8000/sitemap.xml
```

## 🤝 Contributing

When making changes to the web interface:

1. Update relevant documentation
2. Test locally before committing
3. Run SEO test suite
4. Validate with online tools
5. Update CHANGES.txt if needed

## 📝 License

Same as parent project - see `../LICENSE`

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **ReportLab Guide**: https://www.reportlab.com/docs/
- **SEO Best Practices**: https://developers.google.com/search/docs
- **Open Graph Protocol**: https://ogp.me/
- **Schema.org**: https://schema.org/

## 🔗 Related Files

- **Main Application**: `app.py`
- **SEO Documentation**: `SEO_IMPROVEMENTS.md`
- **Quick Reference**: `SEO_QUICK_REFERENCE.md`
- **Deployment Guide**: `DEPLOYMENT_CHECKLIST.md`
- **Parent README**: `../README.md`
- **Docker Configuration**: `Dockerfile`

## 💡 Tips

1. **Performance**: Enable gzip compression in production
2. **Caching**: Consider adding CDN for static files
3. **Monitoring**: Set up application monitoring (e.g., Sentry)
4. **Backups**: Not needed - stateless application
5. **Scaling**: Can run multiple instances behind load balancer

## 📞 Support

For issues or questions:
- Check the documentation files in this directory
- Review FastAPI logs for errors
- Test with online validation tools
- Consult the parent project README

---

**Version**: 1.0  
**Last Updated**: 2026-01-08  
**Status**: ✅ Production Ready
