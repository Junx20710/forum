# 💡 使用官方 Python 3.9 的轻量级 (slim) 镜像作为基础底座
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 💡 环境变量优化：禁止生成 .pyc 文件，强制无缓冲输出日志
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 💡 安装系统级依赖 (防止某些 Python C 扩展编译失败，比如 PyMySQL 的底层依赖)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 💡 利用 Docker 缓存机制：先拷贝 requirements.txt 并安装，只要依赖没变，这步极速秒过
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 将整个项目代码拷贝进容器
COPY . .

# 暴露 FastAPI 运行的 8000 端口
EXPOSE 8000

# 💡 启动命令：注意这里 host 必须是 0.0.0.0，否则宿主机无法访问容器内部
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]