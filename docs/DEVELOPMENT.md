# 开发指南

## 开发环境搭建

### 1. 克隆项目
```bash
git clone <repository-url>
cd teaching-assistant-system
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行测试
```bash
python run_tests.py
```

## 项目结构

```
.
├── main.py                 # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── start.sql             # 数据库初始化脚本
├── modules/              # 核心模块
│   ├── auth.py          # 认证管理
│   ├── db_manager.py    # 数据库管理
│   ├── models.py        # 数据模型
│   ├── ai_grader.py     # AI 评分
│   ├── validators.py    # 数据验证
│   ├── exceptions.py    # 自定义异常
│   ├── logger.py        # 日志配置
│   ├── assignment_service.py   # 作业服务
│   ├── submission_service.py   # 提交服务
│   └── analytics_service.py    # 分析服务
├── ui/                   # 界面模块
├── tests/                # 测试模块
├── utils/                # 工具模块
├── docs/                 # 文档
├── data/                 # 数据目录
└── logs/                 # 日志目录
```

## 编码规范

### Python 代码风格
遵循 PEP 8 规范：
- 使用 4 空格缩进
- 类名使用 PascalCase
- 函数名使用 snake_case
- 常量使用 UPPER_CASE
- 每行不超过 120 字符

### 文档字符串
```python
def function_name(param1, param2):
    """
    函数简短描述
    
    详细描述（可选）
    
    参数:
        param1: 参数1说明
        param2: 参数2说明
    
    返回:
        返回值说明
    
    异常:
        ExceptionType: 异常说明
    """
    pass
```

### 注释规范
- 使用中文注释
- 复杂逻辑必须添加注释
- 避免无意义的注释

## 添加新功能

### 1. 创建服务模块

在 `modules/` 目录下创建新的服务类：

```python
# modules/new_service.py
import logging
from modules.db_manager import DBManager

logger = logging.getLogger(__name__)

class NewService:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
    
    def new_method(self):
        """新功能实现"""
        pass
```

### 2. 创建 UI 组件

在 `ui/` 目录下创建界面组件：

```python
# ui/new_frame.py
import tkinter as tk
from tkinter import ttk

class NewFrame(ttk.Frame):
    def __init__(self, parent, user, db_manager):
        super().__init__(parent)
        self.user = user
        self.db = db_manager
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面元素"""
        pass
```

### 3. 编写测试

在 `tests/` 目录下创建测试文件：

```python
# tests/test_new_service.py
import unittest
from modules.new_service import NewService

class TestNewService(unittest.TestCase):
    def test_new_method(self):
        """测试新方法"""
        pass
```

### 4. 更新文档

- 更新 README.md
- 更新 API.md
- 更新 CHANGELOG.md

## 数据库操作

### 添加新表

1. 修改 `start.sql`：
```sql
CREATE TABLE IF NOT EXISTS new_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field1 TEXT NOT NULL,
    field2 INTEGER
);
```

2. 创建对应的模型类：
```python
# modules/models.py
class NewModel:
    def __init__(self, id, field1, field2):
        self.id = id
        self.field1 = field1
        self.field2 = field2
    
    @staticmethod
    def from_row(row):
        return NewModel(
            id=row['id'],
            field1=row['field1'],
            field2=row['field2']
        )
```

3. 删除旧数据库，重新初始化：
```bash
rm data/teaching_assistant.db
python main.py
```

## 调试技巧

### 1. 查看日志
```bash
tail -f logs/app.log
```

### 2. 使用 Python 调试器
```python
import pdb; pdb.set_trace()
```

### 3. 数据库查询
```bash
sqlite3 data/teaching_assistant.db
.tables
SELECT * FROM user;
```

## 性能优化

### 1. 数据库索引
```sql
CREATE INDEX idx_assignment_teacher ON assignment(teacher_id);
CREATE INDEX idx_submission_student ON submission(student_id);
```

### 2. 批量操作
使用 `execute_many` 代替循环插入：
```python
params_list = [(val1, val2), (val3, val4)]
db.execute_many(query, params_list)
```

### 3. 缓存查询结果
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user(user_id):
    # 查询用户
    pass
```

## 常见问题

### Q: 如何切换数据库？
A: 修改 `config.py` 中的 `DB_PATH`，或实现新的 DBManager。

### Q: 如何添加新的题型？
A: 
1. 修改 `start.sql` 中的 CHECK 约束
2. 在 `AIGrader` 中添加评分逻辑
3. 更新 UI 组件

### Q: 如何部署到生产环境？
A: 
1. 使用更强的密码加密（bcrypt）
2. 配置 HTTPS
3. 使用生产级数据库（PostgreSQL）
4. 添加日志监控
5. 定期备份数据

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 代码审查清单

- [ ] 代码符合 PEP 8 规范
- [ ] 添加了必要的注释和文档字符串
- [ ] 编写了单元测试
- [ ] 测试全部通过
- [ ] 更新了相关文档
- [ ] 没有引入新的安全漏洞
- [ ] 性能没有明显下降

## 发布流程

1. 更新版本号（config.py）
2. 更新 CHANGELOG.md
3. 运行所有测试
4. 创建 Git 标签
5. 打包发布

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```
