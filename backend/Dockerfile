# Production Dockerfile for AutoForgeNexus Backend
# Multi-stage build for optimized production image
# Python 3.13 + FastAPI

# ============================================
# Stage 1: Builder - Dependencies compilation
# ============================================
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy dependency files only (optimize layer caching)
# Separate pyproject.toml and README.md for better cache hits
COPY pyproject.toml ./

# Install dependencies to /install directory
# Use --no-deps for explicit dependency control (security)
RUN pip install --prefix=/install --no-warn-script-location .

# ============================================
# Stage 2: Runtime - Production image
# ============================================
FROM python:3.13-slim AS runtime

# Set working directory
WORKDIR /app

# Install only runtime dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi8 \
    libssl3 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/install/lib/python3.13/site-packages:${PYTHONPATH}" \
    # Observability (Phase 2 monitoring infrastructure)
    ENABLE_METRICS=true \
    ENABLE_TRACING=true \
    # LangFuse integration (Phase 2 LLM observability)
    LANGFUSE_ENABLED=false \
    LANGFUSE_HOST=http://langfuse:3002 \
    # Prometheus metrics
    PROMETHEUS_ENABLED=false \
    PROMETHEUS_PORT=9090

# Copy installed dependencies from builder
COPY --from=builder /install /install

# Copy application code (production only, no tests)
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic

# Copy entrypoint script with executable permission
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Install netcat for database wait functionality
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID/GID
RUN groupadd -g 1000 appuser && \
    useradd -m -u 1000 -g appuser appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check (uses /health endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint for migrations and startup logic
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Production command with Gunicorn process management
# Gunicorn provides:
#  - Graceful shutdown (SIGTERM handling)
#  - Worker management and auto-restart
#  - Better production stability
# Dynamic workers: WORKERS env var (default: CPU cores * 2 + 1)
CMD ["sh", "-c", "gunicorn src.main:app \
     --worker-class uvicorn.workers.UvicornWorker \
     --workers ${WORKERS:-4} \
     --bind 0.0.0.0:8000 \
     --access-logfile - \
     --error-logfile - \
     --log-level info \
     --timeout 120 \
     --graceful-timeout 30 \
     --keep-alive 5"]
