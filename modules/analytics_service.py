"""
数据分析服务 - 提供学情分析功能
"""
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_assignment_statistics(self, assignment_id):
        """
        获取作业统计信息
        返回: {
            'total_submissions': int,
            'avg_score': float,
            'max_score': float,
            'min_score': float,
            'pass_rate': float
        }
        """
        query = """
            SELECT 
                COUNT(*) as total,
                AVG(total_score) as avg_score,
                MAX(total_score) as max_score,
                MIN(total_score) as min_score
            FROM submission
            WHERE assignment_id = ?
        """
        rows = self.db.execute_query(query, (assignment_id,))
        
        if not rows or rows[0]['total'] == 0:
            return {
                'total_submissions': 0,
                'avg_score': 0,
                'max_score': 0,
                'min_score': 0,
                'pass_rate': 0
            }
        
        row = rows[0]
        
        # 计算及格率（假设60%为及格线）
        total_possible = self._get_assignment_total_score(assignment_id)
        pass_threshold = total_possible * 0.6
        
        pass_query = """
            SELECT COUNT(*) as pass_count
            FROM submission
            WHERE assignment_id = ? AND total_score >= ?
        """
        pass_rows = self.db.execute_query(pass_query, (assignment_id, pass_threshold))
        pass_count = pass_rows[0]['pass_count'] if pass_rows else 0
        
        pass_rate = (pass_count / row['total']) * 100 if row['total'] > 0 else 0
        
        return {
            'total_submissions': row['total'],
            'avg_score': round(row['avg_score'], 2) if row['avg_score'] else 0,
            'max_score': row['max_score'] if row['max_score'] else 0,
            'min_score': row['min_score'] if row['min_score'] else 0,
            'pass_rate': round(pass_rate, 2),
            'total_possible': total_possible
        }

    def _get_assignment_total_score(self, assignment_id):
        """获取作业总分"""
        query = "SELECT SUM(score) as total FROM question WHERE assignment_id = ?"
        rows = self.db.execute_query(query, (assignment_id,))
        return rows[0]['total'] if rows and rows[0]['total'] else 0

    def get_question_statistics(self, assignment_id):
        """
        获取每道题的统计信息
        返回: list of {
            'question_id': int,
            'content': str,
            'avg_score': float,
            'max_score': float,
            'correct_rate': float
        }
        """
        query = """
            SELECT 
                q.id as question_id,
                q.content,
                q.score as max_score,
                q.type,
                AVG(sd.score) as avg_score,
                COUNT(CASE WHEN sd.is_correct = 1 THEN 1 END) as correct_count,
                COUNT(*) as total_count
            FROM question q
            LEFT JOIN submission_detail sd ON q.id = sd.question_id
            WHERE q.assignment_id = ?
            GROUP BY q.id
            ORDER BY q.id
        """
        rows = self.db.execute_query(query, (assignment_id,))
        
        results = []
        for row in rows:
            correct_rate = 0
            if row['type'] in ['single_choice', 'multi_choice', 'boolean', 'fill_in']:
                # 客观题计算正确率
                if row['total_count'] > 0:
                    correct_rate = (row['correct_count'] / row['total_count']) * 100
            
            results.append({
                'question_id': row['question_id'],
                'content': row['content'][:50] + '...' if len(row['content']) > 50 else row['content'],
                'type': row['type'],
                'avg_score': round(row['avg_score'], 2) if row['avg_score'] else 0,
                'max_score': row['max_score'],
                'correct_rate': round(correct_rate, 2),
                'total_count': row['total_count']
            })
        
        return results

    def get_student_performance(self, student_id):
        """
        获取学生整体表现
        返回: {
            'total_assignments': int,
            'completed': int,
            'avg_score': float,
            'recent_submissions': list
        }
        """
        # 总体统计
        query = """
            SELECT 
                COUNT(DISTINCT a.id) as total_assignments,
                COUNT(s.id) as completed,
                AVG(s.total_score) as avg_score
            FROM assignment a
            LEFT JOIN submission s ON a.id = s.assignment_id AND s.student_id = ?
        """
        rows = self.db.execute_query(query, (student_id,))
        row = rows[0] if rows else {}
        
        # 最近提交
        recent_query = """
            SELECT 
                a.title,
                s.total_score,
                s.submit_time
            FROM submission s
            JOIN assignment a ON s.assignment_id = a.id
            WHERE s.student_id = ?
            ORDER BY s.submit_time DESC
            LIMIT 5
        """
        recent = self.db.execute_query(recent_query, (student_id,))
        
        return {
            'total_assignments': row.get('total_assignments', 0),
            'completed': row.get('completed', 0),
            'avg_score': round(row.get('avg_score', 0), 2) if row.get('avg_score') else 0,
            'recent_submissions': [dict(r) for r in recent]
        }

    def get_class_ranking(self, assignment_id, limit=10):
        """
        获取作业排名
        返回: list of {rank, student_name, score}
        """
        query = """
            SELECT 
                u.nickname as student_name,
                s.total_score as score,
                s.submit_time
            FROM submission s
            JOIN user u ON s.student_id = u.id
            WHERE s.assignment_id = ?
            ORDER BY s.total_score DESC, s.submit_time ASC
            LIMIT ?
        """
        rows = self.db.execute_query(query, (assignment_id, limit))
        
        rankings = []
        for idx, row in enumerate(rows, 1):
            rankings.append({
                'rank': idx,
                'student_name': row['student_name'],
                'score': row['score'],
                'submit_time': row['submit_time']
            })
        
        return rankings

    def get_score_distribution(self, assignment_id):
        """
        获取分数分布
        返回: dict {score_range: count}
        """
        query = """
            SELECT total_score
            FROM submission
            WHERE assignment_id = ?
        """
        rows = self.db.execute_query(query, (assignment_id,))
        
        # 分数段统计
        distribution = {
            '0-59': 0,
            '60-69': 0,
            '70-79': 0,
            '80-89': 0,
            '90-100': 0
        }
        
        total_possible = self._get_assignment_total_score(assignment_id)
        
        for row in rows:
            score = row['total_score']
            percentage = (score / total_possible * 100) if total_possible > 0 else 0
            
            if percentage < 60:
                distribution['0-59'] += 1
            elif percentage < 70:
                distribution['60-69'] += 1
            elif percentage < 80:
                distribution['70-79'] += 1
            elif percentage < 90:
                distribution['80-89'] += 1
            else:
                distribution['90-100'] += 1
        
        return distribution
