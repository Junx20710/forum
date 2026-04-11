# Forum API Pro

> 基于 FastAPI + MySQL + Redis 的社交论坛后端服务，配套完整的自动化测试体系（单元 / 集成 / 性能）与 CI/CD 流水线。

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 数据库 | MySQL 8.0（Alembic 迁移管理） |
| 缓存 | Redis 7.0（Token 黑名单 + 速率限制） |
| 自动化测试 | Pytest + 数据驱动（DDT）+ 深度 Mock |
| 性能压测 | Locust（FastHttpUser C 扩展引擎） |
| CI/CD | GitHub Actions（两阶段流水线） |
| 容器化 | Docker 多阶段构建 + docker-compose |
| 测试报告 | Allure（自动发布 GitHub Pages） |

## 项目亮点

- **测试金字塔全覆盖**：单元测试（Mock 隔离）→ 集成测试（27+ 参数化用例）→ 性能测试（100 并发 / 60s），覆盖率 93%+
- **CI 质量门禁**：覆盖率低于 90% 直接阻断流水线，确保代码质量底线
- **安全机制验证**：JWT Token 黑名单拦截、Redis 滑动窗口防刷（10s/3次），均有专属测试用例
- **性能瓶颈定位**：压测数据预热从 152s 优化至 1s（Bcrypt 批处理），精确捕获连接池雪崩阈值
- **配置安全**：敏感信息通过 `.env` 环境变量管理，不进入版本控制

## 项目结构

```
forum/
├── app/                        # 应用代码
│   ├── api/
│   │   ├── deps.py             # 依赖注入（DB / Redis / JWT 鉴权）
│   │   └── endpoints/
│   │       ├── auth.py         # 注册 / 登录 / 登出
│   │       └── posts.py        # 发帖 / 列表 / 点赞
│   ├── core/
│   │   ├── config.py           # 环境变量配置（.env 驱动）
│   │   └── security.py         # 密码哈希 / JWT 签发
│   └── schemas/                # Pydantic 请求校验
├── tests/
│   ├── unit/                   # 单元测试（Mock 隔离）
│   ├── integration/            # 集成测试（真实 DB + Redis）
│   │   ├── auth/               # 注册正/反向 + 登出黑名单
│   │   └── posts/              # 发帖 DDT + 多用户交互链
│   └── performance/            # Locust 性能压测
├── migrations/                 # Alembic 数据库迁移
├── scripts/                    # 压测数据预热脚本
├── .github/workflows/          # CI/CD 流水线
├── Dockerfile                  # 多阶段构建（生产级瘦身镜像）
├── docker-compose.yml          # MySQL + Redis + API 三服务编排
├── 测试计划_v1.0.docx           # 正式测试计划文档
└── 测试用例矩阵_v1.0.xlsx       # 35 条用例，覆盖 4 种设计方法
```

## 快速启动

### 方式一：Docker（推荐）

```bash
git clone https://github.com/Junx20710/forum.git
cd forum
cp .env.example .env          # 创建环境配置
docker-compose up -d          # 启动 MySQL + Redis + API
docker exec forum_api alembic upgrade head   # 初始化数据库
```

访问 API 文档：http://localhost:8000/docs

### 方式二：WSL 本地开发

```bash
cd /mnt/d/DevSoftware/code/forum
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
sudo service mysql start && sudo service redis-server start
alembic upgrade head
uvicorn app.main:app --reload
```

## 运行测试

```bash
# 单元 + 集成测试（含覆盖率）
pytest tests/unit tests/integration --cov=app --cov-fail-under=90 -v

# 性能压测（需先启动 API）
python scripts/pre_warm.py
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s --host http://127.0.0.1:8000
```

## CI/CD 流水线

```
Push / PR to main
    ↓
[Stage 1] Pytest 功能测试 → 覆盖率 ≥ 90% 门禁
    ↓
[Stage 2] Locust 性能压测 → 100 并发 / 60s
    ↓
[Stage 3] Allure 报告聚合 → 自动发布 GitHub Pages
```

## API 接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/v2/user/register` | 用户注册 | 无 |
| POST | `/api/v2/user/login` | 用户登录（返回 JWT） | 无 |
| POST | `/api/v2/user/logout` | 用户登出（Token 黑名单） | Bearer |
| POST | `/api/v2/posts/create` | 发布帖子（Redis 限流） | Bearer |
| GET | `/api/v2/posts/list` | 帖子列表（分页） | 无 |
| POST | `/api/v2/posts/{id}/like` | 点赞 / 取消点赞 | Bearer |

## 测试设计方法

本项目测试用例基于以下四种标准化方法设计：

- **等价类划分**：输入数据分有效/无效类，减少冗余用例
- **边界值分析**：用户名 2/3/20/21，标题 0/1/100/101
- **错误猜测法**：空值、纯空格、Token 重放攻击、SQL 注入
- **场景法**：多用户交互链路（注册→发帖→点赞→取消→验证一致性）
