# --- Stage 1: Build React Frontend ---
    FROM node:18 AS frontend

    WORKDIR /app/frontend
    COPY app/frontend/ .
    
    RUN npm install
    RUN npm run build
    
    # --- Stage 2: Build Python Backend with Frontend Output ---
    FROM python:3.10
    
    # Set work directory
    WORKDIR /app
    
    # Copy backend code
    COPY app/backend/ ./backend
    

    # Create virtual environment
    RUN python -m venv /app/backend/.venv
    
    # Install dependencies using venv
    RUN /app/backend/.venv/bin/pip install --upgrade pip && \
        /app/backend/.venv/bin/pip install -r backend/requirements.txt
    
    # Expose backend port
    EXPOSE 3000
    
    # Run the app with the venv python interpreter
    CMD ["/app/backend/.venv/bin/python", "-m", "quart", "--app", "backend/main:app", "run", "--port", "3000", "--host", "0.0.0.0"]
    