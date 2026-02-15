import sqlite3
import os
from config import DB_PATH, SQL_SCRIPT_PATH

class DBManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 允许通过列名访问
        return conn

    def init_db(self):
        """初始化数据库"""
        if not os.path.exists(SQL_SCRIPT_PATH):
            print(f"Error: SQL script not found at {SQL_SCRIPT_PATH}")
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 读取 SQL 脚本
            with open(SQL_SCRIPT_PATH, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # 执行脚本
            cursor.executescript(sql_script)
            conn.commit()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Database initialization failed: {e}")
        finally:
            if conn:
                conn.close()

    def execute_query(self, query, params=()):
        """执行查询语句 (SELECT)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Query execution failed: {e}")
            return []
        finally:
            conn.close()

    def execute_update(self, query, params=()):
        """执行更新语句 (INSERT, UPDATE, DELETE)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Update execution failed: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

if __name__ == "__main__":
    db = DBManager()
