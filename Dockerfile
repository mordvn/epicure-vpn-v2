# Build stage
FROM python:3.13-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
ENV PATH="/root/.cargo/bin:$PATH"
RUN uv pip install --system --no-cache -r <(uv pip compile pyproject.toml)

# Runtime stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY app/ ./app/
COPY pyproject.toml ./

# Copy .env file
COPY .env ./.env

# Expose port if needed (adjust as necessary)
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "app"]
