############################ Builder Stage ############################
FROM python:3.12.3-slim-bullseye AS builder

# Build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_HTTP_TIMEOUT=120

# Install essential build tools (if any other non-python build steps needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies with UV
COPY pyproject.toml .
RUN pip install uv && \    
    uv pip install . --system

# Placeholder for any future build steps if needed

############################ Final Stage ############################
FROM python:3.12.3-slim-bullseye

# Create essential directories with proper permissions
RUN mkdir -p /app \
    /app/staticfiles \
    /app/staticfiles/media \
    /app/core/static \
    /app/core_theme/static \
    /root/.ssh && \
    chmod -R 777 /app && \
    chmod 700 /root/.ssh

# Copy only what we need from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=core.config.settings

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    dos2unix \
    openssh-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

CMD ["/bin/sh", "-c", "dos2unix /app/scripts/* && chmod +x /app/scripts/* && /app/scripts/entrypoint.prod.sh"]