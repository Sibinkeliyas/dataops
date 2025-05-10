# --- Stage 1: Build React Frontend ---
    FROM node:18 AS frontend

    WORKDIR /app/frontend
    COPY app/frontend/ ./
    
    RUN npm install
    RUN npm run build
    
    # --- Stage 2: Python Backend ---
    FROM python:3.10
    
    # Set work directory
    WORKDIR /app
    
    # Set PYTHONPATH to make `app` package discoverable
    ENV PYTHONPATH="/app"
    
    # Copy backend code (includes app/backend)
    COPY app/ ./app
    
    
    # Create virtual environment
    RUN python -m venv /app/app/backend/.venv
    
    # Install backend dependencies
    RUN /app/app/backend/.venv/bin/pip install --upgrade pip && \
        /app/app/backend/.venv/bin/pip install -r app/backend/requirements.txt
    
    # Expose the backend port
    EXPOSE 3000
    
    # Run the backend app
    CMD ["/app/app/backend/.venv/bin/python", "-m", "quart", "--app", "app.backend.main:app", "run", "--port", "3000", "--host", "0.0.0.0"]
    