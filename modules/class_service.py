"""
班级管理服务
"""
import logging
from typing import List, Dict, Any, Optional
from modules.models import Class, User
from modules.exceptions import ValidationError, ResourceNotFoundError, PermissionError

logger = logging.getLogger(__name__)

class ClassService:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_class(self, name: str, description: str, teacher_id: int, 
                    max_students: int = 50, code: str = None) -> int:
        """创建班级"""
        if not name or len(name.strip()) < 2:
            raise ValidationError("班级名称至少需要2个字符")
        
        if max_students < 1 or max_students > 200:
            raise ValidationError("班级人数限制应在1-200之间")
        
        # 生成班级代码（如果未提供）
        if not code:
            import random
            import string
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # 检查代码是否唯一
        check_query = "SELECT id FROM class WHERE code = ?"
        if self.db.execute_query(check_query, (code,)):
            raise ValidationError("班级代码已存在，请使用其他代码")
        
        query = """
            INSERT INTO class (name, code, description, teacher_id, max_students)
            VALUES (?, ?, ?, ?, ?)
        """
        class_id = self.db.execute_update(
            query, (name.strip(), code, description.strip(), teacher_id, max_students)
        )
        
        if class_id:
            logger.info(f"Class created: {class_id} by teacher {teacher_id}")
            return class_id
        raise ValidationError("创建班级失败")

    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """根据ID获取班级"""
        query = """
            SELECT c.*, u.nickname as teacher_name
            FROM class c
            LEFT JOIN user u ON c.teacher_id = u.id
            WHERE c.id = ?
        """
        rows = self.db.execute_query(query, (class_id,))
        if rows:
            return Class.from_row(rows[0])
        return None

    def get_classes_by_teacher(self, teacher_id: int) -> List[Class]:
        """获取教师的所有班级"""
        query = """
            SELECT c.*, 
                   (SELECT COUNT(*) FROM class_member WHERE class_id = c.id AND status = 'active') as student_count
            FROM class c
            WHERE c.teacher_id = ? AND c.status != 'archived'
            ORDER BY c.created_at DESC
        """
        rows = self.db.execute_query(query, (teacher_id,))
        return [Class.from_row(row) for row in rows]

    def update_class(self, class_id: int, name: str = None, description: str = None,
                    max_students: int = None, status: str = None) -> bool:
        """更新班级信息"""
        updates = []
        params = []
        
        if name:
            if len(name.strip()) < 2:
                raise ValidationError("班级名称至少需要2个字符")
            updates.append("name = ?")
            params.append(name.strip())
        
        if description is not None:
            updates.append("description = ?")
            params.append(description.strip())
        
        if max_students:
            if max_students < 1 or max_students > 200:
                raise ValidationError("班级人数限制应在1-200之间")
            updates.append("max_students = ?")
            params.append(max_students)
        
        if status:
            if status not in ['active', 'archived', 'closed']:
                raise ValidationError("无效的班级状态")
            updates.append("status = ?")
            params.append(status)
        
        if not updates:
            return True
        
        query = f"UPDATE class SET {', '.join(updates)} WHERE id = ?"
        params.append(class_id)
        
        result = self.db.execute_update(query, tuple(params))
        if result is not None:
            logger.info(f"Class updated: {class_id}")
            return True
        return False

    def delete_class(self, class_id: int) -> bool:
        """删除班级（软删除）"""
        query = "UPDATE class SET status = 'archived' WHERE id = ?"
        result = self.db.execute_update(query, (class_id,))
        if result is not None:
            logger.info(f"Class archived: {class_id}")
            return True
        return False

    def add_student_to_class(self, class_id: int, student_id: int) -> bool:
        """添加学生到班级"""
        # 检查班级是否存在且未满
        class_info = self.get_class_by_id(class_id)
        if not class_info:
            raise ResourceNotFoundError(f"班级不存在: {class_id}")
        
        if class_info.status != 'active':
            raise ValidationError("班级未激活")
        
        # 检查学生是否已经是班级成员
        check_query = """
            SELECT id FROM class_member 
            WHERE class_id = ? AND student_id = ? AND status = 'active'
        """
        if self.db.execute_query(check_query, (class_id, student_id)):
            raise ValidationError("学生已经在班级中")
        
        # 检查班级人数限制
        count_query = """
            SELECT COUNT(*) as count FROM class_member 
            WHERE class_id = ? AND status = 'active'
        """
        count_rows = self.db.execute_query(count_query, (class_id,))
        current_count = count_rows[0]['count'] if count_rows else 0
        
        if current_count >= class_info.max_students:
            raise ValidationError("班级人数已满")
        
        # 添加学生
        query = """
            INSERT INTO class_member (class_id, student_id, status)
            VALUES (?, ?, 'active')
        """
        result = self.db.execute_update(query, (class_id, student_id))
        if result is not None:
            logger.info(f"Student {student_id} added to class {class_id}")
            return True
        return False

    def remove_student_from_class(self, class_id: int, student_id: int) -> bool:
        """从班级移除学生"""
        query = """
            UPDATE class_member 
            SET status = 'removed' 
            WHERE class_id = ? AND student_id = ? AND status = 'active'
        """
        result = self.db.execute_update(query, (class_id, student_id))
        if result is not None:
            logger.info(f"Student {student_id} removed from class {class_id}")
            return True
        return False

    def get_class_students(self, class_id: int) -> List[Dict[str, Any]]:
        """获取班级学生列表"""
        query = """
            SELECT u.id, u.username, u.nickname, u.email, u.avatar,
                   cm.join_date, cm.status as member_status
            FROM class_member cm
            JOIN user u ON cm.student_id = u.id
            WHERE cm.class_id = ? AND cm.status = 'active'
            ORDER BY cm.join_date DESC
        """
        rows = self.db.execute_query(query, (class_id,))
        return [dict(row) for row in rows]

    def get_student_classes(self, student_id: int) -> List[Dict[str, Any]]:
        """获取学生加入的班级"""
        query = """
            SELECT c.*, u.nickname as teacher_name,
                   (SELECT COUNT(*) FROM class_member WHERE class_id = c.id AND status = 'active') as student_count
            FROM class_member cm
            JOIN class c ON cm.class_id = c.id
            JOIN user u ON c.teacher_id = u.id
            WHERE cm.student_id = ? AND cm.status = 'active' AND c.status = 'active'
            ORDER BY cm.join_date DESC
        """
        rows = self.db.execute_query(query, (student_id,))
        return [dict(row) for row in rows]

    def search_classes(self, keyword: str = None, teacher_id: int = None, 
                      status: str = 'active') -> List[Class]:
        """搜索班级"""
        conditions = ["c.status = ?"]
        params = [status]
        
        if keyword:
            conditions.append("(c.name LIKE ? OR c.code LIKE ? OR c.description LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        if teacher_id:
            conditions.append("c.teacher_id = ?")
            params.append(teacher_id)
        
        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT c.*, u.nickname as teacher_name,
                   (SELECT COUNT(*) FROM class_member WHERE class_id = c.id AND status = 'active') as student_count
            FROM class c
            LEFT JOIN user u ON c.teacher_id = u.id
            WHERE {where_clause}
            ORDER BY c.created_at DESC
        """
        
        rows = self.db.execute_query(query, tuple(params))
        return [Class.from_row(row) for row in rows]

    def get_class_statistics(self, class_id: int) -> Dict[str, Any]:
        """获取班级统计信息"""
        # 学生统计
        student_query = """
            SELECT 
                COUNT(*) as total_students,
                COUNT(CASE WHEN u.status = 'active' THEN 1 END) as active_students
            FROM class_member cm
            JOIN user u ON cm.student_id = u.id
            WHERE cm.class_id = ? AND cm.status = 'active'
        """
        student_stats = self.db.execute_query(student_query, (class_id,))
        
        # 作业统计
        assignment_query = """
            SELECT 
                COUNT(*) as total_assignments,
                COUNT(CASE WHEN a.status = 'published' THEN 1 END) as published_assignments,
                COUNT(CASE WHEN a.status = 'graded' THEN 1 END) as graded_assignments
            FROM assignment a
            WHERE a.class_id = ?
        """
        assignment_stats = self.db.execute_query(assignment_query, (class_id,))
        
        # 平均成绩
        grade_query = """
            SELECT AVG(g.score) as average_score
            FROM gradebook g
            JOIN assignment a ON g.assignment_id = a.id
            WHERE a.class_id = ? AND g.score IS NOT NULL
        """
        grade_stats = self.db.execute_query(grade_query, (class_id,))
        
        return {
            'student_stats': dict(student_stats[0]) if student_stats else {},
            'assignment_stats': dict(assignment_stats[0]) if assignment_stats else {},
            'grade_stats': dict(grade_stats[0]) if grade_stats else {}
        }

    def generate_class_code(self) -> str:
        """生成唯一的班级代码"""
        import random
        import string
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            check_query = "SELECT id FROM class WHERE code = ?"
            if not self.db.execute_query(check_query, (code,)):
                return code