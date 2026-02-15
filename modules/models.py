class User:
    def __init__(self, id, username, role, nickname, created_at=None):
        self.id = id
        self.username = username
        self.role = role
        self.nickname = nickname
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
            created_at=row['created_at']
        )

class Assignment:
    def __init__(self, id, title, description, teacher_id, deadline, create_time=None):
        self.id = id
        self.title = title
        self.description = description
        self.teacher_id = teacher_id
        self.deadline = deadline
        self.create_time = create_time

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Assignment(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            teacher_id=row['teacher_id'],
            deadline=row['deadline'],
            create_time=row['create_time']
        )

class Question:
    def __init__(self, id, assignment_id, type, content, answer, score, analysis):
        self.id = id
        self.assignment_id = assignment_id
        self.type = type
        self.content = content
        self.answer = answer
        self.score = score
        self.analysis = analysis

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Question(
            id=row['id'],
            assignment_id=row['assignment_id'],
            type=row['type'],
            content=row['content'],
            answer=row['answer'],
            score=row['score'],
            analysis=row['analysis']
        )
