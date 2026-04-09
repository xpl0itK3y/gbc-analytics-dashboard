FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files
# and to keep stdout/stderr unbuffered for immediate logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKDIR=/app

WORKDIR ${WORKDIR}

# Install system dependencies if required (e.g., for psycopg2 down the line, but currently standard libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the actual application files
COPY . .

# Expose port 3000 as requested
EXPOSE 3000

# Run Uvicorn pointing identically to main.py -> app
# Binding to 0.0.0.0 is critical so the port is exposed outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
