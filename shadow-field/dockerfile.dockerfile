FROM python:3.10-slim AS builder

WORKDIR /build
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir build && python -m build

FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install package
COPY --from=builder /build/dist/*.whl ./
RUN pip install --no-cache-dir *.whl[serve,monitoring] && rm *.whl

# Create non-root user
RUN useradd -m -u 1000 shadow && chown -R shadow:shadow /app
USER shadow

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Entry point - can be overridden
ENTRYPOINT ["shadow-field"]
CMD ["serve", "--port", "8080"]