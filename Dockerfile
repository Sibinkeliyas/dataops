# --- Stage 1: Build React Frontend ---
    FROM node:18 AS frontend

    WORKDIR /frontend
    COPY app/frontend/ ./
    RUN npm install
    RUN npm run build
    
    # --- Stage 2: Python Backend with Frontend Output ---
    FROM python:3.10
    
    # Set working directory
    WORKDIR /app
    
    # Set PYTHONPATH so Python finds the app correctly
    ENV PYTHONPATH="/app"
    
    # Install system dependency for ODBC issue (optional; if you're using pyodbc)
    RUN apt-get update && apt-get install -y libodbc1
    
    # Copy backend
    COPY app/backend/ ./backend
    
    # Copy React build output into backend/static
    # COPY --from=frontend /frontend/build ./backend/static
    
    # Create virtual environment
    RUN python -m venv /app/backend/.venv
    
    # Install Python deps
    RUN /app/backend/.venv/bin/pip install --upgrade pip && \
        /app/backend/.venv/bin/pip install -r backend/requirements.txt
    
    # Expose port
    EXPOSE 3000
    
    # Start the app
    CMD ["/app/backend/.venv/bin/python", "-m", "quart", "--app", "backend.main:app", "run", "--port", "3000", "--host", "0.0.0.0"]
    