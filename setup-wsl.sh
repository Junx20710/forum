#!/bin/bash
# ============================================
# Forum API - WSL 开发环境一键初始化脚本 (国内极速版)
# ============================================

set -e  # 任何命令失败就停止

echo "================================"
echo "🔧 开始初始化 Forum 开发环境"
echo "================================"

# ============================================
# 第 1 步：安装系统依赖 (强制注入国内 APT 镜像源)
# ============================================
echo ""
echo "📦 第 1/6：更新包管理器，安装系统服务..."

echo "🔄 正在将 Ubuntu APT 源切换为阿里云镜像..."
# 兼容老版本 Ubuntu (22.04 及以下)
sudo sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true
sudo sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true

# 兼容新版本 Ubuntu (24.04 及以上)
sudo sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || true
sudo sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || true

# 刷新源列表，必须加 --fix-missing 防范残留的断连包
sudo apt update --fix-missing

# 安装系统级依赖
sudo apt install -y curl python3-pip

# ============================================
# 第 2 步：安装 uv（Python 版本和依赖管理）
# ============================================
echo ""
echo "⚡ 第 2/6：安装 uv..."
# 💡 抛弃 wget/curl github，直接用系统 pip 配合清华源安装 uv
pip3 install uv --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple

# 让 uv 命令在当前 shell 立即可用 (pip 安装通常在 ~/.local/bin)
export PATH="$HOME/.local/bin:$PATH"

echo "✅ uv 安装完成"

echo "🐍 安装 Python 3.11..."
# 💡 强制 uv 从国内镜像下载 Python 预编译包，防止再次卡死！
export UV_PYTHON_INSTALL_MIRROR="https://mirror.ghproxy.com/https://github.com/indygreg/python-build-standalone/releases/download"

echo "✅ Python 3.11 安装完成"

# ============================================
# 第 3 步：安装 MySQL Server
# ============================================
echo ""
echo "🗄️  第 3/6：安装 MySQL Server..."
sudo apt install -y mysql-server

# 启动 MySQL
sudo service mysql start
sleep 3

# 设置 root 密码为 'root'（开发环境）
sudo mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';"
sudo mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS forum_db;"
echo "✅ MySQL 配置完成（用户: root, 密码: root, 数据库: forum_db）"

# ============================================
# 第 4 步：安装 Redis
# ============================================
echo ""
echo "🔴 第 4/6：安装 Redis..."
sudo apt install -y redis-server
sudo service redis-server start
echo "✅ Redis 启动完成"

# ============================================
# 第 5 步：创建 Python 虚拟环境并安装依赖（uv）
# ============================================
echo ""
echo "📚 第 5/6：用 uv 创建虚拟环境和安装依赖..."

cd /mnt/d/DevSoftware/code/forum

uv venv --python 3.11 venv
source venv/bin/activate

# 💡 给 uv pip 也加上清华源，享受毫秒级装包体验
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

echo "✅ Python 依赖安装完成"

# ============================================
# 第 6 步：运行数据库迁移
# ============================================
echo ""
echo "🗄️  第 6/6：运行数据库迁移..."

mysql -u root -proot -e "SELECT 1;"
alembic upgrade head

echo "✅ 数据库迁移完成"

# ============================================
# 完成
# ============================================
echo ""
echo "================================"
echo "✅ 初始化完成！一切就绪。"
echo "================================"