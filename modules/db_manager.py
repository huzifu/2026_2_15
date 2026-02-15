import sqlite3
import os
import logging
from contextlib import contextmanager
from config import DB_PATH, SQL_SCRIPT_PATH

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 允许通过列名访问
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def get_connection_context(self):
        """上下文管理器方式获取连接"""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            conn.close()

    def init_db(self):
        """初始化数据库"""
        if not os.path.exists(SQL_SCRIPT_PATH):
            logger.error(f"SQL script not found at {SQL_SCRIPT_PATH}")
            return

        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # 读取 SQL 脚本
                with open(SQL_SCRIPT_PATH, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                
                # 执行脚本
                cursor.executescript(sql_script)
                logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def execute_query(self, query, params=()):
        """执行查询语句 (SELECT)"""
        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {query}, {params}, {e}")
            return []

    def execute_update(self, query, params=()):
        """执行更新语句 (INSERT, UPDATE, DELETE)"""
        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Update execution failed: {query}, {params}, {e}")
            return None

    def execute_many(self, query, params_list):
        """批量执行更新语句"""
        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Batch execution failed: {query}, {e}")
            return None

if __name__ == "__main__":
    db = DBManager()
