"""
课程管理服务
"""
import logging
import json
from typing import List, Dict, Any, Optional
from modules.models import Course, Chapter, Resource, LearningProgress
from modules.exceptions import ValidationError, ResourceNotFoundError

logger = logging.getLogger(__name__)

class CourseService:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_course(self, title: str, description: str, teacher_id: int, 
                     class_id: int = None, cover_image: str = None) -> int:
        """创建课程"""
        if not title or len(title.strip()) < 2:
            raise ValidationError("课程标题至少需要2个字符")
        
        if class_id:
            # 验证班级是否存在且教师有权限
            check_query = "SELECT id FROM class WHERE id = ? AND teacher_id = ?"
            if not self.db.execute_query(check_query, (class_id, teacher_id)):
                raise ValidationError("班级不存在或您没有权限")
        
        query = """
            INSERT INTO course (title, description, teacher_id, class_id, cover_image)
            VALUES (?, ?, ?, ?, ?)
        """
        course_id = self.db.execute_update(
            query, (title.strip(), description.strip(), teacher_id, class_id, cover_image)
        )
        
        if course_id:
            logger.info(f"Course created: {course_id} by teacher {teacher_id}")
            return course_id
        raise ValidationError("创建课程失败")

    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """根据ID获取课程"""
        query = """
            SELECT c.*, u.nickname as teacher_name,
                   cl.name as class_name
            FROM course c
            LEFT JOIN user u ON c.teacher_id = u.id
            LEFT JOIN class cl ON c.class_id = cl.id
            WHERE c.id = ?
        """
        rows = self.db.execute_query(query, (course_id,))
        if rows:
            return Course.from_row(rows[0])
        return None

    def get_courses_by_teacher(self, teacher_id: int, status: str = None) -> List[Course]:
        """获取教师的所有课程"""
        conditions = ["c.teacher_id = ?"]
        params = [teacher_id]
        
        if status:
            conditions.append("c.status = ?")
            params.append(status)
        
        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM chapter WHERE course_id = c.id) as chapter_count
            FROM course c
            WHERE {where_clause}
            ORDER BY c.created_at DESC
        """
        rows = self.db.execute_query(query, tuple(params))
        return [Course.from_row(row) for row in rows]

    def get_available_courses(self, student_id: int) -> List[Dict[str, Any]]:
        """获取学生可访问的课程"""
        query = """
            SELECT c.*, u.nickname as teacher_name,
                   (SELECT COUNT(*) FROM chapter WHERE course_id = c.id) as chapter_count,
                   lp.progress as student_progress,
                   lp.status as learning_status
            FROM course c
            JOIN user u ON c.teacher_id = u.id
            LEFT JOIN learning_progress lp ON c.id = lp.course_id AND lp.student_id = ?
            WHERE c.status = 'published'
            ORDER BY c.created_at DESC
        """
        rows = self.db.execute_query(query, (student_id,))
        return [dict(row) for row in rows]

    def update_course(self, course_id: int, title: str = None, description: str = None,
                     cover_image: str = None, status: str = None) -> bool:
        """更新课程信息"""
        updates = []
        params = []
        
        if title:
            if len(title.strip()) < 2:
                raise ValidationError("课程标题至少需要2个字符")
            updates.append("title = ?")
            params.append(title.strip())
        
        if description is not None:
            updates.append("description = ?")
            params.append(description.strip())
        
        if cover_image is not None:
            updates.append("cover_image = ?")
            params.append(cover_image)
        
        if status:
            if status not in ['draft', 'published', 'archived']:
                raise ValidationError("无效的课程状态")
            updates.append("status = ?")
            params.append(status)
        
        if not updates:
            return True
        
        query = f"UPDATE course SET {', '.join(updates)} WHERE id = ?"
        params.append(course_id)
        
        result = self.db.execute_update(query, tuple(params))
        if result is not None:
            logger.info(f"Course updated: {course_id}")
            return True
        return False

    def publish_course(self, course_id: int) -> bool:
        """发布课程"""
        query = "UPDATE course SET status = 'published' WHERE id = ?"
        result = self.db.execute_update(query, (course_id,))
        if result is not None:
            logger.info(f"Course published: {course_id}")
            return True
        return False

    def archive_course(self, course_id: int) -> bool:
        """归档课程"""
        query = "UPDATE course SET status = 'archived' WHERE id = ?"
        result = self.db.execute_update(query, (course_id,))
        if result is not None:
            logger.info(f"Course archived: {course_id}")
            return True
        return False

    def add_chapter(self, course_id: int, title: str, description: str = None, 
                   order_index: int = None) -> int:
        """添加章节"""
        if not title or len(title.strip()) < 1:
            raise ValidationError("章节标题不能为空")
        
        # 获取最大order_index
        if order_index is None:
            max_order_query = "SELECT MAX(order_index) as max_order FROM chapter WHERE course_id = ?"
            max_order_rows = self.db.execute_query(max_order_query, (course_id,))
            order_index = (max_order_rows[0]['max_order'] or 0) + 1
        
        query = """
            INSERT INTO chapter (course_id, title, description, order_index)
            VALUES (?, ?, ?, ?)
        """
        chapter_id = self.db.execute_update(
            query, (course_id, title.strip(), description.strip(), order_index)
        )
        
        if chapter_id:
            logger.info(f"Chapter added: {chapter_id} to course {course_id}")
            return chapter_id
        raise ValidationError("添加章节失败")

    def get_chapters(self, course_id: int) -> List[Chapter]:
        """获取课程的所有章节"""
        query = """
            SELECT c.*,
                   (SELECT COUNT(*) FROM course_content WHERE chapter_id = c.id) as content_count
            FROM chapter c
            WHERE c.course_id = ?
            ORDER BY c.order_index
        """
        rows = self.db.execute_query(query, (course_id,))
        return [Chapter.from_row(row) for row in rows]

    def update_chapter(self, chapter_id: int, title: str = None, description: str = None,
                      order_index: int = None) -> bool:
        """更新章节信息"""
        updates = []
        params = []
        
        if title:
            if len(title.strip()) < 1:
                raise ValidationError("章节标题不能为空")
            updates.append("title = ?")
            params.append(title.strip())
        
        if description is not None:
            updates.append("description = ?")
            params.append(description.strip())
        
        if order_index is not None:
            updates.append("order_index = ?")
            params.append(order_index)
        
        if not updates:
            return True
        
        query = f"UPDATE chapter SET {', '.join(updates)} WHERE id = ?"
        params.append(chapter_id)
        
        result = self.db.execute_update(query, tuple(params))
        if result is not None:
            logger.info(f"Chapter updated: {chapter_id}")
            return True
        return False

    def delete_chapter(self, chapter_id: int) -> bool:
        """删除章节"""
        query = "DELETE FROM chapter WHERE id = ?"
        result = self.db.execute_update(query, (chapter_id,))
        if result is not None:
            logger.info(f"Chapter deleted: {chapter_id}")
            return True
        return False

    def add_course_content(self, chapter_id: int, title: str, content_type: str,
                          content: str = None, file_path: str = None, 
                          duration: int = None, order_index: int = None) -> int:
        """添加课程内容"""
        if not title or len(title.strip()) < 1:
            raise ValidationError("内容标题不能为空")
        
        if content_type not in ['text', 'video', 'audio', 'document', 'quiz', 'assignment']:
            raise ValidationError("无效的内容类型")
        
        # 获取最大order_index
        if order_index is None:
            max_order_query = "SELECT MAX(order_index) as max_order FROM course_content WHERE chapter_id = ?"
            max_order_rows = self.db.execute_query(max_order_query, (chapter_id,))
            order_index = (max_order_rows[0]['max_order'] or 0) + 1
        
        query = """
            INSERT INTO course_content (chapter_id, title, content_type, content, file_path, duration, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        content_id = self.db.execute_update(
            query, (chapter_id, title.strip(), content_type, content, file_path, duration, order_index)
        )
        
        if content_id:
            logger.info(f"Course content added: {content_id} to chapter {chapter_id}")
            return content_id
        raise ValidationError("添加课程内容失败")

    def get_course_contents(self, chapter_id: int) -> List[Dict[str, Any]]:
        """获取章节的所有内容"""
        query = """
            SELECT cc.*
            FROM course_content cc
            WHERE cc.chapter_id = ?
            ORDER BY cc.order_index
        """
        rows = self.db.execute_query(query, (chapter_id,))
        return [dict(row) for row in rows]

    def update_learning_progress(self, student_id: int, course_id: int, 
                                chapter_id: int = None, content_id: int = None,
                                progress: float = None, time_spent: int = 0) -> bool:
        """更新学习进度"""
        # 检查是否已存在记录
        check_query = """
            SELECT id FROM learning_progress 
            WHERE student_id = ? AND course_id = ? AND content_id = ?
        """
        existing = self.db.execute_query(check_query, (student_id, course_id, content_id))
        
        if existing:
            # 更新现有记录
            query = """
                UPDATE learning_progress 
                SET progress = ?, time_spent = time_spent + ?, last_accessed = CURRENT_TIMESTAMP,
                    status = CASE WHEN ? >= 100 THEN 'completed' ELSE 'in_progress' END
                WHERE id = ?
            """
            result = self.db.execute_update(
                query, (progress, time_spent, progress, existing[0]['id'])
            )
        else:
            # 创建新记录
            query = """
                INSERT INTO learning_progress 
                (student_id, course_id, chapter_id, content_id, progress, time_spent, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            status = 'completed' if progress and progress >= 100 else 'in_progress'
            result = self.db.execute_update(
                query, (student_id, course_id, chapter_id, content_id, progress, time_spent, status)
            )
        
        if result is not None:
            logger.info(f"Learning progress updated for student {student_id}, course {course_id}")
            return True
        return False

    def get_student_progress(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """获取学生的学习进度"""
        # 总体进度
        overall_query = """
            SELECT 
                AVG(progress) as overall_progress,
                SUM(time_spent) as total_time_spent,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                COUNT(*) as total_count
            FROM learning_progress
            WHERE student_id = ? AND course_id = ?
        """
        overall_stats = self.db.execute_query(overall_query, (student_id, course_id))
        
        # 章节进度
        chapter_query = """
            SELECT 
                ch.id, ch.title, ch.order_index,
                lp.progress, lp.status, lp.last_accessed, lp.time_spent
            FROM chapter ch
            LEFT JOIN learning_progress lp ON ch.id = lp.chapter_id AND lp.student_id = ?
            WHERE ch.course_id = ?
            ORDER BY ch.order_index
        """
        chapter_progress = self.db.execute_query(chapter_query, (student_id, course_id))
        
        # 最近学习的内容
        recent_query = """
            SELECT cc.title, cc.content_type, lp.last_accessed
            FROM learning_progress lp
            JOIN course_content cc ON lp.content_id = cc.id
            WHERE lp.student_id = ? AND lp.course_id = ?
            ORDER BY lp.last_accessed DESC
            LIMIT 5
        """
        recent_activities = self.db.execute_query(recent_query, (student_id, course_id))
        
        return {
            'overall': dict(overall_stats[0]) if overall_stats else {},
            'chapters': [dict(row) for row in chapter_progress],
            'recent_activities': [dict(row) for row in recent_activities]
        }

    def add_resource(self, title: str, file_path: str, uploader_id: int,
                    course_id: int = None, assignment_id: int = None,
                    description: str = None, tags: str = None) -> int:
        """添加资源"""
        if not title or not file_path:
            raise ValidationError("标题和文件路径不能为空")
        
        import os
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        file_type = os.path.splitext(file_path)[1].lower() if file_path else None
        
        query = """
            INSERT INTO resource 
            (title, description, file_path, file_type, file_size, uploader_id, course_id, assignment_id, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        resource_id = self.db.execute_update(
            query, (title.strip(), description, file_path, file_type, file_size, 
                   uploader_id, course_id, assignment_id, tags)
        )
        
        if resource_id:
            logger.info(f"Resource added: {resource_id} by user {uploader_id}")
            return resource_id
        raise ValidationError("添加资源失败")

    def get_course_resources(self, course_id: int) -> List[Resource]:
        """获取课程资源"""
        query = """
            SELECT r.*, u.nickname as uploader_name
            FROM resource r
            LEFT JOIN user u ON r.uploader_id = u.id
            WHERE r.course_id = ?
            ORDER BY r.created_at DESC
        """
        rows = self.db.execute_query(query, (course_id,))
        return [Resource.from_row(row) for row in rows]

    def search_courses(self, keyword: str = None, teacher_id: int = None,
                      status: str = 'published') -> List[Dict[str, Any]]:
        """搜索课程"""
        conditions = ["c.status = ?"]
        params = [status]
        
        if keyword:
            conditions.append("(c.title LIKE ? OR c.description LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if teacher_id:
            conditions.append("c.teacher_id = ?")
            params.append(teacher_id)
        
        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT c.*, u.nickname as teacher_name,
                   (SELECT COUNT(*) FROM chapter WHERE course_id = c.id) as chapter_count,
                   (SELECT COUNT(*) FROM learning_progress WHERE course_id = c.id) as enrolled_count
            FROM course c
            LEFT JOIN user u ON c.teacher_id = u.id
            WHERE {where_clause}
            ORDER BY c.created_at DESC
        """
        
        rows = self.db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def get_course_statistics(self, course_id: int) -> Dict[str, Any]:
        """获取课程统计信息"""
        # 学生统计
        student_query = """
            SELECT 
                COUNT(DISTINCT student_id) as enrolled_students,
                AVG(progress) as average_progress,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_students
            FROM learning_progress
            WHERE course_id = ?
        """
        student_stats = self.db.execute_query(student_query, (course_id,))
        
        # 内容统计
        content_query = """
            SELECT 
                COUNT(*) as total_content,
                COUNT(CASE WHEN content_type = 'video' THEN 1 END) as video_count,
                COUNT(CASE WHEN content_type = 'quiz' THEN 1 END) as quiz_count,
                COUNT(CASE WHEN content_type = 'assignment' THEN 1 END) as assignment_count
            FROM course_content cc
            JOIN chapter ch ON cc.chapter_id = ch.id
            WHERE ch.course_id = ?
        """
        content_stats = self.db.execute_query(content_query, (course_id,))
        
        # 作业统计
        assignment_query = """
            SELECT 
                COUNT(*) as total_assignments,
                AVG(total_score) as average_score,
                COUNT(CASE WHEN grading_status = 'graded' THEN 1 END) as graded_assignments
            FROM submission s
            JOIN assignment a ON s.assignment_id = a.id
            WHERE a.course_id = ?
        """
        assignment_stats = self.db.execute_query(assignment_query, (course_id,))
        
        return {
            'student_stats': dict(student_stats[0]) if student_stats else {},
            'content_stats': dict(content_stats[0]) if content_stats else {},
            'assignment_stats': dict(assignment_stats[0]) if assignment_stats else {}
        }