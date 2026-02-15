"""
自定义异常类
"""

class DatabaseError(Exception):
    """数据库操作异常"""
    pass

class AuthenticationError(Exception):
    """认证异常"""
    pass

class ValidationError(Exception):
    """数据验证异常"""
    pass

class PermissionError(Exception):
    """权限异常"""
    pass

class ResourceNotFoundError(Exception):
    """资源不存在异常"""
    pass
