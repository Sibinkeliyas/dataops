# Step 1: Build React frontend
FROM node:18 AS frontend

WORKDIR /app/frontend
COPY app/frontend/ .

RUN npm install
RUN npm run build

# Step 2: Python backend with built frontend
FROM python:3.10

WORKDIR /app

# Copy backend code
COPY app/backend/ ./backend



# Expose port
EXPOSE 3000

# Run backend (should serve static files from /static)
CMD ["python", "-m", "quart", "--app", "backend/main:app", "run", "--port", "3000", "--host", "0.0.0.0", "--reload"]
