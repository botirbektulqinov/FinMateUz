FROM python:3.12-slim

WORKDIR /app/apps/api
ENV PYTHONPATH=/app/apps/api
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip
COPY apps/api ./
RUN pip install --no-cache-dir "."

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
