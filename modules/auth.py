from modules.db_manager import DBManager
from modules.models import User

class AuthManager:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.current_user = None

    def login(self, username, password):
        """用户登录"""
        query = "SELECT * FROM user WHERE username = ? AND password = ?"
        # 注意：实际生产中应使用哈希比对，这里演示明文/简单存储
        rows = self.db.execute_query(query, (username, password))
        
        if rows:
            self.current_user = User.from_row(rows[0])
            return True, "登录成功"
        else:
            return False, "用户名或密码错误"

    def register(self, username, password, role, nickname):
        """用户注册"""
        # 检查用户名是否已存在
        check_query = "SELECT id FROM user WHERE username = ?"
        if self.db.execute_query(check_query, (username,)):
            return False, "用户名已存在"

        insert_query = "INSERT INTO user (username, password, role, nickname) VALUES (?, ?, ?, ?)"
        try:
            self.db.execute_update(insert_query, (username, password, role, nickname))
            return True, "注册成功"
        except Exception as e:
            return False, f"注册失败: {str(e)}"

    def logout(self):
        """退出登录"""
        self.current_user = None
