import os
import logging
from datetime import timedelta

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据存储目录
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 日志目录
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 上传文件目录
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 临时文件目录
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# 数据库路径
DB_PATH = os.path.join(DATA_DIR, 'teaching_assistant.db')

# SQL 脚本路径
SQL_SCRIPT_PATH = os.path.join(BASE_DIR, 'start.sql')

# 日志配置
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# UI 配置
WINDOW_TITLE = "智能教学管理系统"
WINDOW_SIZE = "1280x800"
THEME_NAME = "cosmo"  # ttkbootstrap theme

# 应用配置
APP_VERSION = "2.0.0"
APP_NAME = "智能教学管理系统"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SESSION_TIMEOUT = timedelta(hours=2)

# AI 评分配置
AI_SIMILARITY_THRESHOLD = 0.6  # 相似度阈值
AI_MIN_SCORE_RATIO = 0.3  # 最低得分比例
AI_MAX_GRADING_TIME = 30  # 最大评分时间（秒）

# 文件上传配置
ALLOWED_EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
    'documents': ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'],
    'videos': ['.mp4', '.avi', '.mov', '.wmv'],
    'audios': ['.mp3', '.wav', '.ogg'],
    'archives': ['.zip', '.rar', '.7z'],
    'code': ['.py', '.java', '.cpp', '.c', '.js', '.html', '.css']
}

# 成绩等级配置
GRADE_SCALE = {
    'A': (90, 100),
    'B': (80, 89),
    'C': (70, 79),
    'D': (60, 69),
    'F': (0, 59)
}

# 系统功能开关
FEATURES = {
    'ai_grading': True,
    'notifications': True,
    'discussion_forum': True,
    'file_upload': True,
    'real_time_messaging': True,
    'analytics_dashboard': True,
    'export_reports': True,
    'multi_language': False,
    'dark_mode': True
}

# 邮件配置（可选）
EMAIL_CONFIG = {
    'enabled': False,
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'use_tls': True,
    'username': '',
    'password': '',
    'from_email': 'noreply@example.com'
}

# 缓存配置
CACHE_CONFIG = {
    'enabled': True,
    'ttl': 300,  # 缓存时间（秒）
    'max_size': 1000  # 最大缓存条目数
}

# 安全配置
SECURITY_CONFIG = {
    'password_min_length': 8,
    'password_require_uppercase': True,
    'password_require_lowercase': True,
    'password_require_digits': True,
    'password_require_special': False,
    'max_login_attempts': 5,
    'lockout_duration': 300,  # 锁定时间（秒）
    'session_secure': True
}

# 通知配置
NOTIFICATION_CONFIG = {
    'assignment_due_reminder': True,
    'grade_posted': True,
    'new_discussion': True,
    'system_announcement': True,
    'reminder_days_before': [1, 3, 7]  # 作业截止前提醒天数
}

# 分析配置
ANALYTICS_CONFIG = {
    'track_learning_progress': True,
    'generate_insights': True,
    'predict_performance': True,
    'recommend_content': True,
    'retention_analysis': True
}

# 导出配置
EXPORT_CONFIG = {
    'formats': ['excel', 'pdf', 'csv', 'json'],
    'include_attachments': True,
    'compress_files': True,
    'watermark': True
}
