# 系统架构文档

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     Presentation Layer                   │
│                    (Tkinter/ttkbootstrap)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Login Frame  │  │   Teacher    │  │   Student    │  │
│  │              │  │  Dashboard   │  │  Dashboard   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     Business Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Assignment   │  │ Submission   │  │  Analytics   │  │
│  │   Service    │  │   Service    │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │     Auth     │  │  AI Grader   │                    │
│  │   Manager    │  │              │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  DB Manager  │  │   Models     │  │  Validators  │  │
│  │              │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    SQLite     │
                    │   Database    │
                    └───────────────┘
```

## 核心模块

### 1. 认证模块 (auth.py)

负责用户认证和授权：
- 用户登录/注册
- 密码加密（SHA256）
- 用户名/密码验证
- 会话管理

### 2. 数据库管理 (db_manager.py)

提供数据库操作接口：
- 连接池管理
- 事务处理
- 查询/更新操作
- 批量操作支持

### 3. 作业服务 (assignment_service.py)

处理作业相关业务：
- 创建/编辑/删除作业
- 题目管理
- 作业查询

### 4. 提交服务 (submission_service.py)

处理作业提交和评分：
- 作业提交
- 自动评分
- 手动评分
- 提交历史查询

### 5. AI 评分引擎 (ai_grader.py)

智能评分算法：
- 客观题精确匹配
- 主观题相似度计算
- TF-IDF + 余弦相似度
- Jaccard 相似度（备用）

### 6. 分析服务 (analytics_service.py)

数据统计和分析：
- 作业统计
- 题目难度分析
- 学生成绩排名
- 分数分布

## 数据模型

### 用户表 (user)
```sql
- id: 主键
- username: 用户名（唯一）
- password: 密码（SHA256加密）
- role: 角色（teacher/student/admin）
- nickname: 昵称
- created_at: 创建时间
```

### 作业表 (assignment)
```sql
- id: 主键
- title: 标题
- description: 描述
- teacher_id: 教师ID（外键）
- deadline: 截止时间
- create_time: 创建时间
```

### 题目表 (question)
```sql
- id: 主键
- assignment_id: 作业ID（外键）
- type: 题型
- content: 内容
- answer: 标准答案
- score: 分值
- analysis: 解析
```

### 提交表 (submission)
```sql
- id: 主键
- student_id: 学生ID（外键）
- assignment_id: 作业ID（外键）
- total_score: 总分
- feedback: 评语
- submit_time: 提交时间
```

### 提交详情表 (submission_detail)
```sql
- id: 主键
- submission_id: 提交ID（外键）
- question_id: 题目ID（外键）
- student_answer: 学生答案
- is_correct: 是否正确
- score: 得分
- ai_feedback: AI反馈
```

## 技术选型

### 前端
- Tkinter: Python 标准 GUI 库
- ttkbootstrap: 现代化主题支持
- matplotlib: 数据可视化

### 后端
- Python 3.8+: 主要开发语言
- SQLite: 轻量级数据库

### AI/ML
- scikit-learn: 机器学习库
- jieba: 中文分词
- numpy: 数值计算

### 工具
- logging: 日志记录
- unittest: 单元测试
- hashlib: 密码加密

## 设计模式

### 1. MVC 模式
- Model: modules/models.py
- View: ui/*.py
- Controller: modules/*_service.py

### 2. 服务层模式
业务逻辑封装在服务类中，提供清晰的 API。

### 3. 单例模式
DBManager 使用单例模式管理数据库连接。

### 4. 策略模式
AI 评分支持多种算法策略（TF-IDF、Jaccard）。

## 安全考虑

### 1. 密码安全
- SHA256 哈希加密
- 建议升级到 bcrypt

### 2. SQL 注入防护
- 参数化查询
- 输入验证和清理

### 3. 数据验证
- 前端验证
- 后端二次验证
- 自定义验证器

### 4. 日志审计
- 操作日志记录
- 错误追踪

## 性能优化

### 1. 数据库优化
- 索引优化
- 批量操作
- 连接池管理

### 2. 缓存策略
- 查询结果缓存
- 静态资源缓存

### 3. 异步处理
- 后台任务队列
- 异步 IO

## 扩展性

### 1. 插件系统
支持自定义评分算法插件。

### 2. API 接口
可扩展为 Web API 服务。

### 3. 多数据库支持
可切换到 MySQL/PostgreSQL。

### 4. 分布式部署
支持多实例部署。

## 未来规划

1. Web 版本（Flask/Django）
2. 移动端应用
3. 实时协作功能
4. 更强大的 AI 评分
5. 视频/音频作业支持
