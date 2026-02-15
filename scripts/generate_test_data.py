"""
生成测试数据脚本
用于快速填充系统测试数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import DBManager
from modules.auth import AuthManager
from modules.assignment_service import AssignmentService
from modules.submission_service import SubmissionService
from datetime import datetime, timedelta

def generate_users(db, auth):
    """生成测试用户"""
    print("生成测试用户...")
    
    # 生成教师
    teachers = [
        ("teacher2", "123456", "teacher", "王老师"),
        ("teacher3", "123456", "teacher", "李老师"),
    ]
    
    for username, password, role, nickname in teachers:
        try:
            auth.register(username, password, role, nickname)
            print(f"  ✓ 创建教师: {nickname}")
        except:
            print(f"  - 教师已存在: {nickname}")
    
    # 生成学生
    students = [
        ("student2", "123456", "student", "张同学"),
        ("student3", "123456", "student", "刘同学"),
        ("student4", "123456", "student", "陈同学"),
        ("student5", "123456", "student", "杨同学"),
    ]
    
    for username, password, role, nickname in students:
        try:
            auth.register(username, password, role, nickname)
            print(f"  ✓ 创建学生: {nickname}")
        except:
            print(f"  - 学生已存在: {nickname}")

def generate_assignments(db, assignment_service):
    """生成测试作业"""
    print("\n生成测试作业...")
    
    # 获取教师ID
    query = "SELECT id FROM user WHERE role = 'teacher' LIMIT 1"
    rows = db.execute_query(query)
    if not rows:
        print("  ✗ 没有找到教师账号")
        return []
    
    teacher_id = rows[0]['id']
    
    assignments = [
        {
            'title': 'Python 基础测试',
            'description': '测试 Python 基础知识掌握情况',
            'deadline': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            'title': '数据结构作业',
            'description': '链表、栈、队列相关题目',
            'deadline': (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            'title': '算法设计练习',
            'description': '排序和搜索算法实现',
            'deadline': (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    assignment_ids = []
    for assign in assignments:
        try:
            aid = assignment_service.create_assignment(
                assign['title'],
                assign['description'],
                teacher_id,
                assign['deadline']
            )
            assignment_ids.append(aid)
            print(f"  ✓ 创建作业: {assign['title']}")
        except Exception as e:
            print(f"  ✗ 创建作业失败: {e}")
    
    return assignment_ids

def generate_questions(db, assignment_service, assignment_ids):
    """生成测试题目"""
    print("\n生成测试题目...")
    
    if not assignment_ids:
        print("  ✗ 没有作业可添加题目")
        return
    
    # 为第一个作业添加题目
    assignment_id = assignment_ids[0]
    
    questions = [
        {
            'type': 'single_choice',
            'content': 'Python 是什么类型的语言？\nA. 编译型\nB. 解释型\nC. 汇编语言\nD. 机器语言',
            'answer': 'B',
            'score': 10,
            'analysis': 'Python 是一种解释型的高级编程语言'
        },
        {
            'type': 'single_choice',
            'content': '以下哪个不是 Python 的数据类型？\nA. list\nB. tuple\nC. array\nD. dict',
            'answer': 'C',
            'score': 10,
            'analysis': 'array 不是 Python 内置数据类型，需要导入 numpy'
        },
        {
            'type': 'fill_in',
            'content': 'Python 中用于定义函数的关键字是 ______',
            'answer': 'def',
            'score': 10,
            'analysis': 'def 关键字用于定义函数'
        },
        {
            'type': 'subjective',
            'content': '请简述 Python 列表(list)和元组(tuple)的区别',
            'answer': '列表是可变的，可以修改元素；元组是不可变的，创建后不能修改。列表使用方括号[]，元组使用圆括号()。',
            'score': 20,
            'analysis': '主要考察可变性、语法、使用场景等方面'
        },
        {
            'type': 'subjective',
            'content': '什么是 Python 的装饰器？请举例说明',
            'answer': '装饰器是一种设计模式，用于在不修改原函数代码的情况下增加额外功能。使用@符号语法。例如：@staticmethod、@property等。',
            'score': 20,
            'analysis': '考察装饰器的概念、语法和应用'
        }
    ]
    
    for q in questions:
        try:
            assignment_service.add_question(
                assignment_id,
                q['type'],
                q['content'],
                q['answer'],
                q['score'],
                q['analysis']
            )
            print(f"  ✓ 添加题目: {q['content'][:30]}...")
        except Exception as e:
            print(f"  ✗ 添加题目失败: {e}")

def generate_submissions(db, submission_service, assignment_ids):
    """生成测试提交"""
    print("\n生成测试提交...")
    
    if not assignment_ids:
        print("  ✗ 没有作业可提交")
        return
    
    # 获取学生ID
    query = "SELECT id FROM user WHERE role = 'student'"
    students = db.execute_query(query)
    
    if not students:
        print("  ✗ 没有找到学生账号")
        return
    
    # 获取第一个作业的题目
    assignment_id = assignment_ids[0]
    query = "SELECT id FROM question WHERE assignment_id = ?"
    questions = db.execute_query(query, (assignment_id,))
    
    if not questions:
        print("  ✗ 作业没有题目")
        return
    
    # 为每个学生生成提交
    for student in students[:2]:  # 只为前两个学生生成
        student_id = student['id']
        
        # 模拟答案
        answers = {
            questions[0]['id']: 'B',
            questions[1]['id']: 'C',
            questions[2]['id']: 'def',
            questions[3]['id']: '列表可以修改，元组不能修改。列表用[]，元组用()。',
            questions[4]['id']: '装饰器是用来修改函数行为的工具，使用@符号。'
        }
        
        try:
            submission_id, score = submission_service.submit_assignment(
                student_id, assignment_id, answers
            )
            print(f"  ✓ 学生 {student_id} 提交作业，得分: {score:.1f}")
        except Exception as e:
            print(f"  ✗ 提交失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("AI 智能教学助手系统 - 测试数据生成器")
    print("=" * 50)
    
    db = DBManager()
    auth = AuthManager(db)
    assignment_service = AssignmentService(db)
    submission_service = SubmissionService(db)
    
    # 生成数据
    generate_users(db, auth)
    assignment_ids = generate_assignments(db, assignment_service)
    generate_questions(db, assignment_service, assignment_ids)
    generate_submissions(db, submission_service, assignment_ids)
    
    print("\n" + "=" * 50)
    print("测试数据生成完成！")
    print("=" * 50)
    print("\n现在可以使用以下账号登录系统：")
    print("  教师: teacher1 / 123456")
    print("  学生: student1 / 123456")

if __name__ == "__main__":
    main()
