

WORKDIR /app

# Copy full app (including backend with built static files)
COPY app/ ./app

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/app/backend"

# Install Python dependencies
RUN python3 -m venv /app/app/backend/.venv \
    && /app/app/backend/.venv/bin/pip install --no-cache-dir -r app/backend/requirements.txt

# Step 1: Build React frontend
FROM node:18 AS frontend

WORKDIR /app/app/frontend
COPY app/frontend/ ./

RUN npm install
RUN npm run build

# Step 2: Python backend
FROM python:3.10

# Expose port
EXPOSE 3000

# Run backend
CMD ["/app/app/backend/.venv/bin/python", "-m", "quart", "--app", "app/backend/main:app", "run", "--port", "3000", "--host", "0.0.0.0", "--reload"]
