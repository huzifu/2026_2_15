import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据存储目录
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 数据库路径
DB_PATH = os.path.join(DATA_DIR, 'teaching_assistant.db')

# SQL 脚本路径
SQL_SCRIPT_PATH = os.path.join(BASE_DIR, 'start.sql')

# UI 配置
WINDOW_TITLE = "AI 智能教学助手系统"
WINDOW_SIZE = "1024x768"
THEME_NAME = "cosmo" # ttkbootstrap theme
