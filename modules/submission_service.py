"""
提交服务层 - 处理作业提交和评分逻辑
"""
import logging
from datetime import datetime
from modules.ai_grader import AIGrader
from modules.validators import Validator
from modules.exceptions import ValidationError, ResourceNotFoundError

logger = logging.getLogger(__name__)

class SubmissionService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.ai_grader = AIGrader()

    def submit_assignment(self, student_id, assignment_id, answers):
        """
        提交作业并自动评分
        answers: {question_id: student_answer}
        返回: submission_id
        """
        # 获取所有题目
        questions = self._get_questions(assignment_id)
        if not questions:
            raise ResourceNotFoundError("该作业没有题目")
        
        # 创建提交记录
        submission_id = self._create_submission(student_id, assignment_id)
        
        # 逐题评分
        total_score = 0
        details = []
        
        for question in questions:
            student_answer = answers.get(question.id, "")
            score, is_correct, feedback = self._grade_question(
                question, student_answer
            )
            total_score += score
            
            details.append({
                'submission_id': submission_id,
                'question_id': question.id,
                'student_answer': student_answer,
                'is_correct': is_correct,
                'score': score,
                'ai_feedback': feedback
            })
        
        # 批量插入提交详情
        self._save_submission_details(details)
        
        # 更新总分
        self._update_total_score(submission_id, total_score)
        
        logger.info(f"Submission completed: {submission_id}, score: {total_score}")
        return submission_id, total_score

    def _get_questions(self, assignment_id):
        """获取作业题目"""
        query = "SELECT * FROM question WHERE assignment_id = ? ORDER BY id"
        rows = self.db.execute_query(query, (assignment_id,))
        
        from modules.models import Question
        return [Question.from_row(row) for row in rows]

    def _create_submission(self, student_id, assignment_id):
        """创建提交记录"""
        query = """
            INSERT INTO submission (student_id, assignment_id, total_score, feedback)
            VALUES (?, ?, 0, '')
        """
        submission_id = self.db.execute_update(query, (student_id, assignment_id))
        if not submission_id:
            raise ValidationError("创建提交记录失败")
        return submission_id

    def _grade_question(self, question, student_answer):
        """评分单个题目"""
        if question.type in ['single_choice', 'multi_choice', 'boolean', 'fill_in']:
            # 客观题
            is_correct = self.ai_grader.grade_objective(student_answer, question.answer)
            score = question.score if is_correct else 0
            feedback = "正确" if is_correct else "错误"
            return score, is_correct, feedback
        
        elif question.type == 'subjective':
            # 主观题
            score, feedback = self.ai_grader.grade_subjective(
                student_answer, question.answer, question.score
            )
            is_correct = None  # 主观题不判断对错
            return score, is_correct, feedback
        
        return 0, False, "未知题型"

    def _save_submission_details(self, details):
        """批量保存提交详情"""
        query = """
            INSERT INTO submission_detail 
            (submission_id, question_id, student_answer, is_correct, score, ai_feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params_list = [
            (d['submission_id'], d['question_id'], d['student_answer'],
             d['is_correct'], d['score'], d['ai_feedback'])
            for d in details
        ]
        self.db.execute_many(query, params_list)

    def _update_total_score(self, submission_id, total_score):
        """更新总分"""
        query = "UPDATE submission SET total_score = ? WHERE id = ?"
        self.db.execute_update(query, (total_score, submission_id))

    def get_student_submissions(self, student_id):
        """获取学生的所有提交记录"""
        query = """
            SELECT s.*, a.title as assignment_title
            FROM submission s
            JOIN assignment a ON s.assignment_id = a.id
            WHERE s.student_id = ?
            ORDER BY s.submit_time DESC
        """
        return self.db.execute_query(query, (student_id,))

    def get_submission_detail(self, submission_id):
        """获取提交详情"""
        query = """
            SELECT sd.*, q.content, q.answer as standard_answer, q.type, q.score as max_score
            FROM submission_detail sd
            JOIN question q ON sd.question_id = q.id
            WHERE sd.submission_id = ?
            ORDER BY sd.question_id
        """
        return self.db.execute_query(query, (submission_id,))

    def get_assignment_submissions(self, assignment_id):
        """获取作业的所有提交（教师查看）"""
        query = """
            SELECT s.*, u.nickname as student_name
            FROM submission s
            JOIN user u ON s.student_id = u.id
            WHERE s.assignment_id = ?
            ORDER BY s.submit_time DESC
        """
        return self.db.execute_query(query, (assignment_id,))

    def manual_grade(self, submission_detail_id, score, feedback):
        """教师手动评分（主观题）"""
        query = """
            UPDATE submission_detail 
            SET score = ?, ai_feedback = ?
            WHERE id = ?
        """
        result = self.db.execute_update(query, (score, feedback, submission_detail_id))
        
        if result is not None:
            # 重新计算总分
            self._recalculate_total_score(submission_detail_id)
            return True
        return False

    def _recalculate_total_score(self, submission_detail_id):
        """重新计算提交的总分"""
        # 获取submission_id
        query = "SELECT submission_id FROM submission_detail WHERE id = ?"
        rows = self.db.execute_query(query, (submission_detail_id,))
        if not rows:
            return
        
        submission_id = rows[0]['submission_id']
        
        # 计算总分
        query = """
            SELECT SUM(score) as total
            FROM submission_detail
            WHERE submission_id = ?
        """
        rows = self.db.execute_query(query, (submission_id,))
        total_score = rows[0]['total'] if rows and rows[0]['total'] else 0
        
        # 更新
        self._update_total_score(submission_id, total_score)
