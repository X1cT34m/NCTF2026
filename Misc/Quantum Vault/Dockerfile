FROM ubuntu:22.04

# 安装必要依赖 (注意这里增加了 sudo，用于启动时的降权切换)
RUN apt-get update && apt-get install -y python3 gcc make sudo && rm -rf /var/lib/apt/lists/*

# 创建低权限用户
RUN useradd -m -s /bin/bash ctfuser

# 部署 Python 服务端
COPY server.py /home/ctfuser/server.py
RUN chown ctfuser:ctfuser /home/ctfuser/server.py && chmod 755 /home/ctfuser/server.py

# 编译并部署 SUID 漏洞程序
COPY q-vault-sync.c /tmp/q-vault-sync.c
RUN gcc /tmp/q-vault-sync.c -o /usr/local/bin/q-vault-sync
RUN chown root:root /usr/local/bin/q-vault-sync && chmod 4755 /usr/local/bin/q-vault-sync
RUN rm /tmp/q-vault-sync.c

# 准备工作目录
WORKDIR /home/ctfuser
EXPOSE 9999

# --- 关键部分：启动命令 ---
# 1. 使用 root 身份执行 (不要写 USER ctfuser)
# 2. 在 CMD 中完成：写入 Flag -> 修改权限 -> 切换用户执行服务
CMD sh -c "echo \$GZCTF_FLAG > /root/flag.txt && chmod 400 /root/flag.txt && exec sudo -u ctfuser python3 /home/ctfuser/server.py"