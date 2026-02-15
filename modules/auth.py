import hashlib
import re
from modules.db_manager import DBManager
from modules.models import User

class AuthManager:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.current_user = None

    @staticmethod
    def hash_password(password):
        """密码哈希加密"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def validate_username(username):
        """验证用户名格式：4-20位字母数字下划线"""
        if not username or len(username) < 4 or len(username) > 20:
            return False, "用户名长度应为4-20位"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "用户名只能包含字母、数字和下划线"
        return True, ""

    @staticmethod
    def validate_password(password):
        """验证密码强度：至少6位"""
        if not password or len(password) < 6:
            return False, "密码长度至少为6位"
        return True, ""

    def login(self, username, password):
        """用户登录"""
        if not username or not password:
            return False, "用户名和密码不能为空"
        
        hashed_password = self.hash_password(password)
        query = "SELECT * FROM user WHERE username = ? AND password = ?"
        rows = self.db.execute_query(query, (username, hashed_password))
        
        if rows:
            self.current_user = User.from_row(rows[0])
            return True, "登录成功"
        else:
            return False, "用户名或密码错误"

    def register(self, username, password, role, nickname):
        """用户注册"""
        # 验证用户名
        valid, msg = self.validate_username(username)
        if not valid:
            return False, msg
        
        # 验证密码
        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg
        
        # 验证昵称
        if not nickname or len(nickname.strip()) == 0:
            return False, "昵称不能为空"
        
        # 检查用户名是否已存在
        check_query = "SELECT id FROM user WHERE username = ?"
        if self.db.execute_query(check_query, (username,)):
            return False, "用户名已存在"

        # 密码加密
        hashed_password = self.hash_password(password)
        
        insert_query = "INSERT INTO user (username, password, role, nickname) VALUES (?, ?, ?, ?)"
        try:
            self.db.execute_update(insert_query, (username, hashed_password, role, nickname.strip()))
            return True, "注册成功"
        except Exception as e:
            return False, f"注册失败: {str(e)}"

    def logout(self):
        """退出登录"""
        self.current_user = None
