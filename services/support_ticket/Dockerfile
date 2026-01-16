FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY services/support_ticket/ ./services/support_ticket/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "services.support_ticket.main:app", "--host", "0.0.0.0", "--port", "8000"]
