# Pinned base image (no :latest) for supply-chain integrity (SECURITY-10).
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY src ./src
COPY migrations ./migrations

# Run as a non-root user (hardening, SECURITY-09).
RUN useradd --create-home appuser
USER appuser

# Inbound entrypoint (MCP/HTTP) is provided by U6; placeholder until then.
CMD ["python", "-c", "import mini_aip; print('mini-aip', mini_aip.__version__)"]
