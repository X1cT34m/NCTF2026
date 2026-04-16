ARG PYTHON_VERSION=3.10.11
FROM python:${PYTHON_VERSION}-slim
# RUN pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple pycryptodome

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY task.py /app/run
# COPY secret.py /app

EXPOSE 5000

CMD socat TCP-LISTEN:5000,reuseaddr,fork EXEC:"python /app/run",pty,stderr,setsid,sigint,sane