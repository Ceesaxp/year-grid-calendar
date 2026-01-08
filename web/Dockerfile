FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and fonts
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Copy source files
COPY src/ /app/src/
COPY web/ /app/web/
COPY fonts/ /app/fonts/

# Install Python dependencies
RUN pip install --no-cache-dir \
    reportlab \
    fastapi \
    uvicorn[standard] \
    python-multipart

# Expose port
EXPOSE 8000

# Run the web service
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
