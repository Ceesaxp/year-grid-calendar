# Dockerfile for Digital Ocean App Platform
# Alpine-based multi-stage build for minimal image size (~50-80MB)

# Stage 1: Download fonts
FROM alpine:3.23 AS builder

RUN apk add --no-cache curl unzip

WORKDIR /app/fonts
COPY fonts/download_fonts.sh .
RUN chmod +x download_fonts.sh && ./download_fonts.sh

# Stage 2: Runtime
FROM python:3.12-alpine

WORKDIR /app

# Install Python dependencies
# Note: reportlab may need build deps on some systems, but wheels are available
RUN pip install --no-cache-dir \
    reportlab>=4.0.0 \
    fastapi>=0.104.0 \
    uvicorn>=0.24.0 \
    python-multipart>=0.0.6

# Copy application files
COPY src/ /app/src/
COPY web/ /app/web/

# Copy downloaded fonts from builder stage
COPY --from=builder /app/fonts/*.ttf /app/fonts/

# Create non-root user for security
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (DO App Platform uses 8080 by default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]
