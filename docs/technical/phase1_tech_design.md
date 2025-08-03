# 技术设计：第一阶段

## 1. 概述

### 1.1 目标
本阶段目标是完成用户身份认证、核心用户交互功能（对话、运势、合盘）的研发侧架构与接口设计。

### 1.2 研发与算法职责划分
*   **研发团队**：负责前端界面、后端服务（FastAPI BFF 服务、用户管理、支付流程、数据存储、消息推送）、系统集成、基础设施搭建、以及与算法团队的接口联调。
*   **算法团队**：负责核心 AI 模型的开发、部署、优化，包括用户画像分析、运势推算、对话理解与生成、合盘逻辑等，并通过研发团队定义的接口提供服务。

### 1.3 服务协作流程
前端应用发出的请求首先会通过 **FastAPI BFF 服务**。FastAPI BFF 服务负责认证鉴权、业务逻辑编排和请求路由。对于需要调用算法能力（如用户画像分析、运势推算、对话理解与生成、合盘分析）的请求，FastAPI BFF 服务会将请求转发至 **算法服务**。算法服务处理完核心 AI 逻辑后，会将结果返回给 FastAPI BFF 服务，再由 FastAPI BFF 服务进行数据聚合和业务处理后返回给前端。研发团队负责维护 FastAPI BFF 服务和所有与数据存储、用户管理、支付、消息推送等相关的后端服务，并确保与算法服务之间的接口联调顺畅。算法团队则专注于其微服务内部的 AI 模型开发和优化，通过研发团队定义的标准接口提供计算能力。

## 2. 详细设计任务分解

### 2.1 用户身份认证与账号管理 (P1)
*   **研发任务**：
    *   **利用 Supabase Auth 进行用户身份认证和管理**。
    *   设计用户 Profile 表结构，并与 Supabase 用户 ID 关联。具体表结构详见 `3.1 用户 Profile 表设计`。
    *   实现基于 Supabase 的邮箱/手机号注册、登录、密码重置、用户信息更新。
    *   **Supabase 负责验证码发送（邮件）和凭证管理**。
    *   预留与第三方认证服务（如 OAuth）的集成点，Supabase 通常支持这些集成。
*   **算法接口预留**：
    *   无直接算法接口，但用户出生信息将作为后续算法模块的输入。

### 2.2 新手引导 (P0)
*   **研发任务**：
    *   实现分步式新手引导界面。
    *   收集用户昵称、性别、出生信息（年、月、日、时、分、秒、出生地）。
    *   实现虚拟形象选择界面与数据存储。具体表结构详见 `3.2 虚拟形象表设计`。
    *   引导用户完成首次对话。
*   **算法接口预留**：
    *   `POST /api/algorithm/user-profile-analysis`：接收用户出生信息，返回基础用户分析（如生辰八字、星相基础盘）。此接口由研发调用，将分析结果存储。具体接口定义详见 `4.1 用户画像分析接口`。分析结果存储在 `3.3 用户画像分析结果表设计`。

### 2.3 对话功能 (P0)
*   **研发任务**：
    *   设计实时通讯架构（WebSocket 或其他长连接方式）。
    *   实现聊天界面，支持文本输入与显示。
    *   实现对话历史记录存储与查询。具体表结构详见 `3.4 对话会话表设计` 和 `3.5 对话消息表设计`。
    *   处理对话冷启动逻辑（根据用户角色初始化首次对话）。
    *   实现对话中用户意图识别与功能调用的路由逻辑。
    *   “今日入口”卡片显示与跳转逻辑。
*   **算法接口预留**：
    *   `POST /api/algorithm/chat/initiate`：根据用户ID和选择的虚拟形象，初始化首次对话内容。具体接口定义详见 `4.2 对话初始化接口`。
    *   `POST /api/algorithm/chat/respond`：接收用户输入、当前对话上下文、用户画像，返回 AI 响应文本及可能的引导操作（如建议算卦、索取他人信息）。具体接口定义详见 `4.3 对话响应接口`。
    *   `POST /api/algorithm/fortune/predict`：接收用户请求，触发运势预测。具体接口定义详见 `4.4 运势预测接口`。
    *   `POST /api/algorithm/compatibility/analyze`：接收用户及他人信息，触发合盘分析。具体接口定义详见 `4.5 合盘分析接口`。
    *   **注意**：对话模块需要高度智能地判断何时调用上述算法接口，并根据接口返回的结果进行界面展示和后续引导。

### 2.4 每日运势 (P0)
*   **研发任务**：
    *   设计每日运势数据存储结构。具体表结构详见 `3.6 每日运势数据表设计`。
    *   实现每日运势展示界面（吉凶、宜忌、幸运色、幸运数字、概括）。
    *   实现定时任务（Cron Job，**可能通过 Supabase Functions 或外部服务触发**）触发每日运势计算。
    *   实现消息推送服务（Push Notification，**可能与 Supabase Edge Functions 结合**）。
    *   设计塔罗牌/抽签卜卦沉浸式交互入口。
*   **算法接口预留**：
    *   `POST /api/algorithm/daily-fortune/calculate`：接收用户ID、当天日期、用户画像，返回当天的运势详细信息。具体接口定义详见 `4.6 每日运势计算接口`。
    *   `POST /api/algorithm/tarot/draw`：触发塔罗牌抽取，返回结果及解读。具体接口定义详见 `4.7 塔罗牌抽取接口`。
    *   `POST /api/algorithm/divination/draw`：触发抽签卜卦，返回结果及解读。具体接口定义详见 `4.8 抽签卜卦接口`。

### 2.5 合盘 (P0)
*   **研发任务**：
    *   设计他人 Profile 输入界面（姓名、出生信息等）。具体表结构详见 `3.7 他人 Profile 表设计`。
    *   设计合盘结果展示界面。
*   **算法接口预留**：
    *   `POST /api/algorithm/compatibility/calculate`：接收两个用户的ID及必要信息，返回关系预测与建议（短中长期）。具体接口定义详见 `4.5 合盘分析接口`。分析结果存储在 `3.8 合盘分析结果表设计`。

### 2.6 付费 (P1)
*   **研发任务**：
    *   设计付费点位（高级模型、对话次数等）配置与管理。具体表结构详见 `3.9 定价计划表设计`、`3.10 交易记录表设计` 和 `3.11 用户订阅表设计`。
    *   集成第三方支付网关（如 Stripe、PayPal 等国际支付方案，**可能通过 Supabase Edge Functions 或外部服务集成**）。
    *   实现订单管理、充值、消费记录查询。
    *   设计后台管理界面用于监控付费数据。
*   **算法接口预留**：
    *   无直接算法接口，但算法服务可能需要根据用户付费等级提供不同功能或响应质量。例如，在调用 `chat/respond` 时，可以根据用户的付费等级调整 LLM 的模型选择或生成内容的详细程度。

### 2.7 核心数据分析 (P1)
*   **研发任务**：
    *   搭建简单 Admin 后台（**可考虑 Supabase Studio 或自建管理界面**）。
    *   设计数据采集与日志记录机制（注册用户数、日活、留存、付费、功能渗透率，**利用 Supabase Database、Auth Logs 等**）。
    *   实现数据可视化报表。
*   **算法接口预留**：
    *   无直接算法接口，但算法团队可能需要提供模型性能指标、用户反馈等数据给研发用于分析。

## 3. 数据库表设计

### 3.1 用户 Profile 表设计 (`profiles`)
*   **描述**：存储用户的基本信息和与 Supabase Auth 的关联。
*   **结构**：
    *   `id` (UUID, Primary Key): 对应 `auth.users.id`，与 Supabase Auth 的用户 ID 关联。
    *   `nickname` (TEXT): 用户昵称。
    *   `gender` (ENUM: 'male', 'female', 'secret', 'lgbtq+'): 性别。
    *   `birth_year` (INTEGER): 出生年份。
    *   `birth_month` (INTEGER): 出生月份。
    *   `birth_day` (INTEGER): 出生日期。
    *   `birth_hour` (INTEGER, NULLABLE): 出生小时，24小时制。
    *   `birth_minute` (INTEGER, NULLABLE): 出生分钟。
    *   `birth_second` (INTEGER, NULLABLE): 出生秒。
    *   `birth_location` (TEXT): 出生地（精确到市县或省）。
    *   `birth_longitude` (NUMERIC, NULLABLE): 出生经度。
    *   `birth_latitude` (NUMERIC, NULLABLE): 出生纬度。
    *   `selected_avatar_id` (UUID, Foreign Key to `avatars` table): 用户选择的虚拟形象 ID。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.2 虚拟形象表设计 (`avatars`)
*   **描述**：存储虚拟形象的配置信息。
*   **结构**：
    *   `id` (UUID, Primary Key): 虚拟形象唯一 ID。
    *   `name` (TEXT): 虚拟形象名称（如“星语者·小满”）。
    *   `description` (TEXT): 虚拟形象角色设定/故事。
    *   `image_url` (TEXT): 虚拟形象海报图片 URL。
    *   `abilities` (JSONB, NULLABLE): 差异化能力描述（JSON 数组或字符串）。
    *   `initial_dialogue_prompt` (TEXT): 该虚拟形象的冷启动对话提示词。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.3 用户画像分析结果表设计 (`user_profiles_analysis`)
*   **描述**：存储算法服务对用户出生信息分析后的结果。
*   **结构**：
    *   `id` (UUID, Primary Key): 自增 ID 或其他唯一标识。
    *   `user_id` (UUID, Foreign Key to `auth.users.id`): 关联的用户 ID。
    *   `analysis_data` (JSONB): 存储算法返回的 `analysis_results` JSON 数据。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.4 对话会话表设计 (`chat_sessions`)
*   **描述**：存储用户与 AI 的每一次对话会话信息。
*   **结构**：
    *   `id` (UUID, Primary Key): 对话会话 ID。
    *   `user_id` (UUID, Foreign Key to `auth.users.id`): 关联的用户 ID。
    *   `avatar_id` (UUID, Foreign Key to `avatars` table): 本次会话使用的虚拟形象 ID。
    *   `session_start_time` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 会话开始时间。
    *   `session_end_time` (TIMESTAMP WITH TIME ZONE, NULLABLE): 会话结束时间。
    *   `is_active` (BOOLEAN, DEFAULT TRUE): 会话是否活跃。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.5 对话消息表设计 (`chat_messages`)
*   **描述**：存储对话会话中的每一条消息记录。
*   **结构**：
    *   `id` (UUID, Primary Key): 消息 ID。
    *   `session_id` (UUID, Foreign Key to `chat_sessions` table): 关联的对话会话 ID。
    *   `sender_type` (ENUM: 'user', 'ai'): 发送者类型。
    *   `content` (TEXT): 消息内容（用户输入或 AI 响应）。
    *   `timestamp` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 消息发送时间。
    *   `message_type` (ENUM: 'text', 'fortune_card', 'compatibility_card', 'tarot_result', ...): 消息类型，用于前端渲染不同组件。
    *   `related_data` (JSONB, NULLABLE): 与消息相关的结构化数据，例如运势卡片的数据、塔罗牌结果等。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.6 每日运势数据表设计 (`daily_fortunes`)
*   **描述**：存储用户每日运势的计算结果。
*   **结构**：
    *   `id` (UUID, Primary Key): 运势记录 ID。
    *   `user_id` (UUID, Foreign Key to `auth.users.id`): 关联的用户 ID。
    *   `fortune_date` (DATE): 运势所属日期。
    *   `fortune_data` (JSONB): 存储算法返回的运势详细信息。
    *   `generated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 运势生成时间。
    *   `is_pushed` (BOOLEAN, DEFAULT FALSE): 是否已推送给用户。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.7 他人 Profile 表设计 (`other_profiles`)
*   **描述**：存储用户进行合盘时输入的他人信息。
*   **结构**：
    *   `id` (UUID, Primary Key): 他人 Profile ID。
    *   `user_id` (UUID, Foreign Key to `auth.users.id`): 关联到创建此记录的用户 ID。
    *   `name` (TEXT): 他人姓名。
    *   `gender` (ENUM: 'male', 'female', 'secret', 'lgbtq+', NULLABLE): 性别。
    *   `birth_year` (INTEGER): 出生年份。
    *   `birth_month` (INTEGER): 出生月份。
    *   `birth_day` (INTEGER): 出生日期。
    *   `birth_hour` (INTEGER, NULLABLE): 出生小时。
    *   `birth_minute` (INTEGER, NULLABLE): 出生分钟。
    *   `birth_second` (INTEGER, NULLABLE): 出生秒。
    *   `birth_location` (TEXT): 出生地。
    *   `birth_longitude` (NUMERIC, NULLABLE): 出生经度。
    *   `birth_latitude` (NUMERIC, NULLABLE): 出生纬度。
    *   `relation_type` (TEXT, NULLABLE): 与主用户的关系类型（如“伴侣”, “同事”, “朋友”, “亲人”）。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.8 合盘分析结果表设计 (`compatibility_analysis_results`)
*   **描述**：存储合盘分析的详细结果。
*   **结构**：
    *   `id` (UUID, Primary Key): 合盘分析结果 ID。
    *   `user_id_main` (UUID, Foreign Key to `auth.users.id`): 主用户 ID。
    *   `other_profile_id` (UUID, Foreign Key to `other_profiles` table): 关联的他人 Profile ID。
    *   `analysis_data` (JSONB): 存储算法返回的 `compatibility_result` JSON 数据。
    *   `analysis_date` (DATE, DEFAULT NOW()): 分析日期。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.9 定价计划表设计 (`pricing_plans`)
*   **描述**：定义不同付费计划的详细信息。
*   **结构**：
    *   `id` (UUID, Primary Key): 计划 ID。
    *   `name` (TEXT): 计划名称（如“高级对话包”, “年度会员”）。
    *   `description` (TEXT): 计划描述。
    *   `price` (NUMERIC): 价格。
    *   `currency` (TEXT): 货币单位（如“USD”）。
    *   `duration_days` (INTEGER, NULLABLE): 订阅时长（天）。
    *   `features` (JSONB): 包含的功能列表（如`{"unlimited_chat": true, "tarot_draws_per_day": 5}`）。
    *   `is_active` (BOOLEAN, DEFAULT TRUE): 是否活跃。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.10 交易记录表设计 (`transactions`)
*   **描述**：记录所有用户交易，包括充值、购买和退款。
*   **结构**：
    *   `id` (UUID, Primary Key): 交易 ID。
    *   `user_id` (UUID, Foreign Key to `auth.users.id`): 关联的用户 ID。
    *   `plan_id` (UUID, Foreign Key to `pricing_plans` table, NULLABLE): 关联的付费计划 ID。
    *   `amount` (NUMERIC): 交易金额。
    *   `currency` (TEXT): 货币单位。
    *   `transaction_type` (ENUM: 'purchase', 'refund', 'recharge'): 交易类型。
    *   `status` (ENUM: 'pending', 'completed', 'failed', 'refunded'): 交易状态。
    *   `payment_gateway_id` (TEXT, NULLABLE): 支付网关返回的交易 ID。
    *   `payment_method` (TEXT, NULLABLE): 支付方式。
    *   `transaction_time` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 交易时间。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

### 3.11 用户订阅表设计 (`user_subscriptions`)
*   **描述**：记录用户的活跃订阅信息。
*   **结构**：
    *   `id` (UUID, Primary Key): 订阅 ID。
    *   `user_id` (UUID, Foreign Key to `auth.users.id`): 关联的用户 ID。
    *   `plan_id` (UUID, Foreign Key to `pricing_plans` table): 关联的付费计划 ID。
    *   `start_date` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 订阅开始时间。
    *   `end_date` (TIMESTAMP WITH TIME ZONE): 订阅结束时间。
    *   `status` (ENUM: 'active', 'inactive', 'cancelled'): 订阅状态。
    *   `auto_renew` (BOOLEAN, DEFAULT FALSE): 是否自动续订。
    *   `created_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录创建时间。
    *   `updated_at` (TIMESTAMP WITH TIME ZONE, DEFAULT NOW()): 记录更新时间。

## 4. 算法接口设计

### 4.1 用户画像分析接口 (`POST /api/algorithm/user-profile-analysis`)
*   **描述**：接收用户出生信息，返回基础用户分析（如生辰八字、星相基础盘）。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "user_id": "string", // Supabase Auth 用户 ID
        "birth_info": {
            "year": "integer",
            "month": "integer",
            "day": "integer",
            "hour": "integer", // 可选
            "minute": "integer", // 可选
            "second": "integer", // 可选
            "location": "string", // 出生地名称
            "longitude": "number", // 可选
            "latitude": "number" // 可选
        }
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "analysis_results": {
            "birth_chart_traditional": { // 生辰八字
                "heavenly_stems": ["甲", "乙", "丙", "丁"],
                "earthly_branches": ["子", "丑", "寅", "卯"],
                "five_elements_balance": {"wood": "balanced", "fire": "strong", ...},
                "lucky_elements": ["wood", "water"],
                "summary": "根据八字分析，您...",
                "detailed_analysis": { /* 更详细的八字解读 */ }
            },
            "birth_chart_astrology": { // 西方占星基础盘
                "sun_sign": "Leo",
                "moon_sign": "Cancer",
                "rising_sign": "Scorpio",
                "planets_positions": [
                    {"planet": "Mars", "sign": "Aries", "degree": 15},
                    // ...其他行星
                ],
                "aspects": [
                    {"planet1": "Sun", "planet2": "Moon", "type": "trine", "orb": 2},
                    // ...其他相位
                ],
                "houses_cusps": {"house1": "Scorpio", ...},
                "summary": "根据您的星盘，您...",
                "detailed_analysis": { /* 更详细的占星解读 */ }
            },
            "general_insights": [ // 综合洞察
                "您天生具备领导力，但在感情中可能略显强势。",
                "近期需关注肠胃健康，建议多食绿色蔬菜。"
            ]
        }
    }
    ```

### 4.2 对话初始化接口 (`POST /api/algorithm/chat/initiate`)
*   **描述**：根据用户ID和选择的虚拟形象，初始化首次对话内容。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "user_id": "string", // Supabase Auth 用户 ID
        "avatar_id": "string" // 用户选择的虚拟形象 ID
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "session_id": "string", // 新创建的会话 ID
        "initial_message": {
            "sender_type": "ai",
            "content": "string", // AI 的冷启动问候语
            "message_type": "text"
        }
    }
    ```

### 4.3 对话响应接口 (`POST /api/algorithm/chat/respond`)
*   **描述**：接收用户输入、当前对话上下文、用户画像，返回 AI 响应文本及可能的引导操作。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "session_id": "string", // 当前对话会话 ID
        "user_id": "string", // Supabase Auth 用户 ID
        "user_input": "string", // 用户输入的文本
        "user_profile": { /* 用户的出生信息、分析结果等，根据需要传递 */ },
        "conversation_history": [ // 最近N条对话记录，用于模型理解上下文
            {"sender_type": "user", "content": "string"},
            {"sender_type": "ai", "content": "string"}
            // ...
        ]
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "ai_response": {
            "sender_type": "ai",
            "content": "string", // AI 响应文本
            "message_type": "text", // 或 "fortune_card", "compatibility_card", etc.
            "related_data": { /* 如果是特定消息类型，附带的数据 */ }
        },
        "suggested_actions": [ // 可选：建议用户进行的操作，前端可据此展示按钮或引导
            {"type": "fortune_prediction", "text": "要不要算一卦？"},
            {"type": "compatibility_analysis", "text": "想了解和ta的关系吗？"},
            {"type": "tarot_draw", "text": "抽一张塔罗牌？"}
        ],
        "function_call_required": { // 可选：表示 AI 识别到需要调用某个具体算法功能
            "function_name": "string", // 例如 "daily_fortune_calculate", "tarot_draw"
            "parameters": { /* 调用该功能所需的参数 */ }
        }
    }
    ```

### 4.4 运势预测接口 (`POST /api/algorithm/fortune/predict`)
*   **描述**：接收用户请求，触发运势预测（通用接口，可处理每日运势、塔罗、卜卦等）。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "request_type": "string", // 例如 "daily_fortune", "tarot", "divination"
        "date": "string", // YYYY-MM-DD，仅当 request_type 为 daily_fortune 时需要
        "tarot_question": "string", // 仅当 request_type 为 tarot 时需要，用户提问
        "divination_type": "string" // 仅当 request_type 为 divination 时需要，如 "求签", "摇卦"
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "fortune_result": {
            "type": "string", // "daily_fortune", "tarot_reading", "divination_result"
            "summary": "string", // 运势概述或牌面/卦象解读
            "details": { /* 根据类型包含详细信息，例如： */
                "luck_level": "吉/凶/平",
                "suitability": ["宜XX", "忌YY"],
                "lucky_color": "string",
                "lucky_number": "integer",
                "tarot_cards": [{"name": "string", "meaning": "string", "image_url": "string", "is_reversed": "boolean", "position_meaning": "string"}], // 塔罗牌结果
                "divination_output": "string", // 签文或卦象
                "explanation": "string", // 深度解读
                "actionable_advice": ["string"] // 可执行建议
            }
        }
    }
    ```

### 4.5 合盘分析接口 (`POST /api/algorithm/compatibility/calculate`)
*   **描述**：接收两个用户的ID及必要信息，返回关系预测与建议（短中长期）。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "user_id_main": "string", // 主用户 Supabase Auth ID
        "main_profile_birth_info": { /* 主用户出生信息 */ },
        "main_profile_analysis_data": { /* 主用户画像分析结果，可选 */ },
        "other_profile_id": "string", // 他人 Profile ID (如果已存在于 other_profiles 表)
        "other_profile_birth_info": { /* 他人出生信息，如果未传入 other_profile_id */
            "name": "string",
            "gender": "string",
            "birth_year": "integer",
            "birth_month": "integer",
            "birth_day": "integer",
            "birth_hour": "integer", // 可选
            "birth_minute": "integer", // 可选
            "birth_second": "integer", // 可选
            "birth_location": "string",
            "birth_longitude": "number", // 可选
            "birth_latitude": "number" // 可选
        },
        "analysis_depth": "string" // "short_term", "medium_term", "long_term", "all"
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "main_user_id": "string",
        "other_profile_id": "string", // 如果通过 ID 传入则返回
        "other_name": "string", // 如果直接传入他人信息则返回姓名
        "compatibility_result": {
            "overall_score": "number", // 0-100
            "aspect_scores": {
                "emotional_connection": "number", // 情感连接得分
                "communication_style": "number", // 沟通风格得分
                "values_alignment": "number", // 价值观匹配得分
                "conflict_resolution": "number" // 冲突解决得分
            },
            "relationship_overview": "string", // 概述
            "short_term_outlook": "string", // 短期预测
            "medium_term_outlook": "string", // 中期预测
            "long_term_outlook": "string", // 长期预测
            "strengths": ["string"], // 关系中的优势
            "challenges": ["string"], // 关系中的挑战
            "actionable_advice": ["string"], // 针对性建议
            "detailed_analysis": { /* 更详细的合盘分析数据 */ }
        }
    }
    ```

### 4.6 每日运势计算接口 (`POST /api/algorithm/daily-fortune/calculate`)
*   **描述**：接收用户ID、当天日期、用户画像，返回当天的运势详细信息。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "user_id": "string", // Supabase Auth 用户 ID
        "date": "string", // YYYY-MM-DD
        "user_profile": { /* 用户的出生信息、分析结果等 */ }
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "fortune_date": "string", // YYYY-MM-DD
        "fortune_details": {
            "luck_level": "string", // "吉", "凶", "平"
            "suitability": ["string"], // "宜XX", "忌YY"
            "lucky_color": "string",
            "lucky_number": "integer",
            "general_summary": "string" // 一段话概括
        }
    }
    ```

### 4.7 塔罗牌抽取接口 (`POST /api/algorithm/tarot/draw`)
*   **描述**：触发塔罗牌抽取，返回结果及解读。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "question": "string", // 用户提出的具体问题
        "draw_method": "string", // 例如 "three_card_spread", "celtic_cross"
        "user_profile": { /* 用户的出生信息、分析结果等 */ }
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "drawn_cards": [
            {"name": "string", "meaning_upright": "string", "meaning_reversed": "string", "image_url": "string", "is_reversed": "boolean", "position_meaning": "string"},
            // ... 更多牌
        ],
        "interpretation": "string", // 对牌阵的综合解读
        "actionable_advice": ["string"] // 可执行建议
    }
    ```

### 4.8 抽签卜卦接口 (`POST /api/algorithm/divination/draw`)
*   **描述**：触发抽签卜卦，返回结果及解读。
*   **请求参数 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "divination_type": "string", // 例如 "求签", "摇卦", "金钱卦"
        "question": "string", // 用户提出的具体问题
        "user_profile": { /* 用户的出生信息、分析结果等 */ }
    }
    ```
*   **响应示例 (JSON Body)**:
    ```json
    {
        "user_id": "string",
        "divination_output": { // 签文或卦象信息
            "text": "string", // 签文或卦辞
            "image_url": "string", // 如果有卦象图等
            "verse": "string", // 签诗
            "explanation": "string", // 解签/卦象解读
            "judgment": "string", // 吉凶判断
            "actionable_advice": ["string"] // 可执行建议
        }
    }
    ``` 