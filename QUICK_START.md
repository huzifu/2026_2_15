# 智能教学管理系统 - 快速开始指南

## 🚀 5分钟快速部署

### 系统要求
- **操作系统**: Windows 10+/Linux/macOS
- **Python版本**: 3.8 或更高版本
- **内存**: 至少 4GB（推荐 8GB）
- **磁盘空间**: 至少 10GB 可用空间

### 第一步：下载项目
```bash
# 克隆项目（如果有Git）
git clone <项目地址>
cd teaching-management-system

# 或者直接下载ZIP包并解压
```

### 第二步：一键安装（推荐）

#### Windows 用户
1. 双击运行 `install.bat`
2. 等待依赖安装完成
3. 双击运行 `run.bat` 启动系统

#### Linux/macOS 用户
```bash
# 给脚本添加执行权限
chmod +x install.sh run.sh

# 运行安装脚本
./install.sh

# 启动系统
./run.sh
```

### 第三步：手动安装（可选）

如果一键安装失败，可以手动安装：

```bash
# 1. 创建虚拟环境（推荐）
python -m venv .venv

# Windows 激活
.venv\Scripts\activate

# Linux/macOS 激活
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 检查系统环境
python scripts/check_system.py

# 4. 生成测试数据（可选）
python scripts/generate_test_data.py

# 5. 启动系统
python main.py
```

## 👥 默认测试账号

系统预置了以下测试账号，方便快速体验：

### 管理员账号
- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: 系统管理员
- **权限**: 所有功能

### 教师账号
- **用户名**: `teacher1`
- **密码**: `123456`
- **角色**: 教师
- **昵称**: 张老师

- **用户名**: `teacher2`
- **密码**: `123456`
- **角色**: 教师
- **昵称**: 王老师

### 学生账号
- **用户名**: `student1`
- **密码**: `123456`
- **角色**: 学生
- **昵称**: 李同学

- **用户名**: `student2`
- **密码**: `123456`
- **角色**: 学生
- **昵称**: 张同学

- **用户名**: `student3`
- **密码**: `123456`
- **角色**: 学生
- **昵称**: 王同学

## 🎯 快速体验流程

### 1. 教师端体验（2分钟）

1. **登录教师账号**
   - 用户名: `teacher1`
   - 密码: `123456`

2. **创建班级**
   - 点击左侧菜单"班级管理"
   - 点击"新建班级"按钮
   - 填写班级信息：
     - 名称: "Python编程班"
     - 描述: "Python基础编程教学"
     - 人数限制: 50

3. **创建课程**
   - 点击"课程管理"
   - 点击"新建课程"
   - 填写课程信息：
     - 标题: "Python基础编程"
     - 描述: "Python语法和基础编程"
     - 选择刚创建的班级

4. **布置作业**
   - 点击"作业管理"
   - 点击"新建作业"
   - 填写作业信息：
     - 标题: "Python基础测试"
     - 类型: "作业"
     - 总分: 100
     - 截止时间: 7天后

### 2. 学生端体验（2分钟）

1. **登录学生账号**
   - 用户名: `student1`
   - 密码: `123456`

2. **查看课程**
   - 点击"我的课程"
   - 查看可用课程列表
   - 点击课程进入学习

3. **完成作业**
   - 点击"我的作业"
   - 找到"Python基础测试"
   - 点击"开始答题"
   - 完成题目并提交

4. **查看成绩**
   - 点击"我的成绩"
   - 查看作业成绩和反馈
   - 查看学习进度

### 3. 讨论区体验（1分钟）

1. **教师发布讨论**
   - 教师登录后点击"讨论区"
   - 点击"新建帖子"
   - 发布一个学习问题

2. **学生参与讨论**
   - 学生登录后点击"讨论区"
   - 查看教师发布的帖子
   - 点击"回复"参与讨论

## 📊 核心功能速览

### 教师端功能
- **班级管理**: 创建、编辑、删除班级，管理学生
- **课程管理**: 创建课程、添加章节、上传资源
- **作业管理**: 布置作业、添加题目、设置截止时间
- **成绩管理**: 批改作业、录入成绩、生成成绩单
- **学情分析**: 查看学生学习进度、成绩分析
- **讨论区**: 发布讨论、回答问题、管理帖子

### 学生端功能
- **课程学习**: 查看课程、学习内容、跟踪进度
- **作业完成**: 在线答题、提交作业、查看反馈
- **成绩查询**: 查看成绩、成绩分析、学习报告
- **资源下载**: 下载学习资料、课件、视频
- **讨论参与**: 提问、回答、参与学习讨论
- **个人中心**: 查看通知、修改资料、学习统计

### 管理员功能
- **用户管理**: 管理所有用户账号
- **系统设置**: 配置系统参数、功能开关
- **数据管理**: 数据备份、恢复、清理
- **系统监控**: 查看系统状态、日志、性能

## 🔧 常见问题解决

### Q: 安装依赖失败怎么办？
**A:** 尝试以下解决方案：
1. 升级pip: `python -m pip install --upgrade pip`
2. 使用国内镜像源：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
3. 手动安装主要依赖：
   ```bash
   pip install ttkbootstrap matplotlib pandas scikit-learn jieba
   ```

### Q: 启动时提示缺少模块？
**A:** 运行环境检查脚本：
```bash
python scripts/check_system.py
```
根据提示安装缺失的模块。

### Q: 数据库初始化失败？
**A:** 删除旧数据库文件重新初始化：
```bash
# 删除数据库文件
rm data/teaching_assistant.db

# 重新启动系统
python main.py
```

### Q: 界面显示异常？
**A:** 尝试以下方法：
1. 安装ttkbootstrap: `pip install ttkbootstrap`
2. 使用标准Tkinter主题
3. 检查Python和Tkinter版本

### Q: 如何添加新用户？
**A:** 有以下几种方式：
1. 使用注册功能（如果启用）
2. 管理员在用户管理中添加
3. 直接修改数据库（不推荐）

## 📁 项目结构说明

```
teaching-management-system/
├── main.py                    # 主程序入口
├── config.py                  # 配置文件
├── requirements.txt           # 依赖列表
├── start.sql                  # 数据库初始化脚本
├── README.md                  # 项目说明
├── QUICK_START.md            # 快速开始指南
├── FEATURES.md               # 功能清单
├── install.bat               # Windows安装脚本
├── install.sh                # Linux/macOS安装脚本
├── run.bat                   # Windows启动脚本
├── run.sh                    # Linux/macOS启动脚本
│
├── modules/                  # 核心模块
│   ├── auth.py              # 认证管理
│   ├── db_manager.py        # 数据库管理
│   ├── models.py            # 数据模型
│   ├── class_service.py     # 班级服务
│   ├── course_service.py    # 课程服务
│   ├── assignment_service.py # 作业服务
│   ├── submission_service.py # 提交服务
│   ├── discussion_service.py # 讨论服务
│   ├── notification_service.py # 通知服务
│   ├── gradebook_service.py # 成绩服务
│   ├── analytics_service.py # 分析服务
│   ├── ai_grader.py         # AI评分
│   ├── validators.py        # 数据验证
│   ├── exceptions.py        # 异常处理
│   └── logger.py            # 日志配置
│
├── ui/                       # 界面模块
│   ├── components.py        # 通用组件
│   ├── login_frame.py       # 登录界面
│   ├── teacher_dashboard.py # 教师仪表板
│   ├── student_dashboard.py # 学生仪表板
│   ├── admin_dashboard.py   # 管理员仪表板
│   └── dialogs/             # 对话框
│
├── scripts/                  # 工具脚本
│   ├── check_system.py      # 系统检查
│   ├── generate_test_data.py # 测试数据生成
│   └── run_tests.py         # 测试运行
│
├── docs/                     # 文档
│   ├── SYSTEM_ARCHITECTURE.md # 系统架构
│   ├── API.md               # API文档
│   ├── DEVELOPMENT.md       # 开发指南
│   └── FAQ.md               # 常见问题
│
├── data/                     # 数据目录
│   └── teaching_assistant.db # 数据库文件
│
├── logs/                     # 日志目录
│   └── app.log              # 应用日志
│
├── uploads/                  # 上传文件目录
└── temp/                     # 临时文件目录
```

## 🆘 获取帮助

### 在线文档
- **用户手册**: 查看 `docs/` 目录
- **API文档**: `docs/API.md`
- **开发指南**: `docs/DEVELOPMENT.md`
- **常见问题**: `docs/FAQ.md`

### 技术支持
1. **查看日志**: `logs/app.log`
2. **运行诊断**: `python scripts/check_system.py`
3. **生成测试数据**: `python scripts/generate_test_data.py`
4. **运行测试**: `python scripts/run_tests.py`

### 联系支持
- **问题反馈**: 提交Issue
- **功能建议**: 提交Feature Request
- **紧急问题**: 查看日志文件

## 🎉 下一步

### 基础使用
1. 熟悉教师端和学生端界面
2. 创建几个测试班级和课程
3. 布置一些作业让学生完成
4. 体验成绩管理和学情分析

### 高级功能
1. 配置系统设置和通知规则
2. 使用AI自动评分功能
3. 导出成绩报表和学习报告
4. 设置数据备份和恢复

### 生产部署
1. 修改默认账号密码
2. 配置数据库备份策略
3. 设置系统监控和告警
4. 进行性能测试和优化

---

**系统状态**: ✅ 完整可用  
**版本**: v2.0.0  
**最后更新**: 2024-02-15  
**许可证**: MIT开源许可证  

祝您使用愉快！🎊