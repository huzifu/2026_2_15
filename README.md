# AI 智能教学助手系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

一个基于 Python + Tkinter + SQLite 开发的智能教学辅助系统，支持作业管理、自动评分、学情分析等功能。

![系统截图](docs/screenshot.png)

## ✨ 特性亮点

- 🎯 **多角色支持** - 教师、学生、管理员三种角色
- 🔒 **安全可靠** - SHA256 密码加密，SQL 注入防护
- 🤖 **AI 智能评分** - 基于 TF-IDF 和余弦相似度的主观题评分
- 📊 **数据分析** - 丰富的统计图表和学情分析
- 📝 **多种题型** - 支持单选、多选、判断、填空、主观题
- 🎨 **现代化界面** - 基于 ttkbootstrap 的美观 UI
- 📦 **轻量级部署** - 无需复杂配置，开箱即用

## 功能特性

### 用户管理
- 多角色支持（教师、学生、管理员）
- 安全的密码加密存储（SHA256）
- 用户注册与登录验证

### 作业管理
- 创建、编辑、删除作业
- 支持多种题型：
  - 单选题
  - 多选题
  - 判断题
  - 填空题
  - 主观题

### 智能评分
- 客观题自动评分
- 主观题 AI 智能评分（基于 TF-IDF 和余弦相似度）
- 教师可手动调整主观题分数

### 学情分析
- 作业统计（平均分、及格率等）
- 题目难度分析
- 学生成绩排名
- 分数分布图表

## 技术栈

- **语言**: Python 3.8+
- **GUI**: Tkinter / ttkbootstrap
- **数据库**: SQLite
- **AI 评分**: scikit-learn, jieba
- **数据分析**: pandas, matplotlib

## 🚀 快速开始

### 方式一：一键安装（推荐）

Windows:
```bash
install.bat
run.bat
```

Linux/Mac:
```bash
chmod +x install.sh run.sh
./install.sh
./run.sh
```

### 方式二：手动安装

1. 克隆项目
```bash
git clone <repository-url>
cd teaching-assistant-system
```

2. 创建虚拟环境（可选）
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行程序
```bash
python main.py
```

### 生成测试数据（可选）

```bash
python scripts/generate_test_data.py
```

## 默认账号

系统预置了以下测试账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| teacher1 | 123456 | 教师 |
| student1 | 123456 | 学生 |

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
│   ├── login_frame.py
│   ├── teacher_dashboard.py
│   ├── student_dashboard.py
│   ├── assignment_frames.py
│   ├── student_frames.py
│   └── analytics_frame.py
├── tests/                # 测试模块
│   ├── test_auth.py
│   └── test_ai_grader.py
├── data/                 # 数据目录
│   └── teaching_assistant.db
└── logs/                 # 日志目录
    └── app.log
```

## 📖 使用指南

### 教师端功能

| 功能 | 说明 |
|------|------|
| 作业管理 | 创建、编辑、删除作业 |
| 题目管理 | 添加多种题型，设置分值和解析 |
| 查看提交 | 查看学生提交记录和答题详情 |
| 手动评分 | 调整主观题分数和评语 |
| 学情分析 | 查看统计图表、排名、分数分布 |

### 学生端功能

| 功能 | 说明 |
|------|------|
| 我的作业 | 查看可用作业列表 |
| 在线答题 | 完成作业并提交 |
| 历史提交 | 查看成绩和 AI 反馈 |
| 成绩统计 | 查看个人学习情况 |

详细使用说明请查看 [快速开始指南](docs/QUICKSTART.md)

## 🛠️ 开发指南

### 运行测试

```bash
python run_tests.py
```

### 代码规范

- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串
- 添加单元测试

### 项目文档

- [系统架构](docs/ARCHITECTURE.md) - 了解系统设计
- [API 文档](docs/API.md) - 查看接口说明
- [开发指南](docs/DEVELOPMENT.md) - 参与开发
- [更新日志](CHANGELOG.md) - 查看版本历史

### 添加新功能

1. 创建功能分支
2. 实现功能代码
3. 编写单元测试
4. 更新文档
5. 提交 Pull Request

详细开发说明请查看 [开发指南](docs/DEVELOPMENT.md)

## 🔐 安全建议

- ⚠️ 生产环境请修改默认账号密码
- 💾 定期备份数据库文件（`data/teaching_assistant.db`）
- 🔑 考虑使用更强的密码加密算法（如 bcrypt）
- 🌐 部署为 Web 应用时添加 HTTPS 支持
- 📝 定期查看日志文件（`logs/app.log`）

## 🐛 常见问题

### Q: 忘记密码怎么办？
A: 可以直接修改数据库或联系管理员重置。

### Q: 如何备份数据？
A: 复制 `data/teaching_assistant.db` 文件即可。

### Q: 主观题评分不准确？
A: AI 评分仅供参考，教师可以手动调整分数。

### Q: 支持多少用户？
A: SQLite 理论上支持数千用户，建议小班教学使用（<100人）。

更多问题请查看 [FAQ](docs/FAQ.md) 或提交 Issue。

## 📊 系统要求

- Python 3.8 或更高版本
- Windows / Linux / macOS
- 至少 100MB 磁盘空间
- 建议 2GB 以上内存

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) - 现代化 Tkinter 主题
- [scikit-learn](https://scikit-learn.org/) - 机器学习库
- [jieba](https://github.com/fxsjy/jieba) - 中文分词

## 📮 联系方式

- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮件: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给个 Star！
