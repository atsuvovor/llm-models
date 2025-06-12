# Use official slim Python image (compact and secure)
FROM python:3.10-slim

# Environment settings to streamline Python behavior
ENV PYTHONDONTWRITEBYTECODE 1  # Avoid .pyc files
ENV PYTHONUNBUFFERED 1         # Immediate stdout/stderr

# Set working directory inside container
WORKDIR /app

# Install essential system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .

# Upgrade pip and install dependencies without caching
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password appuser
USER appuser

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health or exit 1

# Copy app source code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Run the Streamlit app with CORS disabled for dev-friendly access
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]

