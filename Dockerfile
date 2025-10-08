# Dockerfile

# Stage 1: Build stage with dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools if needed by dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential

# Copy requirements and install wheels
COPY requirement.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirement.txt

# Stage 2: Final application stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed wheels from the builder stage and install them
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy the application code
COPY ./k8s_cost_optimizer ./k8s_cost_optimizer

EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "k8s_cost_optimizer.main:app", "--host", "0.0.0.0", "--port", "8000"]