# Aura Backend

基于 FastAPI 的 Aura 占星应用后端服务，整合 Supabase 进行用户认证、数据存储和文件管理。

## 功能特性

- 🔐 **用户认证**：基于 Supabase Auth 的用户注册、登录和会话管理
- 👤 **用户画像**：收集用户出生信息并进行星相分析
- 🎭 **虚拟形象**：多种 AI 助手角色选择
- 🔮 **新手引导**：分步式引导用户完成初始化设置
- 🤖 **算法集成**：与专门的算法服务进行交互
- 📊 **异步处理**：高性能的异步 API 设计

## 技术栈

- **后端框架**：FastAPI
- **数据库**：Supabase PostgreSQL
- **认证**：Supabase Auth
- **文件存储**：Supabase Storage
- **开发环境**：WSL + Docker

## 快速开始

### 环境要求

- Python 3.11+
- WSL2 (Windows) 或 Linux
- Supabase 项目

### 1. 自动化设置（推荐）

```bash
# 运行自动化设置脚本
./scripts/setup.sh
```

### 2. 手动设置

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 Supabase 配置
```

### 3. 数据库设置

```bash
# 如果使用 Supabase CLI
supabase db push

# 或者在 Supabase Dashboard 中手动执行 migration 文件
```

### 4. 启动服务

```bash
# 开发模式
./scripts/dev.sh

# 或直接运行
python main.py

# 或使用 Docker
docker-compose up
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

## 项目结构

```
aura-backend/
├── src/
│   ├── config/          # 配置文件
│   ├── controllers/     # API 控制器
│   ├── middleware/      # 中间件
│   ├── services/        # 业务逻辑层
│   ├── types/          # 数据模型
│   └── utils/          # 工具函数
├── scripts/            # 部署和开发脚本
├── supabase/          # Supabase 配置和迁移
├── main.py            # 应用入口点
└── requirements.txt   # Python 依赖
```

## API 端点

### 新手引导相关

- `GET /api/v1/onboarding/status` - 获取引导状态
- `GET /api/v1/onboarding/avatars` - 获取可选虚拟形象
- `GET /api/v1/onboarding/profile` - 获取用户档案
- `POST /api/v1/onboarding/profile` - 创建/更新用户档案
- `PATCH /api/v1/onboarding/profile` - 部分更新用户档案
- `GET /api/v1/onboarding/profile/analysis` - 获取用户分析结果

### 健康检查

- `GET /health` - 应用健康状态
- `GET /api/v1/health` - API 健康状态

## 环境变量

参考 `.env.example` 文件配置以下环境变量：

```env
# Supabase 配置
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:54322/postgres

# API 配置
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# 环境设置
ENVIRONMENT=development

# 算法服务
ALGORITHM_SERVICE_URL=http://localhost:8001
```

## 开发指南

### 新增 API 端点

1. 在 `src/types/database.py` 中定义数据模型
2. 在 `src/services/` 中实现业务逻辑
3. 在 `src/controllers/` 中创建控制器
4. 在 `src/routes/__init__.py` 中注册路由

### 数据库变更

1. 创建新的迁移文件：`supabase migration new your_migration_name`
2. 编写 SQL 语句
3. 应用迁移：`supabase db push`

### 算法服务集成

系统已集成与算法服务的异步通信接口，参考 `src/services/onboarding.py` 中的实现。

## 部署

### 使用 Docker

```bash
# 构建并启动
docker-compose up --build

# 后台运行
docker-compose up -d
```

### 生产环境

1. 设置生产环境变量
2. 配置 HTTPS
3. 使用生产级数据库
4. 配置日志和监控

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License