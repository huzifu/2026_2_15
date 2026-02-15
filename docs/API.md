# API 文档

## 认证模块 (AuthManager)

### login(username, password)
用户登录

**参数:**
- username: 用户名
- password: 密码

**返回:**
- (bool, str): (成功/失败, 消息)

**示例:**
```python
auth = AuthManager(db)
success, msg = auth.login("teacher1", "123456")
if success:
    print(f"当前用户: {auth.current_user.nickname}")
```

### register(username, password, role, nickname)
用户注册

**参数:**
- username: 用户名（4-20位字母数字下划线）
- password: 密码（至少6位）
- role: 角色（teacher/student/admin）
- nickname: 昵称

**返回:**
- (bool, str): (成功/失败, 消息)

### logout()
退出登录

## 作业服务 (AssignmentService)

### create_assignment(title, description, teacher_id, deadline)
创建作业

**参数:**
- title: 作业标题
- description: 作业描述
- teacher_id: 教师ID
- deadline: 截止时间（YYYY-MM-DD HH:MM:SS）

**返回:**
- int: 作业ID

**异常:**
- ValidationError: 验证失败

### get_assignments_by_teacher(teacher_id)
获取教师的所有作业

**返回:**
- list[Assignment]: 作业列表

### add_question(assignment_id, question_type, content, answer, score, analysis)
添加题目

**参数:**
- assignment_id: 作业ID
- question_type: 题型（single_choice/multi_choice/boolean/fill_in/subjective）
- content: 题目内容
- answer: 标准答案
- score: 分值
- analysis: 题目解析

**返回:**
- int: 题目ID

## 提交服务 (SubmissionService)

### submit_assignment(student_id, assignment_id, answers)
提交作业并自动评分

**参数:**
- student_id: 学生ID
- assignment_id: 作业ID
- answers: dict {question_id: student_answer}

**返回:**
- (int, float): (提交ID, 总分)

**示例:**
```python
service = SubmissionService(db)
answers = {
    1: "A",
    2: "Python是一种高级编程语言..."
}
submission_id, score = service.submit_assignment(student_id, assignment_id, answers)
print(f"提交成功，得分: {score}")
```

### get_student_submissions(student_id)
获取学生的所有提交记录

**返回:**
- list[dict]: 提交记录列表

### manual_grade(submission_detail_id, score, feedback)
教师手动评分

**参数:**
- submission_detail_id: 提交详情ID
- score: 分数
- feedback: 评语

## AI 评分 (AIGrader)

### grade_objective(student_answer, standard_answer)
评分客观题

**返回:**
- bool: 是否正确

### grade_subjective(student_answer, standard_answer, max_score)
评分主观题

**返回:**
- (float, str): (得分, 反馈)

**算法:**
1. 使用 jieba 分词
2. TF-IDF 向量化
3. 计算余弦相似度
4. 相似度 × 满分 = 得分

## 分析服务 (AnalyticsService)

### get_assignment_statistics(assignment_id)
获取作业统计信息

**返回:**
```python
{
    'total_submissions': int,
    'avg_score': float,
    'max_score': float,
    'min_score': float,
    'pass_rate': float,
    'total_possible': float
}
```

### get_question_statistics(assignment_id)
获取每道题的统计信息

**返回:**
```python
[{
    'question_id': int,
    'content': str,
    'type': str,
    'avg_score': float,
    'max_score': float,
    'correct_rate': float,
    'total_count': int
}]
```

### get_class_ranking(assignment_id, limit=10)
获取作业排名

**返回:**
```python
[{
    'rank': int,
    'student_name': str,
    'score': float,
    'submit_time': str
}]
```

## 数据库管理 (DBManager)

### execute_query(query, params=())
执行查询语句

**参数:**
- query: SQL 查询语句
- params: 参数元组

**返回:**
- list[sqlite3.Row]: 查询结果

### execute_update(query, params=())
执行更新语句

**返回:**
- int: 最后插入的行ID

### execute_many(query, params_list)
批量执行更新语句

**返回:**
- int: 影响的行数

## 数据模型

### User
```python
class User:
    id: int
    username: str
    role: str
    nickname: str
    created_at: str
```

### Assignment
```python
class Assignment:
    id: int
    title: str
    description: str
    teacher_id: int
    deadline: str
    create_time: str
```

### Question
```python
class Question:
    id: int
    assignment_id: int
    type: str
    content: str
    answer: str
    score: float
    analysis: str
```

## 异常类型

### ValidationError
数据验证失败

### ResourceNotFoundError
资源不存在

### AuthenticationError
认证失败

### DatabaseError
数据库操作失败
