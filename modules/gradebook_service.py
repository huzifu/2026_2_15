"""
成绩管理服务
"""
import logging
import json
from typing import List, Dict, Any, Optional
from modules.models import User, Assignment
from modules.exceptions import ValidationError, ResourceNotFoundError
from config import GRADE_SCALE

logger = logging.getLogger(__name__)

class GradebookService:
    def __init__(self, db_manager):
        self.db = db_manager

    def calculate_grade(self, score: float, total_score: float = 100) -> str:
        """根据分数计算等级"""
        if score is None:
            return None
        
        percentage = (score / total_score) * 100 if total_score > 0 else 0
        
        for grade, (min_score, max_score) in GRADE_SCALE.items():
            if min_score <= percentage <= max_score:
                return grade
        
        return 'F'

    def update_gradebook(self, student_id: int, course_id: int, 
                        assignment_id: int = None, score: float = None,
                        weight: float = 1.0, comment: str = None) -> bool:
        """更新成绩簿"""
        if score is not None and (score < 0 or score > 1000):
            raise ValidationError("分数必须在0-1000之间")
        
        if weight <= 0 or weight > 10:
            raise ValidationError("权重必须在0-10之间")
        
        # 检查是否已存在记录
        check_query = """
            SELECT id FROM gradebook 
            WHERE student_id = ? AND course_id = ? AND assignment_id = ?
        """
        params = [student_id, course_id]
        if assignment_id:
            params.append(assignment_id)
            check_query += " AND assignment_id = ?"
        else:
            check_query += " AND assignment_id IS NULL"
        
        existing = self.db.execute_query(check_query, tuple(params))
        
        if existing:
            # 更新现有记录
            updates = []
            update_params = []
            
            if score is not None:
                updates.append("score = ?")
                update_params.append(score)
                
                # 计算等级
                grade = self.calculate_grade(score)
                updates.append("grade = ?")
                update_params.append(grade)
            
            if weight is not None:
                updates.append("weight = ?")
                update_params.append(weight)
            
            if comment is not None:
                updates.append("comment = ?")
                update_params.append(comment)
            
            if not updates:
                return True
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE gradebook SET {', '.join(updates)} WHERE id = ?"
            update_params.append(existing[0]['id'])
            
            result = self.db.execute_update(query, tuple(update_params))
        else:
            # 创建新记录
            grade = self.calculate_grade(score) if score is not None else None
            
            query = """
                INSERT INTO gradebook 
                (student_id, course_id, assignment_id, score, grade, weight, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            result = self.db.execute_update(
                query, (student_id, course_id, assignment_id, score, grade, weight, comment)
            )
        
        if result is not None:
            logger.info(f"Gradebook updated for student {student_id}, course {course_id}")
            return True
        return False

    def get_student_grades(self, student_id: int, course_id: int = None) -> List[Dict[str, Any]]:
        """获取学生成绩"""
        conditions = ["g.student_id = ?"]
        params = [student_id]
        
        if course_id:
            conditions.append("g.course_id = ?")
            params.append(course_id)
        
        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT g.*, 
                   a.title as assignment_title, a.total_score as assignment_total,
                   c.title as course_title,
                   u.nickname as student_name
            FROM gradebook g
            LEFT JOIN assignment a ON g.assignment_id = a.id
            LEFT JOIN course c ON g.course_id = c.id
            LEFT JOIN user u ON g.student_id = u.id
            WHERE {where_clause}
            ORDER BY g.updated_at DESC
        """
        
        rows = self.db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def get_course_grades(self, course_id: int) -> Dict[str, Any]:
        """获取课程所有学生成绩"""
        # 获取学生列表
        students_query = """
            SELECT DISTINCT g.student_id, u.nickname, u.username
            FROM gradebook g
            JOIN user u ON g.student_id = u.id
            WHERE g.course_id = ?
            ORDER BY u.nickname
        """
        students = self.db.execute_query(students_query, (course_id,))
        
        # 获取作业列表
        assignments_query = """
            SELECT a.id, a.title, a.total_score, a.type
            FROM assignment a
            WHERE a.course_id = ? AND a.status = 'graded'
            ORDER BY a.created_at
        """
        assignments = self.db.execute_query(assignments_query, (course_id,))
        
        # 获取成绩数据
        grades_query = """
            SELECT g.student_id, g.assignment_id, g.score, g.grade, g.comment
            FROM gradebook g
            WHERE g.course_id = ?
        """
        grades = self.db.execute_query(grades_query, (course_id,))
        
        # 构建成绩矩阵
        grade_matrix = {}
        for grade in grades:
            student_id = grade['student_id']
            assignment_id = grade['assignment_id']
            if student_id not in grade_matrix:
                grade_matrix[student_id] = {}
            grade_matrix[student_id][assignment_id] = {
                'score': grade['score'],
                'grade': grade['grade'],
                'comment': grade['comment']
            }
        
        # 计算每个学生的总分和平均分
        student_stats = {}
        for student in students:
            student_id = student['student_id']
            student_grades = grade_matrix.get(student_id, {})
            
            total_score = 0
            total_weight = 0
            grade_count = 0
            
            for assignment in assignments:
                assignment_id = assignment['id']
                if assignment_id in student_grades:
                    grade_data = student_grades[assignment_id]
                    if grade_data['score'] is not None:
                        total_score += grade_data['score']
                        total_weight += 1
                        grade_count += 1
            
            average_score = total_score / total_weight if total_weight > 0 else None
            average_grade = self.calculate_grade(average_score) if average_score is not None else None
            
            student_stats[student_id] = {
                'total_score': total_score,
                'average_score': average_score,
                'average_grade': average_grade,
                'grade_count': grade_count
            }
        
        return {
            'students': [dict(s) for s in students],
            'assignments': [dict(a) for a in assignments],
            'grade_matrix': grade_matrix,
            'student_stats': student_stats
        }

    def get_assignment_grades(self, assignment_id: int) -> List[Dict[str, Any]]:
        """获取作业成绩"""
        query = """
            SELECT g.*, 
                   u.nickname as student_name, u.username,
                   s.submit_time, s.late_submission
            FROM gradebook g
            JOIN user u ON g.student_id = u.id
            LEFT JOIN submission s ON g.assignment_id = s.assignment_id AND g.student_id = s.student_id
            WHERE g.assignment_id = ?
            ORDER BY u.nickname
        """
        rows = self.db.execute_query(query, (assignment_id,))
        return [dict(row) for row in rows]

    def import_grades_from_submissions(self, assignment_id: int) -> int:
        """从提交记录导入成绩"""
        # 获取作业信息
        assignment_query = "SELECT id, total_score FROM assignment WHERE id = ?"
        assignment_rows = self.db.execute_query(assignment_query, (assignment_id,))
        if not assignment_rows:
            raise ResourceNotFoundError("作业不存在")
        
        assignment_info = assignment_rows[0]
        total_score = assignment_info['total_score']
        
        # 获取所有提交记录
        submissions_query = """
            SELECT s.student_id, s.total_score, s.grading_status
            FROM submission s
            WHERE s.assignment_id = ? AND s.grading_status = 'graded'
        """
        submissions = self.db.execute_query(submissions_query, (assignment_id,))
        
        imported_count = 0
        for submission in submissions:
            student_id = submission['student_id']
            score = submission['total_score']
            
            # 更新成绩簿
            success = self.update_gradebook(
                student_id=student_id,
                course_id=None,  # 需要通过作业获取课程ID
                assignment_id=assignment_id,
                score=score,
                weight=1.0,
                comment="从提交记录导入"
            )
            
            if success:
                imported_count += 1
        
        logger.info(f"Grades imported from submissions: {imported_count} records")
        return imported_count

    def calculate_final_grade(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """计算最终成绩"""
        # 获取所有作业成绩
        grades_query = """
            SELECT g.score, g.weight, a.title, a.type
            FROM gradebook g
            JOIN assignment a ON g.assignment_id = a.id
            WHERE g.student_id = ? AND g.course_id = ? AND g.score IS NOT NULL
        """
        grades = self.db.execute_query(grades_query, (student_id, course_id))
        
        if not grades:
            return {
                'final_score': None,
                'final_grade': None,
                'grade_breakdown': []
            }
        
        # 计算加权平均分
        total_weighted_score = 0
        total_weight = 0
        grade_breakdown = []
        
        for grade in grades:
            score = grade['score']
            weight = grade['weight']
            
            total_weighted_score += score * weight
            total_weight += weight
            
            grade_breakdown.append({
                'assignment': grade['title'],
                'type': grade['type'],
                'score': score,
                'weight': weight,
                'weighted_score': score * weight
            })
        
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0
        final_grade = self.calculate_grade(final_score)
        
        return {
            'final_score': round(final_score, 2),
            'final_grade': final_grade,
            'total_weight': total_weight,
            'grade_breakdown': grade_breakdown
        }

    def get_grade_statistics(self, course_id: int) -> Dict[str, Any]:
        """获取成绩统计信息"""
        # 总体统计
        overall_query = """
            SELECT 
                COUNT(DISTINCT g.student_id) as total_students,
                AVG(g.score) as average_score,
                MIN(g.score) as min_score,
                MAX(g.score) as max_score,
                COUNT(CASE WHEN g.grade = 'A' THEN 1 END) as grade_a,
                COUNT(CASE WHEN g.grade = 'B' THEN 1 END) as grade_b,
                COUNT(CASE WHEN g.grade = 'C' THEN 1 END) as grade_c,
                COUNT(CASE WHEN g.grade = 'D' THEN 1 END) as grade_d,
                COUNT(CASE WHEN g.grade = 'F' THEN 1 END) as grade_f
            FROM gradebook g
            WHERE g.course_id = ? AND g.score IS NOT NULL
        """
        overall_stats = self.db.execute_query(overall_query, (course_id,))
        
        # 作业统计
        assignment_query = """
            SELECT 
                a.id, a.title, a.type,
                AVG(g.score) as average_score,
                MIN(g.score) as min_score,
                MAX(g.score) as max_score,
                COUNT(g.score) as submission_count
            FROM assignment a
            LEFT JOIN gradebook g ON a.id = g.assignment_id
            WHERE a.course_id = ?
            GROUP BY a.id, a.title, a.type
            ORDER BY a.created_at
        """
        assignment_stats = self.db.execute_query(assignment_query, (course_id,))
        
        # 学生排名
        ranking_query = """
            SELECT 
                g.student_id, u.nickname, u.username,
                AVG(g.score) as average_score,
                COUNT(g.score) as assignment_count
            FROM gradebook g
            JOIN user u ON g.student_id = u.id
            WHERE g.course_id = ? AND g.score IS NOT NULL
            GROUP BY g.student_id, u.nickname, u.username
            ORDER BY average_score DESC
        """
        ranking_stats = self.db.execute_query(ranking_query, (course_id,))
        
        # 成绩分布
        distribution_query = """
            SELECT 
                g.grade,
                COUNT(*) as count
            FROM gradebook g
            WHERE g.course_id = ? AND g.grade IS NOT NULL
            GROUP BY g.grade
            ORDER BY g.grade
        """
        distribution_stats = self.db.execute_query(distribution_query, (course_id,))
        
        return {
            'overall': dict(overall_stats[0]) if overall_stats else {},
            'assignments': [dict(a) for a in assignment_stats],
            'ranking': [dict(r) for r in ranking_stats],
            'distribution': [dict(d) for d in distribution_stats]
        }

    def export_grades(self, course_id: int, format: str = 'excel') -> Dict[str, Any]:
        """导出成绩"""
        # 获取课程信息
        course_query = "SELECT title FROM course WHERE id = ?"
        course_rows = self.db.execute_query(course_query, (course_id,))
        if not course_rows:
            raise ResourceNotFoundError("课程不存在")
        
        course_title = course_rows[0]['title']
        
        # 获取成绩数据
        grades_data = self.get_course_grades(course_id)
        
        # 构建导出数据
        export_data = {
            'course_title': course_title,
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'students': [],
            'assignments': grades_data['assignments'],
            'grades': []
        }
        
        for student in grades_data['students']:
            student_id = student['student_id']
            student_grades = []
            
            for assignment in grades_data['assignments']:
                assignment_id = assignment['id']
                grade_info = grades_data['grade_matrix'].get(student_id, {}).get(assignment_id, {})
                student_grades.append({
                    'assignment_id': assignment_id,
                    'score': grade_info.get('score'),
                    'grade': grade_info.get('grade'),
                    'comment': grade_info.get('comment')
                })
            
            student_stats = grades_data['student_stats'].get(student_id, {})
            
            export_data['students'].append({
                'student_id': student_id,
                'name': student['nickname'],
                'username': student['username'],
                'grades': student_grades,
                'total_score': student_stats.get('total_score'),
                'average_score': student_stats.get('average_score'),
                'average_grade': student_stats.get('average_grade')
            })
        
        return export_data

    def generate_report_card(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """生成成绩报告单"""
        # 获取学生信息
        student_query = "SELECT nickname, username FROM user WHERE id = ?"
        student_rows = self.db.execute_query(student_query, (student_id,))
        if not student_rows:
            raise ResourceNotFoundError("学生不存在")
        
        student_info = student_rows[0]
        
        # 获取课程信息
        course_query = "SELECT title, description FROM course WHERE id = ?"
        course_rows = self.db.execute_query(course_query, (course_id,))
        if not course_rows:
            raise ResourceNotFoundError("课程不存在")
        
        course_info = course_rows[0]
        
        # 计算最终成绩
        final_grade = self.calculate_final_grade(student_id, course_id)
        
        # 获取详细成绩
        detailed_grades = self.get_student_grades(student_id, course_id)
        
        # 获取学习进度
        progress_query = """
            SELECT 
                AVG(progress) as overall_progress,
                SUM(time_spent) as total_time_spent
            FROM learning_progress
            WHERE student_id = ? AND course_id = ?
        """
        progress_rows = self.db.execute_query(progress_query, (student_id, course_id))
        progress_info = progress_rows[0] if progress_rows else {}
        
        # 获取教师评语
        comment_query = """
            SELECT comment FROM gradebook 
            WHERE student_id = ? AND course_id = ? AND assignment_id IS NULL
            ORDER BY updated_at DESC
            LIMIT 1
        """
        comment_rows = self.db.execute_query(comment_query, (student_id, course_id))
        teacher_comment = comment_rows[0]['comment'] if comment_rows else None
        
        return {
            'student': {
                'name': student_info['nickname'],
                'username': student_info['username']
            },
            'course': {
                'title': course_info['title'],
                'description': course_info['description']
            },
            'final_grade': final_grade,
            'detailed_grades': detailed_grades,
            'learning_progress': {
                'overall_progress': progress_info.get('overall_progress', 0),
                'total_time_spent': progress_info.get('total_time_spent', 0)
            },
            'teacher_comment': teacher_comment,
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def bulk_update_grades(self, assignment_id: int, grade_data: List[Dict[str, Any]]) -> int:
        """批量更新成绩"""
        updated_count = 0
        
        for data in grade_data:
            student_id = data.get('student_id')
            score = data.get('score')
            comment = data.get('comment')
            
            if not student_id or score is None:
                continue
            
            # 获取课程ID
            course_query = "SELECT course_id FROM assignment WHERE id = ?"
            course_rows = self.db.execute_query(course_query, (assignment_id,))
            if not course_rows:
                continue
            
            course_id = course_rows[0]['course_id']
            
            # 更新成绩
            success = self.update_gradebook(
                student_id=student_id,
                course_id=course_id,
                assignment_id=assignment_id,
                score=score,
                comment=comment
            )
            
            if success:
                updated_count += 1
        
        logger.info(f"Bulk grades updated: {updated_count} records")
        return updated_count