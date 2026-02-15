"""
讨论区服务
"""
import logging
from typing import List, Dict, Any, Optional
from modules.models import Discussion, User
from modules.exceptions import ValidationError, ResourceNotFoundError

logger = logging.getLogger(__name__)

class DiscussionService:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_post(self, user_id: int, content: str, title: str = None,
                   course_id: int = None, assignment_id: int = None,
                   parent_id: int = None) -> int:
        """创建讨论帖子"""
        if not content or len(content.strip()) < 5:
            raise ValidationError("帖子内容至少需要5个字符")
        
        if parent_id:
            # 验证父帖子是否存在
            check_query = "SELECT id FROM discussion WHERE id = ?"
            if not self.db.execute_query(check_query, (parent_id,)):
                raise ResourceNotFoundError("父帖子不存在")
        
        query = """
            INSERT INTO discussion 
            (course_id, assignment_id, user_id, title, content, parent_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        post_id = self.db.execute_update(
            query, (course_id, assignment_id, user_id, title, content.strip(), parent_id)
        )
        
        if post_id:
            logger.info(f"Discussion post created: {post_id} by user {user_id}")
            return post_id
        raise ValidationError("创建帖子失败")

    def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取帖子详情"""
        query = """
            SELECT d.*, 
                   u.nickname as author_name, u.avatar as author_avatar,
                   (SELECT COUNT(*) FROM discussion WHERE parent_id = d.id) as reply_count
            FROM discussion d
            JOIN user u ON d.user_id = u.id
            WHERE d.id = ?
        """
        rows = self.db.execute_query(query, (post_id,))
        if rows:
            return dict(rows[0])
        return None

    def get_course_discussions(self, course_id: int, page: int = 1, 
                              page_size: int = 20) -> Dict[str, Any]:
        """获取课程讨论区帖子"""
        offset = (page - 1) * page_size
        
        # 获取帖子总数
        count_query = """
            SELECT COUNT(*) as total 
            FROM discussion 
            WHERE course_id = ? AND parent_id IS NULL AND status = 'active'
        """
        count_rows = self.db.execute_query(count_query, (course_id,))
        total = count_rows[0]['total'] if count_rows else 0
        
        # 获取帖子列表
        query = """
            SELECT d.*, 
                   u.nickname as author_name, u.avatar as author_avatar,
                   (SELECT COUNT(*) FROM discussion WHERE parent_id = d.id) as reply_count,
                   (SELECT MAX(created_at) FROM discussion WHERE parent_id = d.id) as last_reply_time
            FROM discussion d
            JOIN user u ON d.user_id = u.id
            WHERE d.course_id = ? AND d.parent_id IS NULL AND d.status = 'active'
            ORDER BY d.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = self.db.execute_query(query, (course_id, page_size, offset))
        
        return {
            'posts': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def get_assignment_discussions(self, assignment_id: int, page: int = 1,
                                  page_size: int = 20) -> Dict[str, Any]:
        """获取作业讨论区帖子"""
        offset = (page - 1) * page_size
        
        # 获取帖子总数
        count_query = """
            SELECT COUNT(*) as total 
            FROM discussion 
            WHERE assignment_id = ? AND parent_id IS NULL AND status = 'active'
        """
        count_rows = self.db.execute_query(count_query, (assignment_id,))
        total = count_rows[0]['total'] if count_rows else 0
        
        # 获取帖子列表
        query = """
            SELECT d.*, 
                   u.nickname as author_name, u.avatar as author_avatar,
                   (SELECT COUNT(*) FROM discussion WHERE parent_id = d.id) as reply_count,
                   (SELECT MAX(created_at) FROM discussion WHERE parent_id = d.id) as last_reply_time
            FROM discussion d
            JOIN user u ON d.user_id = u.id
            WHERE d.assignment_id = ? AND d.parent_id IS NULL AND d.status = 'active'
            ORDER BY d.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = self.db.execute_query(query, (assignment_id, page_size, offset))
        
        return {
            'posts': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def get_post_replies(self, post_id: int) -> List[Dict[str, Any]]:
        """获取帖子的回复"""
        query = """
            SELECT d.*, 
                   u.nickname as author_name, u.avatar as author_avatar
            FROM discussion d
            JOIN user u ON d.user_id = u.id
            WHERE d.parent_id = ? AND d.status = 'active'
            ORDER BY d.created_at ASC
        """
        rows = self.db.execute_query(query, (post_id,))
        return [dict(row) for row in rows]

    def update_post(self, post_id: int, user_id: int, content: str = None,
                   title: str = None, status: str = None) -> bool:
        """更新帖子"""
        # 验证用户权限
        check_query = "SELECT user_id FROM discussion WHERE id = ?"
        rows = self.db.execute_query(check_query, (post_id,))
        if not rows:
            raise ResourceNotFoundError("帖子不存在")
        
        if rows[0]['user_id'] != user_id:
            # 检查是否是教师或管理员
            user_query = "SELECT role FROM user WHERE id = ?"
            user_rows = self.db.execute_query(user_query, (user_id,))
            if not user_rows or user_rows[0]['role'] not in ['teacher', 'admin']:
                raise ValidationError("没有权限修改此帖子")
        
        updates = []
        params = []
        
        if content:
            if len(content.strip()) < 5:
                raise ValidationError("帖子内容至少需要5个字符")
            updates.append("content = ?")
            params.append(content.strip())
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if status:
            if status not in ['active', 'closed', 'archived']:
                raise ValidationError("无效的帖子状态")
            updates.append("status = ?")
            params.append(status)
        
        if not updates:
            return True
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE discussion SET {', '.join(updates)} WHERE id = ?"
        params.append(post_id)
        
        result = self.db.execute_update(query, tuple(params))
        if result is not None:
            logger.info(f"Discussion post updated: {post_id}")
            return True
        return False

    def delete_post(self, post_id: int, user_id: int) -> bool:
        """删除帖子（软删除）"""
        # 验证用户权限
        check_query = "SELECT user_id FROM discussion WHERE id = ?"
        rows = self.db.execute_query(check_query, (post_id,))
        if not rows:
            raise ResourceNotFoundError("帖子不存在")
        
        if rows[0]['user_id'] != user_id:
            # 检查是否是教师或管理员
            user_query = "SELECT role FROM user WHERE id = ?"
            user_rows = self.db.execute_query(user_query, (user_id,))
            if not user_rows or user_rows[0]['role'] not in ['teacher', 'admin']:
                raise ValidationError("没有权限删除此帖子")
        
        query = "UPDATE discussion SET status = 'archived' WHERE id = ?"
        result = self.db.execute_update(query, (post_id,))
        if result is not None:
            logger.info(f"Discussion post archived: {post_id}")
            return True
        return False

    def search_discussions(self, keyword: str, course_id: int = None,
                          assignment_id: int = None, user_id: int = None,
                          page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """搜索讨论帖子"""
        offset = (page - 1) * page_size
        
        conditions = ["d.status = 'active'", "d.parent_id IS NULL"]
        params = []
        
        if keyword:
            conditions.append("(d.title LIKE ? OR d.content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if course_id:
            conditions.append("d.course_id = ?")
            params.append(course_id)
        
        if assignment_id:
            conditions.append("d.assignment_id = ?")
            params.append(assignment_id)
        
        if user_id:
            conditions.append("d.user_id = ?")
            params.append(user_id)
        
        where_clause = " AND ".join(conditions)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM discussion d WHERE {where_clause}"
        count_rows = self.db.execute_query(count_query, tuple(params))
        total = count_rows[0]['total'] if count_rows else 0
        
        # 获取帖子列表
        query = f"""
            SELECT d.*, 
                   u.nickname as author_name, u.avatar as author_avatar,
                   (SELECT COUNT(*) FROM discussion WHERE parent_id = d.id) as reply_count,
                   (SELECT MAX(created_at) FROM discussion WHERE parent_id = d.id) as last_reply_time
            FROM discussion d
            JOIN user u ON d.user_id = u.id
            WHERE {where_clause}
            ORDER BY d.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        
        rows = self.db.execute_query(query, tuple(params))
        
        return {
            'posts': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def get_popular_discussions(self, course_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门讨论帖子（按回复数排序）"""
        query = """
            SELECT d.*, 
                   u.nickname as author_name, u.avatar as author_avatar,
                   (SELECT COUNT(*) FROM discussion WHERE parent_id = d.id) as reply_count
            FROM discussion d
            JOIN user u ON d.user_id = u.id
            WHERE d.course_id = ? AND d.parent_id IS NULL AND d.status = 'active'
            ORDER BY reply_count DESC, d.created_at DESC
            LIMIT ?
        """
        rows = self.db.execute_query(query, (course_id, limit))
        return [dict(row) for row in rows]

    def get_user_discussions(self, user_id: int, page: int = 1, 
                            page_size: int = 20) -> Dict[str, Any]:
        """获取用户的讨论帖子"""
        offset = (page - 1) * page_size
        
        # 获取总数
        count_query = """
            SELECT COUNT(*) as total 
            FROM discussion 
            WHERE user_id = ? AND parent_id IS NULL AND status = 'active'
        """
        count_rows = self.db.execute_query(count_query, (user_id,))
        total = count_rows[0]['total'] if count_rows else 0
        
        # 获取帖子列表
        query = """
            SELECT d.*, 
                   u.nickname as author_name, u.avatar as author_avatar,
                   (SELECT COUNT(*) FROM discussion WHERE parent_id = d.id) as reply_count,
                   (SELECT MAX(created_at) FROM discussion WHERE parent_id = d.id) as last_reply_time
            FROM discussion d
            JOIN user u ON d.user_id = u.id
            WHERE d.user_id = ? AND d.parent_id IS NULL AND d.status = 'active'
            ORDER BY d.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = self.db.execute_query(query, (user_id, page_size, offset))
        
        return {
            'posts': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def mark_as_solved(self, post_id: int, user_id: int) -> bool:
        """标记帖子为已解决（仅限教师或帖子作者）"""
        # 验证用户权限
        check_query = "SELECT user_id, course_id FROM discussion WHERE id = ?"
        rows = self.db.execute_query(check_query, (post_id,))
        if not rows:
            raise ResourceNotFoundError("帖子不存在")
        
        post_user_id = rows[0]['user_id']
        course_id = rows[0]['course_id']
        
        if post_user_id != user_id:
            # 检查是否是课程教师
            if course_id:
                teacher_query = """
                    SELECT teacher_id FROM course WHERE id = ?
                """
                teacher_rows = self.db.execute_query(teacher_query, (course_id,))
                if not teacher_rows or teacher_rows[0]['teacher_id'] != user_id:
                    # 检查是否是管理员
                    user_query = "SELECT role FROM user WHERE id = ?"
                    user_rows = self.db.execute_query(user_query, (user_id,))
                    if not user_rows or user_rows[0]['role'] != 'admin':
                        raise ValidationError("没有权限标记此帖子")
        
        query = "UPDATE discussion SET status = 'closed' WHERE id = ?"
        result = self.db.execute_update(query, (post_id,))
        if result is not None:
            logger.info(f"Discussion post marked as solved: {post_id}")
            return True
        return False

    def get_discussion_statistics(self, course_id: int) -> Dict[str, Any]:
        """获取讨论区统计信息"""
        # 帖子统计
        post_query = """
            SELECT 
                COUNT(*) as total_posts,
                COUNT(CASE WHEN parent_id IS NULL THEN 1 END) as main_posts,
                COUNT(CASE WHEN parent_id IS NOT NULL THEN 1 END) as replies,
                COUNT(CASE WHEN status = 'closed' THEN 1 END) as solved_posts
            FROM discussion
            WHERE course_id = ? AND status != 'archived'
        """
        post_stats = self.db.execute_query(post_query, (course_id,))
        
        # 活跃用户
        active_user_query = """
            SELECT 
                COUNT(DISTINCT user_id) as active_users,
                u.nickname as most_active_user,
                MAX(post_count) as max_posts
            FROM (
                SELECT user_id, COUNT(*) as post_count
                FROM discussion
                WHERE course_id = ? AND status != 'archived'
                GROUP BY user_id
                ORDER BY post_count DESC
                LIMIT 1
            ) user_stats
            JOIN user u ON user_stats.user_id = u.id
        """
        active_user_stats = self.db.execute_query(active_user_query, (course_id,))
        
        # 最近活动
        recent_activity_query = """
            SELECT 
                COUNT(*) as posts_last_week,
                COUNT(CASE WHEN created_at >= datetime('now', '-1 day') THEN 1 END) as posts_last_day
            FROM discussion
            WHERE course_id = ? AND status != 'archived'
        """
        recent_activity_stats = self.db.execute_query(recent_activity_query, (course_id,))
        
        return {
            'post_stats': dict(post_stats[0]) if post_stats else {},
            'active_user_stats': dict(active_user_stats[0]) if active_user_stats else {},
            'recent_activity_stats': dict(recent_activity_stats[0]) if recent_activity_stats else {}
        }

    def pin_post(self, post_id: int, user_id: int) -> bool:
        """置顶帖子（仅限教师）"""
        # 验证用户是否是教师
        user_query = "SELECT role FROM user WHERE id = ?"
        user_rows = self.db.execute_query(user_query, (user_id,))
        if not user_rows or user_rows[0]['role'] not in ['teacher', 'admin']:
            raise ValidationError("只有教师可以置顶帖子")
        
        # 首先取消所有置顶
        unpin_query = "UPDATE discussion SET title = REPLACE(title, '[置顶] ', '') WHERE title LIKE '[置顶] %'"
        self.db.execute_update(unpin_query)
        
        # 置顶指定帖子
        pin_query = "UPDATE discussion SET title = '[置顶] ' || title WHERE id = ?"
        result = self.db.execute_update(pin_query, (post_id,))
        
        if result is not None:
            logger.info(f"Discussion post pinned: {post_id}")
            return True
        return False