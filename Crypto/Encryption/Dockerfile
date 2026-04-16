FROM ubuntu:22.04

RUN useradd -m -s /bin/sh ctf && passwd -d ctf

RUN sed -i 's|http://archive.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com|http://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y socat

WORKDIR /app
COPY ./task/build/out /app

EXPOSE 5000

CMD socat -d -d TCP-LISTEN:5000,reuseaddr,fork EXEC:"/app/main",stderr