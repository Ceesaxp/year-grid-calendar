# Dockerfile for Digital Ocean App Platform
# Standalone build that includes all dependencies and fonts

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and tools
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY src/ /app/src/
COPY web/ /app/web/
COPY fonts/ /app/fonts/

# Install Python dependencies
RUN pip install --no-cache-dir \
    reportlab>=4.0.0 \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    python-multipart>=0.0.6

# Download fonts at build time
WORKDIR /app/fonts
RUN chmod +x download_fonts.sh && \
    ./download_fonts.sh || echo "Warning: Font download failed, will use system fonts"

# Return to app directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (DO App Platform uses 8080 by default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]
