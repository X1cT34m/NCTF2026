FROM python:3.12-slim

WORKDIR /app

COPY . /app
COPY entrypoint.sh /

RUN chmod +x /entrypoint.sh

RUN pip install --no-cache-dir flask

CMD ["/entrypoint.sh"]