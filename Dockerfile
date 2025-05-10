# Step 1: Python backend setup
FROM python:3.10 AS backend

# Set the working directory for the entire app (frontend and backend)
WORKDIR /app

# Copy the backend files into the container
COPY app/backend/ ./app/backend/

# Create virtual environment and install dependencies for the backend
RUN python3 -m venv /app/app/backend/.venv \
    && /app/app/backend/.venv/bin/pip install --no-cache-dir -r /app/app/backend/requirements.txt

# Step 2: Build React frontend
FROM node:18 AS frontend

WORKDIR /app/frontend

# Copy the frontend code into the container
COPY app/frontend/ ./

# Install dependencies and build the React app
RUN npm install
RUN npm run build

# Step 3: Copy the frontend build into the backend's static directory
FROM backend

# Copy the built frontend files (moved to backend/static via Vite) into the backend's static folder
# Expose the port the backend will run on
EXPOSE 3000

# Command to run the backend
CMD ["/app/app/backend/.venv/bin/python", "-m", "quart", "--app", "app.backend.main:app", "run", "--port", "3000", "--host", "0.0.0.0", "--reload"]
