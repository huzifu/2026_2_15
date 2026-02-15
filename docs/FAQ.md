# 常见问题 (FAQ)

## 安装和配置

### Q: 如何安装系统？
A: 
1. 确保安装了 Python 3.8+
2. 运行 `install.bat` (Windows) 或 `./install.sh` (Linux/Mac)
3. 或手动执行 `pip install -r requirements.txt`

### Q: 提示缺少某个模块怎么办？
A: 运行 `python scripts/check_system.py` 检查环境，然后安装缺失的包：
```bash
pip install <package-name>
```

### Q: ttkbootstrap 安装失败？
A: ttkbootstrap 不是必需的，系统会自动回退到标准 Tkinter。如果需要安装：
```bash
pip install ttkbootstrap
```

### Q: 在 Linux 上提示找不到 tkinter？
A: 需要安装 Python Tkinter 包：
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

## 使用问题

### Q: 忘记密码怎么办？
A: 有以下几种方法：
1. 使用管理员账号重置（如果有）
2. 直接修改数据库：
```bash
sqlite3 data/teaching_assistant.db
UPDATE user SET password='8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' WHERE username='your_username';
```
（密码会被重置为 123456）

### Q: 如何修改默认账号？
A: 编辑 `start.sql` 文件，修改 INSERT 语句中的用户信息，然后删除数据库重新初始化。

### Q: 如何添加新用户？
A: 
1. 使用注册功能
2. 或直接在数据库中插入（需要手动加密密码）

### Q: 主观题评分不准确？
A: 
- AI 评分基于文本相似度，仅供参考
- 教师可以在作业详情中手动调整分数
- 建议在题目解析中提供详细的评分标准

### Q: 如何导出成绩？
A: 目前系统支持基本的导出功能，可以使用 `utils/export_utils.py` 中的工具：
```python
from utils.export_utils import ExportUtils
ExportUtils.export_to_excel(data, 'grades.xlsx')
```

### Q: 支持批量导入题目吗？
A: 目前不支持，这是计划中的功能。可以通过脚本批量插入数据库。

## 数据管理

### Q: 如何备份数据？
A: 复制以下文件：
- `data/teaching_assistant.db` - 数据库文件
- `logs/app.log` - 日志文件（可选）

### Q: 如何恢复数据？
A: 将备份的数据库文件复制回 `data/` 目录。

### Q: 如何清空所有数据？
A: 删除 `data/teaching_assistant.db` 文件，重新运行程序会自动初始化。

### Q: 数据库文件在哪里？
A: `data/teaching_assistant.db`

### Q: 如何查看数据库内容？
A: 使用 SQLite 客户端：
```bash
sqlite3 data/teaching_assistant.db
.tables
SELECT * FROM user;
```

## 性能问题

### Q: 系统运行缓慢？
A: 
1. 检查数据库大小
2. 定期清理历史数据
3. 考虑添加数据库索引
4. 升级到更强大的数据库（MySQL/PostgreSQL）

### Q: 支持多少学生同时使用？
A: 
- SQLite 理论上支持数千用户
- 建议小班教学使用（<100人）
- 大规模使用建议部署 Web 版本

### Q: AI 评分很慢？
A: 
- 确保安装了 scikit-learn
- 主观题评分需要计算，属于正常现象
- 可以考虑异步处理或批量评分

## 开发问题

### Q: 如何添加新的题型？
A: 
1. 修改 `start.sql` 中的 CHECK 约束
2. 在 `modules/ai_grader.py` 中添加评分逻辑
3. 更新 UI 组件

### Q: 如何修改数据库结构？
A: 
1. 修改 `start.sql`
2. 删除旧数据库
3. 重新运行程序初始化

### Q: 如何运行测试？
A: 
```bash
python run_tests.py
```

### Q: 如何查看日志？
A: 日志文件位于 `logs/app.log`

### Q: 如何切换数据库？
A: 修改 `config.py` 中的 `DB_PATH`，或实现新的 DBManager。

## 部署问题

### Q: 如何部署到服务器？
A: 
1. 当前版本是桌面应用，不适合服务器部署
2. 可以考虑改造为 Web 应用（Flask/Django）
3. 或使用远程桌面方式

### Q: 支持多用户同时登录吗？
A: 当前版本是单机应用，每个实例只能一个用户登录。

### Q: 如何实现多机共享数据？
A: 
1. 使用网络数据库（MySQL/PostgreSQL）
2. 或改造为 Web 应用

## 安全问题

### Q: 密码安全吗？
A: 
- 使用 SHA256 加密存储
- 建议生产环境升级到 bcrypt
- 定期更换密码

### Q: 如何防止 SQL 注入？
A: 系统使用参数化查询，已经有基本防护。

### Q: 数据会丢失吗？
A: 
- 定期备份数据库
- 使用事务处理
- 启用日志记录

## 其他问题

### Q: 支持哪些操作系统？
A: Windows、Linux、macOS 都支持。

### Q: 需要联网吗？
A: 不需要，完全离线运行。

### Q: 有移动端版本吗？
A: 目前没有，这是未来的计划。

### Q: 可以商用吗？
A: 采用 MIT 许可证，可以自由使用和修改。

### Q: 如何获取帮助？
A: 
1. 查看文档
2. 提交 GitHub Issue
3. 发送邮件

---

如果你的问题没有在这里找到答案，请提交 Issue 或联系开发团队。
