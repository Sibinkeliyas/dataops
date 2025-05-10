# Step 1: Build React frontend
FROM node:18 AS frontend

WORKDIR /app/app/frontend
COPY app/frontend/ ./

RUN npm install
RUN npm run build

# Step 2: Python backend
FROM python:3.10 AS backend

WORKDIR /app

# Copy backend files first
COPY app/backend/ ./app/backend/

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/app/backend"

# Create virtual environment and install dependencies
RUN python3 -m venv /app/app/backend/.venv \
    && /app/app/backend/.venv/bin/pip install --no-cache-dir -r /app/app/backend/requirements.txt

# Copy frontend build output from previous stage into backend's static folder
COPY --from=frontend /app/app/frontend/dist/ /app/app/backend/static/


# Expose port
EXPOSE 3000

# Run backend
CMD ["/app/app/backend/.venv/bin/python", "-m", "quart", "--app", "app.backend.main:app", "run", "--port", "3000", "--host", "0.0.0.0", "--reload"]
