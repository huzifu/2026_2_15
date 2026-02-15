"""
通知服务
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from modules.models import Notification, User
from modules.exceptions import ValidationError

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_notification(self, user_id: int, type: str, title: str, 
                           content: str = None, related_id: int = None,
                           related_type: str = None) -> int:
        """创建通知"""
        if not title or len(title.strip()) < 1:
            raise ValidationError("通知标题不能为空")
        
        if type not in ['assignment', 'grade', 'discussion', 'system', 'reminder']:
            raise ValidationError("无效的通知类型")
        
        query = """
            INSERT INTO notification 
            (user_id, type, title, content, related_id, related_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        notification_id = self.db.execute_update(
            query, (user_id, type, title.strip(), content, related_id, related_type)
        )
        
        if notification_id:
            logger.info(f"Notification created: {notification_id} for user {user_id}")
            return notification_id
        raise ValidationError("创建通知失败")

    def create_bulk_notifications(self, user_ids: List[int], type: str, title: str,
                                 content: str = None, related_id: int = None,
                                 related_type: str = None) -> int:
        """批量创建通知"""
        if not user_ids:
            return 0
        
        params = []
        for user_id in user_ids:
            params.append((user_id, type, title, content, related_id, related_type))
        
        query = """
            INSERT INTO notification 
            (user_id, type, title, content, related_id, related_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        result = self.db.execute_many(query, params)
        
        if result:
            logger.info(f"Bulk notifications created: {result} notifications")
            return result
        return 0

    def get_user_notifications(self, user_id: int, unread_only: bool = False,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的通知"""
        conditions = ["user_id = ?"]
        params = [user_id]
        
        if unread_only:
            conditions.append("is_read = FALSE")
        
        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT n.*
            FROM notification n
            WHERE {where_clause}
            ORDER BY n.created_at DESC
            LIMIT ?
        """
        params.append(limit)
        
        rows = self.db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def get_notification_count(self, user_id: int, unread_only: bool = False) -> int:
        """获取用户的通知数量"""
        conditions = ["user_id = ?"]
        params = [user_id]
        
        if unread_only:
            conditions.append("is_read = FALSE")
        
        where_clause = " AND ".join(conditions)
        query = f"SELECT COUNT(*) as count FROM notification WHERE {where_clause}"
        
        rows = self.db.execute_query(query, tuple(params))
        return rows[0]['count'] if rows else 0

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """标记通知为已读"""
        query = """
            UPDATE notification 
            SET is_read = TRUE 
            WHERE id = ? AND user_id = ?
        """
        result = self.db.execute_update(query, (notification_id, user_id))
        if result is not None:
            logger.info(f"Notification marked as read: {notification_id}")
            return True
        return False

    def mark_all_as_read(self, user_id: int) -> bool:
        """标记所有通知为已读"""
        query = "UPDATE notification SET is_read = TRUE WHERE user_id = ?"
        result = self.db.execute_update(query, (user_id,))
        if result is not None:
            logger.info(f"All notifications marked as read for user {user_id}")
            return True
        return False

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """删除通知"""
        query = "DELETE FROM notification WHERE id = ? AND user_id = ?"
        result = self.db.execute_update(query, (notification_id, user_id))
        if result is not None:
            logger.info(f"Notification deleted: {notification_id}")
            return True
        return False

    def delete_old_notifications(self, days: int = 30) -> int:
        """删除旧通知"""
        query = """
            DELETE FROM notification 
            WHERE created_at < datetime('now', ?) AND is_read = TRUE
        """
        result = self.db.execute_update(query, (f'-{days} days',))
        if result is not None:
            logger.info(f"Old notifications deleted: {result} records")
            return result
        return 0

    def create_assignment_notification(self, assignment_id: int, title: str,
                                      content: str = None) -> int:
        """创建作业通知（发送给相关班级的所有学生）"""
        # 获取作业信息
        assignment_query = """
            SELECT a.title as assignment_title, a.deadline, c.id as class_id
            FROM assignment a
            LEFT JOIN class c ON a.class_id = c.id
            WHERE a.id = ?
        """
        assignment_rows = self.db.execute_query(assignment_query, (assignment_id,))
        if not assignment_rows:
            raise ValidationError("作业不存在")
        
        assignment_info = assignment_rows[0]
        class_id = assignment_info['class_id']
        
        if not class_id:
            raise ValidationError("作业没有关联班级")
        
        # 获取班级所有学生
        student_query = """
            SELECT student_id FROM class_member 
            WHERE class_id = ? AND status = 'active'
        """
        student_rows = self.db.execute_query(student_query, (class_id,))
        student_ids = [row['student_id'] for row in student_rows]
        
        if not student_ids:
            return 0
        
        # 创建通知
        notification_title = f"新作业: {assignment_info['assignment_title']}"
        notification_content = content or f"作业截止时间: {assignment_info['deadline']}"
        
        return self.create_bulk_notifications(
            student_ids, 'assignment', notification_title, 
            notification_content, assignment_id, 'assignment'
        )

    def create_grade_notification(self, submission_id: int) -> int:
        """创建成绩通知"""
        # 获取提交信息
        submission_query = """
            SELECT s.student_id, s.total_score, a.title as assignment_title
            FROM submission s
            JOIN assignment a ON s.assignment_id = a.id
            WHERE s.id = ?
        """
        submission_rows = self.db.execute_query(submission_query, (submission_id,))
        if not submission_rows:
            raise ValidationError("提交记录不存在")
        
        submission_info = submission_rows[0]
        student_id = submission_info['student_id']
        
        # 创建通知
        title = f"作业成绩已发布: {submission_info['assignment_title']}"
        content = f"您的得分: {submission_info['total_score']}"
        
        return self.create_notification(
            student_id, 'grade', title, content, submission_id, 'submission'
        )

    def create_discussion_notification(self, post_id: int, reply_user_id: int) -> int:
        """创建讨论回复通知"""
        # 获取帖子信息
        post_query = """
            SELECT d.user_id as author_id, d.title, d.content,
                   u.nickname as reply_user_name
            FROM discussion d
            JOIN user u ON ? = u.id
            WHERE d.id = ?
        """
        post_rows = self.db.execute_query(post_query, (reply_user_id, post_id))
        if not post_rows:
            raise ValidationError("帖子不存在")
        
        post_info = post_rows[0]
        author_id = post_info['author_id']
        
        if author_id == reply_user_id:
            return 0  # 不给自己发通知
        
        # 创建通知
        title = f"您的帖子有新回复"
        content = f"{post_info['reply_user_name']} 回复了您的帖子: {post_info['title']}"
        
        return self.create_notification(
            author_id, 'discussion', title, content, post_id, 'discussion'
        )

    def create_system_announcement(self, title: str, content: str, 
                                  user_ids: List[int] = None) -> int:
        """创建系统公告"""
        if user_ids:
            return self.create_bulk_notifications(
                user_ids, 'system', title, content, None, 'system'
            )
        else:
            # 发送给所有用户
            all_users_query = "SELECT id FROM user WHERE status = 'active'"
            all_users_rows = self.db.execute_query(all_users_query)
            all_user_ids = [row['id'] for row in all_users_rows]
            
            return self.create_bulk_notifications(
                all_user_ids, 'system', title, content, None, 'system'
            )

    def create_reminder_notification(self, assignment_id: int, days_before: int) -> int:
        """创建作业提醒通知"""
        # 获取作业信息
        assignment_query = """
            SELECT a.title, a.deadline, c.id as class_id
            FROM assignment a
            LEFT JOIN class c ON a.class_id = c.id
            WHERE a.id = ?
        """
        assignment_rows = self.db.execute_query(assignment_query, (assignment_id,))
        if not assignment_rows:
            raise ValidationError("作业不存在")
        
        assignment_info = assignment_rows[0]
        class_id = assignment_info['class_id']
        
        if not class_id:
            return 0
        
        # 获取班级所有学生
        student_query = """
            SELECT student_id FROM class_member 
            WHERE class_id = ? AND status = 'active'
        """
        student_rows = self.db.execute_query(student_query, (class_id,))
        student_ids = [row['student_id'] for row in student_rows]
        
        if not student_ids:
            return 0
        
        # 创建提醒通知
        title = f"作业提醒: {assignment_info['title']}"
        content = f"作业还有 {days_before} 天截止，请及时完成"
        
        return self.create_bulk_notifications(
            student_ids, 'reminder', title, content, assignment_id, 'assignment'
        )

    def get_notification_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取通知统计信息"""
        # 按类型统计
        type_query = """
            SELECT 
                type,
                COUNT(*) as total,
                COUNT(CASE WHEN is_read = FALSE THEN 1 END) as unread
            FROM notification
            WHERE user_id = ?
            GROUP BY type
        """
        type_stats = self.db.execute_query(type_query, (user_id,))
        
        # 最近7天统计
        weekly_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM notification
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        weekly_stats = self.db.execute_query(weekly_query, (user_id,))
        
        # 未读通知列表
        unread_query = """
            SELECT id, type, title, created_at
            FROM notification
            WHERE user_id = ? AND is_read = FALSE
            ORDER BY created_at DESC
            LIMIT 10
        """
        unread_list = self.db.execute_query(unread_query, (user_id,))
        
        return {
            'type_stats': [dict(row) for row in type_stats],
            'weekly_stats': [dict(row) for row in weekly_stats],
            'unread_list': [dict(row) for row in unread_list]
        }

    def get_system_notifications(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取系统通知"""
        offset = (page - 1) * page_size
        
        # 获取总数
        count_query = """
            SELECT COUNT(*) as total 
            FROM notification 
            WHERE type = 'system'
        """
        count_rows = self.db.execute_query(count_query)
        total = count_rows[0]['total'] if count_rows else 0
        
        # 获取通知列表
        query = """
            SELECT n.*, u.nickname as sender_name
            FROM notification n
            LEFT JOIN user u ON n.user_id = u.id
            WHERE n.type = 'system'
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = self.db.execute_query(query, (page_size, offset))
        
        return {
            'notifications': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def check_due_assignments(self) -> int:
        """检查即将到期的作业并发送提醒"""
        from datetime import datetime
        
        # 获取即将到期的作业（1天、3天、7天后到期）
        due_query = """
            SELECT a.id, a.title, a.deadline, c.id as class_id,
                   julianday(a.deadline) - julianday('now') as days_left
            FROM assignment a
            LEFT JOIN class c ON a.class_id = c.id
            WHERE a.status = 'published' 
              AND a.deadline IS NOT NULL
              AND julianday(a.deadline) - julianday('now') BETWEEN 0 AND 7
              AND c.id IS NOT NULL
        """
        due_assignments = self.db.execute_query(due_query)
        
        notification_count = 0
        for assignment in due_assignments:
            days_left = int(float(assignment['days_left']))
            
            # 只在特定天数发送提醒
            if days_left in [1, 3, 7]:
                notification_count += self.create_reminder_notification(
                    assignment['id'], days_left
                )
        
        logger.info(f"Due assignment reminders sent: {notification_count} notifications")
        return notification_count

    def send_welcome_notification(self, user_id: int) -> int:
        """发送欢迎通知给新用户"""
        user_query = "SELECT nickname, role FROM user WHERE id = ?"
        user_rows = self.db.execute_query(user_query, (user_id,))
        if not user_rows:
            return 0
        
        user_info = user_rows[0]
        role = user_info['role']
        nickname = user_info['nickname']
        
        if role == 'student':
            title = "欢迎加入智能教学管理系统！"
            content = f"亲爱的{nickname}同学，欢迎使用我们的教学平台。请查看您的课程和作业，开始学习之旅吧！"
        elif role == 'teacher':
            title = "欢迎使用智能教学管理系统！"
            content = f"尊敬的{nickname}老师，欢迎使用我们的教学平台。您可以创建课程、布置作业、管理学生，开始您的教学工作吧！"
        else:
            title = "欢迎使用智能教学管理系统！"
            content = f"尊敬的{nickname}，欢迎使用我们的教学管理平台。"
        
        return self.create_notification(user_id, 'system', title, content)