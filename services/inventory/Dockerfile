FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY services/inventory/ ./services/inventory/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "services.inventory.main:app", "--host", "0.0.0.0", "--port", "8000"]
