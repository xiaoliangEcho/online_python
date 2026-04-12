# Python 沙箱 Dockerfile - 最大安全配置
FROM python:3.11-slim

# 安装必要的工具（最小化）
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m -s /bin/bash sandbox && \
    mkdir -p /sandbox && \
    chown sandbox:sandbox /sandbox

# 移除不必要的工具
RUN rm -rf /usr/bin/wget /usr/bin/curl /usr/bin/apt /usr/bin/apt-get 2>/dev/null || true

WORKDIR /sandbox
USER sandbox

# 禁止创建 Python 缓存
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python3", "-"]
