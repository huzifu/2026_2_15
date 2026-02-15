"""
作业服务层 - 处理作业相关业务逻辑
"""
import logging
from datetime import datetime
from modules.models import Assignment, Question
from modules.validators import Validator
from modules.exceptions import ValidationError, ResourceNotFoundError

logger = logging.getLogger(__name__)

class AssignmentService:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_assignment(self, title, description, teacher_id, deadline):
        """创建作业"""
        # 验证输入
        valid, msg = Validator.validate_not_empty(title, "作业标题")
        if not valid:
            raise ValidationError(msg)
        
        if deadline:
            valid, msg = Validator.validate_date(deadline)
            if not valid:
                raise ValidationError(msg)
        
        query = """
            INSERT INTO assignment (title, description, teacher_id, deadline)
            VALUES (?, ?, ?, ?)
        """
        assignment_id = self.db.execute_update(query, (title, description, teacher_id, deadline))
        
        if assignment_id:
            logger.info(f"Assignment created: {assignment_id} by teacher {teacher_id}")
            return assignment_id
        raise ValidationError("创建作业失败")

    def get_assignment_by_id(self, assignment_id):
        """根据ID获取作业"""
        query = "SELECT * FROM assignment WHERE id = ?"
        rows = self.db.execute_query(query, (assignment_id,))
        if rows:
            return Assignment.from_row(rows[0])
        raise ResourceNotFoundError(f"作业不存在: {assignment_id}")

    def get_assignments_by_teacher(self, teacher_id):
        """获取教师的所有作业"""
        query = """
            SELECT * FROM assignment 
            WHERE teacher_id = ? 
            ORDER BY create_time DESC
        """
        rows = self.db.execute_query(query, (teacher_id,))
        return [Assignment.from_row(row) for row in rows]

    def get_all_assignments(self):
        """获取所有作业（学生视角）"""
        query = "SELECT * FROM assignment ORDER BY create_time DESC"
        rows = self.db.execute_query(query)
        return [Assignment.from_row(row) for row in rows]

    def update_assignment(self, assignment_id, title, description, deadline):
        """更新作业信息"""
        valid, msg = Validator.validate_not_empty(title, "作业标题")
        if not valid:
            raise ValidationError(msg)
        
        query = """
            UPDATE assignment 
            SET title = ?, description = ?, deadline = ?
            WHERE id = ?
        """
        result = self.db.execute_update(query, (title, description, deadline, assignment_id))
        if result is not None:
            logger.info(f"Assignment updated: {assignment_id}")
            return True
        return False

    def delete_assignment(self, assignment_id):
        """删除作业（级联删除题目）"""
        query = "DELETE FROM assignment WHERE id = ?"
        result = self.db.execute_update(query, (assignment_id,))
        if result is not None:
            logger.info(f"Assignment deleted: {assignment_id}")
            return True
        return False

    def add_question(self, assignment_id, question_type, content, answer, score, analysis=""):
        """添加题目"""
        valid, msg = Validator.validate_not_empty(content, "题目内容")
        if not valid:
            raise ValidationError(msg)
        
        valid, msg = Validator.validate_score(score, 1000)
        if not valid:
            raise ValidationError(msg)
        
        query = """
            INSERT INTO question (assignment_id, type, content, answer, score, analysis)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        question_id = self.db.execute_update(
            query, 
            (assignment_id, question_type, content, answer, score, analysis)
        )
        
        if question_id:
            logger.info(f"Question added: {question_id} to assignment {assignment_id}")
            return question_id
        raise ValidationError("添加题目失败")

    def get_questions_by_assignment(self, assignment_id):
        """获取作业的所有题目"""
        query = "SELECT * FROM question WHERE assignment_id = ? ORDER BY id"
        rows = self.db.execute_query(query, (assignment_id,))
        return [Question.from_row(row) for row in rows]

    def update_question(self, question_id, content, answer, score, analysis):
        """更新题目"""
        query = """
            UPDATE question 
            SET content = ?, answer = ?, score = ?, analysis = ?
            WHERE id = ?
        """
        result = self.db.execute_update(query, (content, answer, score, analysis, question_id))
        return result is not None

    def delete_question(self, question_id):
        """删除题目"""
        query = "DELETE FROM question WHERE id = ?"
        result = self.db.execute_update(query, (question_id,))
        return result is not None
