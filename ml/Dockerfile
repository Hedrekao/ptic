FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements from ml folder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Add virtual environment to path
ENV PATH="/opt/venv/bin:$PATH"

COPY ./ml/utils ./ml/utils
COPY ./ml/inference ./ml/inference
COPY ./ml/models ./ml/models
COPY ./ml/data/hierarchy.csv ./ml/data/hierarchy.csv
COPY ./ml/data/config.json ./ml/data/config.json
COPY ./ml/scripts ./ml/scripts
COPY ./ml/__init__.py ./ml/__init__.py

EXPOSE 3000

CMD python -m ml.inference.app
