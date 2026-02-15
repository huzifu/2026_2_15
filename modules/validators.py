"""
数据验证工具模块
"""
import re
from datetime import datetime

class Validator:
    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, ""
        return False, "邮箱格式不正确"

    @staticmethod
    def validate_score(score, max_score):
        """验证分数"""
        try:
            score = float(score)
            if score < 0:
                return False, "分数不能为负数"
            if score > max_score:
                return False, f"分数不能超过满分 {max_score}"
            return True, ""
        except ValueError:
            return False, "分数必须是数字"

    @staticmethod
    def validate_date(date_str):
        """验证日期格式 YYYY-MM-DD HH:MM:SS"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return True, ""
        except ValueError:
            return False, "日期格式不正确，应为 YYYY-MM-DD HH:MM:SS"

    @staticmethod
    def validate_not_empty(value, field_name="字段"):
        """验证非空"""
        if not value or (isinstance(value, str) and len(value.strip()) == 0):
            return False, f"{field_name}不能为空"
        return True, ""

    @staticmethod
    def sanitize_input(text):
        """清理输入，防止SQL注入（额外保护层）"""
        if not text:
            return ""
        # 移除潜在危险字符
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
        sanitized = str(text)
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized.strip()
