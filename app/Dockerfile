FROM python:3.11

COPY backend /app/backend

WORKDIR /app/backend

RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 8000

CMD ["python3", "-m", "gunicorn", "main:app"]
