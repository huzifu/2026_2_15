import json
from datetime import datetime
from typing import Optional, List, Dict, Any

class User:
    def __init__(self, id, username, role, nickname, email=None, phone=None, 
                 avatar=None, bio=None, status='active', last_login=None, created_at=None):
        self.id = id
        self.username = username
        self.role = role
        self.nickname = nickname
        self.email = email
        self.phone = phone
        self.avatar = avatar
        self.bio = bio
        self.status = status
        self.last_login = last_login
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            role=row['role'],
            nickname=row['nickname'],
            email=row.get('email'),
            phone=row.get('phone'),
            avatar=row.get('avatar'),
            bio=row.get('bio'),
            status=row.get('status', 'active'),
            last_login=row.get('last_login'),
            created_at=row.get('created_at')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'nickname': self.nickname,
            'email': self.email,
            'avatar': self.avatar,
            'status': self.status
        }

class Class:
    def __init__(self, id, name, code, description, teacher_id, max_students=50, 
                 status='active', created_at=None):
        self.id = id
        self.name = name
        self.code = code
        self.description = description
        self.teacher_id = teacher_id
        self.max_students = max_students
        self.status = status
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Class(
            id=row['id'],
            name=row['name'],
            code=row['code'],
            description=row['description'],
            teacher_id=row['teacher_id'],
            max_students=row.get('max_students', 50),
            status=row.get('status', 'active'),
            created_at=row.get('created_at')
        )

class Course:
    def __init__(self, id, title, description, teacher_id, class_id=None, 
                 cover_image=None, status='draft', created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.cover_image = cover_image
        self.status = status
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Course(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            teacher_id=row['teacher_id'],
            class_id=row.get('class_id'),
            cover_image=row.get('cover_image'),
            status=row.get('status', 'draft'),
            created_at=row.get('created_at')
        )

class Chapter:
    def __init__(self, id, course_id, title, description, order_index=0, created_at=None):
        self.id = id
        self.course_id = course_id
        self.title = title
        self.description = description
        self.order_index = order_index
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Chapter(
            id=row['id'],
            course_id=row['course_id'],
            title=row['title'],
            description=row.get('description'),
            order_index=row.get('order_index', 0),
            created_at=row.get('created_at')
        )

class Assignment:
    def __init__(self, id, title, description, teacher_id, course_id=None, chapter_id=None,
                 type='homework', total_score=100, deadline=None, time_limit=None,
                 allow_late_submission=False, late_penalty=0, status='draft', created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.chapter_id = chapter_id
        self.type = type
        self.total_score = total_score
        self.deadline = deadline
        self.time_limit = time_limit
        self.allow_late_submission = allow_late_submission
        self.late_penalty = late_penalty
        self.status = status
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Assignment(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            teacher_id=row['teacher_id'],
            course_id=row.get('course_id'),
            chapter_id=row.get('chapter_id'),
            type=row.get('type', 'homework'),
            total_score=row.get('total_score', 100),
            deadline=row.get('deadline'),
            time_limit=row.get('time_limit'),
            allow_late_submission=bool(row.get('allow_late_submission', False)),
            late_penalty=row.get('late_penalty', 0),
            status=row.get('status', 'draft'),
            created_at=row.get('created_at')
        )

class Question:
    def __init__(self, id, assignment_id, type, content, options=None, answer=None,
                 score=0, difficulty='medium', tags=None, analysis=None, hint=None, created_at=None):
        self.id = id
        self.assignment_id = assignment_id
        self.type = type
        self.content = content
        self.options = json.loads(options) if options else [] if type in ['single_choice', 'multi_choice'] else None
        self.answer = answer
        self.score = score
        self.difficulty = difficulty
        self.tags = tags.split(',') if tags else []
        self.analysis = analysis
        self.hint = hint
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Question(
            id=row['id'],
            assignment_id=row['assignment_id'],
            type=row['type'],
            content=row['content'],
            options=row.get('options'),
            answer=row.get('answer'),
            score=row.get('score', 0),
            difficulty=row.get('difficulty', 'medium'),
            tags=row.get('tags'),
            analysis=row.get('analysis'),
            hint=row.get('hint'),
            created_at=row.get('created_at')
        )

class Submission:
    def __init__(self, id, student_id, assignment_id, total_score=None, grade=None,
                 feedback=None, submit_time=None, late_submission=False,
                 grading_status='pending', graded_by=None, graded_at=None):
        self.id = id
        self.student_id = student_id
        self.assignment_id = assignment_id
        self.total_score = total_score
        self.grade = grade
        self.feedback = feedback
        self.submit_time = submit_time
        self.late_submission = late_submission
        self.grading_status = grading_status
        self.graded_by = graded_by
        self.graded_at = graded_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Submission(
            id=row['id'],
            student_id=row['student_id'],
            assignment_id=row['assignment_id'],
            total_score=row.get('total_score'),
            grade=row.get('grade'),
            feedback=row.get('feedback'),
            submit_time=row.get('submit_time'),
            late_submission=bool(row.get('late_submission', False)),
            grading_status=row.get('grading_status', 'pending'),
            graded_by=row.get('graded_by'),
            graded_at=row.get('graded_at')
        )

class Discussion:
    def __init__(self, id, course_id=None, assignment_id=None, user_id=None, title=None,
                 content=None, parent_id=None, status='active', created_at=None, updated_at=None):
        self.id = id
        self.course_id = course_id
        self.assignment_id = assignment_id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.parent_id = parent_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Discussion(
            id=row['id'],
            course_id=row.get('course_id'),
            assignment_id=row.get('assignment_id'),
            user_id=row.get('user_id'),
            title=row.get('title'),
            content=row.get('content'),
            parent_id=row.get('parent_id'),
            status=row.get('status', 'active'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )

class Notification:
    def __init__(self, id, user_id, type, title, content=None, related_id=None,
                 related_type=None, is_read=False, created_at=None):
        self.id = id
        self.user_id = user_id
        self.type = type
        self.title = title
        self.content = content
        self.related_id = related_id
        self.related_type = related_type
        self.is_read = is_read
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Notification(
            id=row['id'],
            user_id=row['user_id'],
            type=row['type'],
            title=row['title'],
            content=row.get('content'),
            related_id=row.get('related_id'),
            related_type=row.get('related_type'),
            is_read=bool(row.get('is_read', False)),
            created_at=row.get('created_at')
        )

class LearningProgress:
    def __init__(self, id, student_id, course_id, chapter_id=None, content_id=None,
                 progress=0, status='in_progress', last_accessed=None, time_spent=0,
                 created_at=None, updated_at=None):
        self.id = id
        self.student_id = student_id
        self.course_id = course_id
        self.chapter_id = chapter_id
        self.content_id = content_id
        self.progress = progress
        self.status = status
        self.last_accessed = last_accessed
        self.time_spent = time_spent
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return LearningProgress(
            id=row['id'],
            student_id=row['student_id'],
            course_id=row['course_id'],
            chapter_id=row.get('chapter_id'),
            content_id=row.get('content_id'),
            progress=row.get('progress', 0),
            status=row.get('status', 'in_progress'),
            last_accessed=row.get('last_accessed'),
            time_spent=row.get('time_spent', 0),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )

class Resource:
    def __init__(self, id, title, description, file_path, file_type=None, file_size=None,
                 uploader_id=None, course_id=None, assignment_id=None, tags=None,
                 download_count=0, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.uploader_id = uploader_id
        self.course_id = course_id
        self.assignment_id = assignment_id
        self.tags = tags.split(',') if tags else []
        self.download_count = download_count
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Resource(
            id=row['id'],
            title=row['title'],
            description=row.get('description'),
            file_path=row['file_path'],
            file_type=row.get('file_type'),
            file_size=row.get('file_size'),
            uploader_id=row.get('uploader_id'),
            course_id=row.get('course_id'),
            assignment_id=row.get('assignment_id'),
            tags=row.get('tags'),
            download_count=row.get('download_count', 0),
            created_at=row.get('created_at')
        )
