"""
UI测试脚本 - 验证系统是否能正常启动
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")
    
    try:
        # 测试核心模块
        print("  - 导入核心模块...")
        from modules.db_manager import DBManager
        from modules.auth import AuthManager
        from modules.logger import setup_logger
        print("    ✓ 核心模块导入成功")
        
        # 测试服务模块
        print("  - 导入服务模块...")
        from modules.class_service import ClassService
        from modules.course_service import CourseService
        from modules.assignment_service import AssignmentService
        from modules.submission_service import SubmissionService
        from modules.discussion_service import DiscussionService
        from modules.notification_service import NotificationService
        from modules.gradebook_service import GradebookService
        from modules.analytics_service import AnalyticsService
        print("    ✓ 服务模块导入成功")
        
        # 测试UI模块
        print("  - 导入UI模块...")
        from ui.login_frame import LoginFrame
        from ui.teacher_dashboard import TeacherDashboard
        from ui.student_dashboard import StudentDashboard
        from ui.components import Header, Sidebar, ContentArea, StatCard
        print("    ✓ UI模块导入成功")
        
        # 测试UI管理器模块
        print("  - 导入UI管理器模块...")
        from ui.class_manager import ClassManagerFrame
        from ui.course_manager import CourseManagerFrame
        from ui.grade_manager import GradeManagerFrame
        from ui.discussion_manager import DiscussionManagerFrame
        from ui.notification_center import NotificationCenter
        print("    ✓ UI管理器模块导入成功")
        
        # 测试学生UI模块
        print("  - 导入学生UI模块...")
        from ui.student_courses import StudentCoursesFrame
        from ui.student_assignments import StudentAssignmentsFrame
        from ui.student_grades import StudentGradesFrame
        from ui.student_discussion import StudentDiscussionFrame
        from ui.student_resources import StudentResourcesFrame
        print("    ✓ 学生UI模块导入成功")
        
        # 测试对话框模块
        print("  - 导入对话框模块...")
        from ui.dialogs import (
            CreateClassDialog,
            CreateCourseDialog,
            CreateAssignmentDialog,
            CreatePostDialog,
            ReplyPostDialog
        )
        print("    ✓ 对话框模块导入成功")
        
        print("\n✓ 所有模块导入测试通过！")
        return True
        
    except Exception as e:
        print(f"\n✗ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    try:
        from modules.db_manager import DBManager
        db = DBManager()
        
        # 测试查询
        result = db.execute_query("SELECT COUNT(*) as count FROM user")
        user_count = result[0]['count'] if result else 0
        
        print(f"  ✓ 数据库连接成功")
        print(f"  ✓ 当前用户数: {user_count}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 数据库连接失败: {e}")
        return False

def test_services():
    """测试服务初始化"""
    print("\n测试服务初始化...")
    
    try:
        from modules.db_manager import DBManager
        from modules.class_service import ClassService
        from modules.course_service import CourseService
        from modules.assignment_service import AssignmentService
        from modules.submission_service import SubmissionService
        from modules.discussion_service import DiscussionService
        from modules.notification_service import NotificationService
        from modules.gradebook_service import GradebookService
        from modules.analytics_service import AnalyticsService
        
        db = DBManager()
        
        # 初始化所有服务
        class_service = ClassService(db)
        course_service = CourseService(db)
        assignment_service = AssignmentService(db)
        submission_service = SubmissionService(db)
        discussion_service = DiscussionService(db)
        notification_service = NotificationService(db)
        gradebook_service = GradebookService(db)
        analytics_service = AnalyticsService(db)
        
        print("  ✓ 所有服务初始化成功")
        return True
        
    except Exception as e:
        print(f"  ✗ 服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("智能教学管理系统 - UI测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("模块导入", test_imports),
        ("数据库连接", test_database),
        ("服务初始化", test_services)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ 所有测试通过！系统可以正常启动。")
        print("\n运行 'python main.py' 启动系统")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
