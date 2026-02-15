"""
认证模块测试
"""
import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.auth import AuthManager
from modules.db_manager import DBManager

class TestAuthManager(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.db = DBManager()
        self.auth = AuthManager(self.db)

    def test_password_hashing(self):
        """测试密码加密"""
        password = "test123"
        hashed = self.auth.hash_password(password)
        self.assertIsNotNone(hashed)
        self.assertNotEqual(password, hashed)
        self.assertEqual(len(hashed), 64)  # SHA256 输出64位十六进制

    def test_validate_username(self):
        """测试用户名验证"""
        # 有效用户名
        valid, msg = self.auth.validate_username("test_user123")
        self.assertTrue(valid)
        
        # 太短
        valid, msg = self.auth.validate_username("abc")
        self.assertFalse(valid)
        
        # 包含特殊字符
        valid, msg = self.auth.validate_username("test@user")
        self.assertFalse(valid)

    def test_validate_password(self):
        """测试密码验证"""
        # 有效密码
        valid, msg = self.auth.validate_password("123456")
        self.assertTrue(valid)
        
        # 太短
        valid, msg = self.auth.validate_password("12345")
        self.assertFalse(valid)

if __name__ == '__main__':
    unittest.main()
