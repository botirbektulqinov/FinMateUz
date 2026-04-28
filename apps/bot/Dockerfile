FROM python:3.12-slim

WORKDIR /app/apps/bot
ENV PYTHONPATH=/app/apps/bot
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip
COPY apps/bot ./
RUN pip install --no-cache-dir "."

CMD ["python", "-m", "bot.main"]
