FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    flask \
    pandas \
    openpyxl \
    faker

COPY . .

RUN mkdir -p /app/static

EXPOSE 8888

CMD ["python", "server.py"]