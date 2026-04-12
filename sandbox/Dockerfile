FROM python:3.11-slim

# 创建非 root 用户
RUN useradd -m -s /bin/bash sandbox && \
    mkdir -p /sandbox && \
    chown sandbox:sandbox /sandbox

WORKDIR /sandbox
USER sandbox

ENTRYPOINT ["python3", "-"]
