# Dockerfile – ZoL0 AI Trading Bot
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt || true
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
