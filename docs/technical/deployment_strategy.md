
# Aura 系统部署策略

## 1. 概述

Aura 项目采用现代化的云原生部署策略，基于"本地开发 -> 预测试 -> 正式环境"的三阶段策略，确保代码质量、功能稳定性和快速迭代。系统以阿里云 Serverless 应用引擎 (SAE) 为核心计算平台，Supabase 作为后端基础设施，实现高可用、弹性扩展的服务部署。

## 2. 环境定义与配置

### 2.1 本地开发环境 (Local Development)

*   **目的**：为开发者提供独立的、快速反馈的开发环境，支持功能开发、调试和单元测试。
*   **架构组件**：
    *   **FastAPI BFF 服务**：在本地直接运行 `uvicorn main:app --reload`，支持热重载开发。
    *   **AI 计算服务**：可选择本地运行或连接到开发环境的 AI 服务。
    *   **Supabase 集成**：
        *   **推荐**：使用 `Supabase CLI` 在本地启动 Supabase 服务（包括 PostgreSQL 数据库、Auth、Storage 等）。
        *   **备选**：连接到共享的开发专用 Supabase 项目。
*   **环境配置**：
    *   使用 `.env.local` 文件管理本地环境变量。
    *   配置本地 Supabase 连接信息、AI 服务端点等。
*   **数据管理**：
    *   本地 Supabase 项目的数据应可被重置或填充测试数据。
    *   数据库模式变更应通过 `Supabase Migrations` 管理，并及时同步到代码库。
*   **开发流程**：
    1. 启动本地 Supabase：`supabase start`
    2. 启动 FastAPI 服务：`uvicorn main:app --reload`
    3. 启动 AI 服务（如需要）
    4. Flutter 应用连接本地后端进行开发调试

### 2.2 预测试环境 (Staging Environment)

*   **目的**：提供一个与生产环境高度相似的独立环境，用于集成测试、端到端测试、性能测试、用户验收测试 (UAT) 和 Bug Fix 验证。
*   **阿里云 SAE 部署**：
    *   **FastAPI BFF 服务**：部署为独立的 SAE 应用，配置 1-2 个实例。
    *   **AI 计算服务**：部署为独立的 SAE 应用或函数计算，根据计算需求配置。
    *   **负载均衡**：通过 SAE 内置网关或 SLB 提供统一入口。
*   **Supabase 集成**：
    *   配置独立的 Supabase 项目，与生产环境配置相似但使用较小的资源配额。
    *   数据应从生产环境脱敏同步或填充代表性测试数据。
*   **部署流程**：
    *   当开发分支（如 `develop` 或特性分支）的代码合并并通过初步测试后，自动部署到预测试环境。
    *   使用 GitHub Actions 或阿里云 DevOps 进行 CI/CD 自动化部署。
*   **环境配置**：
    *   使用 `.env.staging` 环境变量配置。
    *   配置 SAE 应用的环境变量和密钥管理。
*   **数据管理**：
    *   预测试环境的数据库模式应与生产环境保持同步，通过 Supabase Migrations 进行管理。
    *   定期清理或刷新数据，确保测试环境的干净。

### 2.3 正式环境 (Production Environment)

*   **目的**：面向最终用户提供稳定、高性能和高可用的服务。
*   **阿里云 SAE 部署**：
    *   **FastAPI BFF 服务**：部署为生产级 SAE 应用，支持自动扩缩容（最小 2 实例，最大 10 实例）。
    *   **AI 计算服务**：根据业务需求部署为 SAE 应用或函数计算，优化成本和性能。
    *   **负载均衡**：使用阿里云 SLB 提供高可用的流量分发。
    *   **域名和 SSL**：配置自定义域名和 SSL 证书。
*   **Supabase 集成**：
    *   配置独立的、生产级别的 Supabase 项目，具备高可用、备份恢复和监控能力。
    *   严格的数据安全和访问控制，启用行级安全 (RLS)。
*   **部署流程**：
    *   仅部署经过预测试环境充分验证的代码。
    *   使用蓝绿部署或滚动更新策略，确保零停机部署。
    *   部署应通过自动化 CI/CD 管道进行，包括自动化测试、安全扫描等。
*   **监控和告警**：
    *   集成阿里云监控服务，监控 SAE 应用性能、错误率、响应时间等。
    *   配置关键指标的告警规则。
*   **数据管理**：
    *   生产数据库的数据最为关键，需进行严格的备份和恢复策略。
    *   所有数据库模式变更必须经过严格的审查和测试。

## 3. 阿里云 SAE 部署策略

### 3.1 SAE 应用配置

#### 3.1.1 FastAPI BFF 服务
*   **应用类型**：Java/Python 应用
*   **技术栈**：Python 3.12 + FastAPI + Uvicorn
*   **资源配置**：
    *   **开发环境**：0.5 CPU Core, 1GB Memory, 1 实例
    *   **预测试环境**：1 CPU Core, 2GB Memory, 1-2 实例
    *   **生产环境**：2 CPU Core, 4GB Memory, 2-10 实例（自动扩缩容）
*   **部署包**：使用 Docker 镜像或 JAR/WAR 包
*   **健康检查**：配置 `/health` 端点，支持 HTTP 健康检查

#### 3.1.2 AI 计算服务
*   **部署选择**：
    *   **SAE 应用**：适合需要常驻内存和状态管理的 AI 服务
    *   **函数计算 (FC)**：适合无状态的 AI 计算任务，成本更优
*   **资源配置**：
    *   **开发环境**：1 CPU Core, 2GB Memory
    *   **预测试环境**：2 CPU Core, 4GB Memory
    *   **生产环境**：4 CPU Core, 8GB Memory（根据 AI 模型需求调整）

### 3.2 CI/CD 自动化部署

#### 3.2.1 构建流程
```yaml
# GitHub Actions 工作流示例
name: Deploy to SAE
on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t aura-bff:${{ github.sha }} .
          
      - name: Push to Alibaba Cloud Container Registry
        run: |
          # 推送镜像到阿里云容器镜像服务
          
      - name: Deploy to SAE
        run: |
          # 使用阿里云 SAE CLI 或 API 进行部署
```

#### 3.2.2 部署策略
*   **滚动更新**：默认部署方式，逐步替换实例，确保服务连续性
*   **蓝绿部署**：生产环境重要更新时使用，零停机切换
*   **金丝雀发布**：新功能渐进式发布，降低风险

### 3.3 环境变量和配置管理

#### 3.3.1 环境变量配置
*   **Supabase 配置**：
    ```env
    SUPABASE_URL=your_supabase_url
    SUPABASE_ANON_KEY=your_anon_key
    SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
    ```
*   **AI 服务配置**：
    ```env
    AI_SERVICE_URL=http://ai-service:8080
    OPENAI_API_KEY=your_openai_key
    CLAUDE_API_KEY=your_claude_key
    ```
*   **支付配置**：
    ```env
    STRIPE_SECRET_KEY=your_stripe_key
    ALIPAY_APP_ID=your_alipay_app_id
    ```

#### 3.3.2 密钥管理
*   使用阿里云密钥管理服务 (KMS) 存储敏感信息
*   在 SAE 应用中配置环境变量，引用 KMS 密钥
*   定期轮换 API 密钥和数据库密码

### 3.4 监控和日志

#### 3.4.1 应用监控
*   **阿里云应用实时监控服务 (ARMS)**：
    *   应用性能监控 (APM)
    *   业务监控和告警
    *   链路追踪分析
*   **关键指标**：
    *   响应时间 (P95, P99)
    *   错误率
    *   吞吐量 (QPS/TPS)
    *   CPU 和内存使用率

#### 3.4.2 日志管理
*   **阿里云日志服务 (SLS)**：
    *   应用日志收集和分析
    *   错误日志告警
    *   业务日志统计
*   **日志格式标准化**：
    ```json
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "level": "INFO",
      "service": "aura-bff",
      "user_id": "user_123",
      "request_id": "req_456",
      "message": "User login successful"
    }
    ```

### 3.5 安全和网络配置

#### 3.5.1 网络安全
*   **VPC 配置**：将 SAE 应用部署在专有网络 (VPC) 中
*   **安全组规则**：仅开放必要的端口（如 80, 443）
*   **WAF 防护**：使用阿里云 Web 应用防火墙防护常见攻击

#### 3.5.2 SSL 和域名
*   **自定义域名**：配置自有域名指向 SAE 应用
*   **SSL 证书**：使用阿里云 SSL 证书服务或 Let's Encrypt
*   **HTTPS 强制跳转**：确保所有流量都使用 HTTPS

## 4. Supabase 管理策略

### 3.1 独立 Supabase 项目

*   **每个环境（本地、预测试、正式）都将拥有独立的 Supabase 项目**。这确保了环境隔离，避免数据交叉污染和配置冲突。
*   对于本地开发，鼓励使用 `supabase start` 启动本地实例，或连接到共享的开发 Supabase 云项目。

### 3.2 数据库模式迁移 (Migrations)

*   所有数据库模式变更都应通过 `Supabase Migrations` 进行管理。这将确保模式变更的可追溯性、版本控制和跨环境的一致性。
*   迁移文件（`migrations/*.sql`）应与代码一起进行版本控制。
*   **工作流程**：
    1.  在本地开发环境（或通过本地 Supabase CLI）创建新的迁移文件 (`supabase migration new <migration_name>`)。
    2.  编写 SQL 来修改数据库模式（如创建表、添加列等）。
    3.  测试迁移，确保其在本地运行正常 (`supabase db reset` 或 `supabase db diff`)。
    4.  将迁移文件提交到版本控制系统。
    5.  在部署到预测试和正式环境时，运行 `supabase db push` 或其他自动化脚本来应用迁移。

### 3.3 Supabase Secrets/Environment Variables

*   每个环境的 Supabase URL、Anon Key、Service Role Key 等敏感信息都应通过环境变量进行管理，绝不能硬编码到代码中。
*   前端应用、API Gateway (Edge Functions) 和算法服务都需要配置相应的环境变量。
*   利用 Supabase 的 Secret 管理功能或 Vercel 等部署平台的 Secret 管理功能。

## 4. 部署工作流

### 4.1 版本控制 (Git)

*   使用 Git 进行代码版本管理，并遵循 `Git Flow` 或 `Trunk Based Development` 等主流分支策略。
*   例如：`main` 分支对应生产环境，`develop` 分支对应预测试环境，特性分支用于新功能开发。

### 4.2 持续集成 (CI)

*   每次代码提交或合并到 `develop`/`main` 分支时，自动触发 CI 流程。
*   CI 任务包括：代码 Lint、单元测试、集成测试、构建产物等。
*   确保所有测试通过后才能进行后续部署。

### 4.3 持续部署 (CD)

*   **前端应用**：通过 Vercel、Netlify 或其他前端托管服务，连接 Git 仓库，实现自动部署。
*   **API Gateway (Edge Functions)**：如果使用 Vercel Functions，可与前端应用一起部署；如果使用 Supabase Edge Functions，则通过 Supabase CLI 部署。
*   **算法服务**：独立部署，可以通过 Docker 容器化并部署到云平台（如 AWS ECS/EKS, Google Cloud Run, Azure Container Apps）或 Serverless 平台。具体部署方式取决于技术栈和团队偏好。
*   **数据库迁移**：作为 CD 流程的一部分，在代码部署前或后（根据具体策略）应用 Supabase 数据库迁移。

## 5. 监控与日志

*   **每个环境都需要独立的监控和日志系统**。
*   利用 Supabase 提供的日志和监控功能，以及外部服务（如 Datadog, Grafana, CloudWatch Logs）进行日志聚合、指标监控和告警。
*   特别关注 API Gateway 的请求日志、算法服务的性能指标和错误日志。

## 6. 安全

*   **数据脱敏**：在非生产环境中使用脱敏或虚拟数据进行测试。
*   **权限管理**：严格控制对各环境的访问权限，特别是生产环境。
*   **定期审计**：对 Supabase 配置、API Gateway 权限和算法服务进行定期安全审计。

## 7. 回滚策略

*   所有部署都应有明确的回滚方案，以便在出现严重问题时能够迅速恢复到上一个稳定版本。
*   数据库回滚尤其需要谨慎，可能需要数据备份。 

## 8. 团队协作与跨服务部署

Aura 系统由多个独立的服务和团队协作完成，为确保开发效率和系统稳定性，以下将详细阐述前端与后端、研发与算法团队之间的协作与部署策略。

### 8.1 前端 (Flutter App) 与后端 (API Gateway/Supabase/算法服务) 协作与部署

前端应用（Flutter App）和后端服务分别位于不同的代码仓库中，需要明确的协作机制和部署流程。

*   **代码仓库**：
    *   **前端**：独立的 Flutter 项目仓库。
    *   **后端**：当前 Aura-backend 仓库，包含 API Gateway (Edge Functions/Vercel Functions)、Supabase 配置和相关后端业务逻辑代码。算法服务可能位于其独立的仓库。
*   **API 契约**：
    *   **明确定义**：前端与后端之间通过 RESTful API 进行通信。所有 API 接口（包括请求参数、响应结构、错误码等）都必须通过文档（如 OpenAPI/Swagger）明确定义并保持同步。
    *   **版本管理**：当 API 发生不兼容变更时，应引入 API 版本号（例如 `/v1/`, `/v2/`），确保前端可以逐步升级。
*   **本地开发与联调**：
    *   **前端开发**：前端开发者可以在本地运行 Flutter 应用，并通过配置指向本地 Supabase 实例或预测试环境的后端 API。
    *   **后端开发**：后端开发者在本地启动 Supabase 或部署到开发 Supabase 项目，并确保 API Gateway 和算法服务在可访问的状态，供前端联调。
    *   **Mock 数据**：在后端 API 尚未完全就绪时，前端可以利用 Mock 数据进行独立开发和测试。
*   **部署流程**：
    *   **前端部署**：Flutter App 的部署涉及到构建移动端原生应用（Android APK/AAB, iOS IPA）。这通常通过独立的 CI/CD 管道完成，最终发布到应用商店（Google Play Store, Apple App Store）或内部分发平台。
    *   **后端部署**：后端服务（API Gateway、Supabase Edge Functions、算法服务）按照前述的部署策略进行独立部署，通常由研发团队负责。
    *   **解耦部署**：前端和后端可以独立部署，这意味着它们可以有不同的发布周期。API 契约的稳定性是实现这一点的关键。
*   **错误排查**：
    *   当前后端联调出现问题时，需要通过统一的日志和监控系统（见 `5. 监控与日志`）进行请求链路追踪，快速定位问题发生在哪一方。
    *   明确责任方，及时沟通解决。

### 8.2 研发团队与算法团队协作与部署

研发团队（负责基础设施、API Gateway、数据管理、用户认证、支付等）和算法团队（负责核心 AI 模型、运势推算、对话理解等）之间是紧密的合作伙伴，各自拥有独立的代码库和专业领域。

*   **职责划分回顾**：
    *   **研发团队**：提供稳定的平台和数据接口，处理用户侧和基础服务，集成算法服务。
    *   **算法团队**：开发和维护核心 AI 逻辑，通过标准 API 暴露服务。
*   **接口定义与管理**：
    *   **标准 API**：算法服务应通过 RESTful API（如 `4. 算法接口设计` 中定义的接口）向研发团队暴露其能力。这些接口的定义需要双方共同评审和确认。
    *   **版本控制**：与前端类似，算法服务接口也应考虑版本管理，以支持平滑升级。
    *   **契约先行**：在开发新功能时，应优先定义好研发与算法之间的接口契约，再并行开发。
*   **本地调试与联调**：
    *   **独立开发**：研发和算法团队可以独立开发各自的服务。算法团队可以使用 Mock 接口来模拟研发团队的服务，反之亦然。
    *   **联调环境**：在预测试环境中进行端到端联调。当出现跨服务问题时：
        *   **日志共享**：双方的日志系统需要能够关联请求，方便追踪请求在不同服务间的流转。
        *   **分布式追踪**：引入分布式追踪系统（如 OpenTelemetry），可以更清晰地看到请求在 API Gateway -> 算法服务 -> Supabase 之间的调用链和耗时。
        *   **沟通机制**：建立高效的沟通机制（如共享的联调群、定期的联调会议），快速同步问题和进展。
*   **部署与上线**：
    *   **独立部署**：研发服务和算法服务可以独立部署。算法服务通常以微服务形式部署（如 Docker 容器），有自己的 CI/CD 流程。
    *   **部署顺序**：通常情况下，算法服务应先于依赖它的研发服务部署，或者确保有完善的服务发现和熔断降级机制。
    *   **联合发布**：对于涉及新功能或重大变更的发布，研发团队和算法团队需要协调上线时间，确保所有依赖的服务都已更新。制定详细的上线检查清单和回滚预案。
    *   **A/B 测试/灰度发布**：对于算法模型的更新，可以考虑支持 A/B 测试或灰度发布，以降低风险并逐步验证效果。 