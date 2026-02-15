"""
教师仪表板
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from ui.components import Header, Sidebar, ContentArea, NotificationBadge
from ui.class_manager import ClassManagerFrame
from ui.course_manager import CourseManagerFrame
from ui.assignment_frames import AssignmentManagerFrame
from ui.grade_manager import GradeManagerFrame
from ui.discussion_manager import DiscussionManagerFrame
from ui.analytics_dashboard import AnalyticsDashboardFrame

class TeacherDashboard(ttk.Frame):
    def __init__(self, parent, user, db, class_service, course_service, 
                 assignment_service, submission_service, discussion_service,
                 notification_service, gradebook_service, analytics_service, logout_callback):
        super().__init__(parent)
        self.user = user
        self.db = db
        self.class_service = class_service
        self.course_service = course_service
        self.assignment_service = assignment_service
        self.submission_service = submission_service
        self.discussion_service = discussion_service
        self.notification_service = notification_service
        self.gradebook_service = gradebook_service
        self.analytics_service = analytics_service
        self.logout_callback = logout_callback
        
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        self.load_notifications()
        
        # 设置定时刷新通知
        self.after(30000, self.refresh_notifications)  # 每30秒刷新一次

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True)
        
        # 头部
        self.header = Header(
            main_container,
            title=f"教师端 - {self.user.nickname}",
            user=self.user,
            on_logout=self.logout_callback,
            on_notification_click=self.show_notifications
        )
        self.header.pack(fill=X)
        
        # 主体内容区域
        content_container = ttk.Frame(main_container)
        content_container.pack(fill=BOTH, expand=True)
        
        # 侧边栏
        self.sidebar = Sidebar(
            content_container,
            menu_items=[
                {"text": "📊 仪表板", "command": self.show_dashboard, "icon": "dashboard"},
                {"text": "👥 班级管理", "command": self.show_class_manager, "icon": "class"},
                {"text": "📚 课程管理", "command": self.show_course_manager, "icon": "course"},
                {"text": "📝 作业管理", "command": self.show_assignment_manager, "icon": "assignment"},
                {"text": "📊 成绩管理", "command": self.show_grade_manager, "icon": "grade"},
                {"text": "💬 讨论区", "command": self.show_discussion_manager, "icon": "discussion"},
                {"text": "📈 数据分析", "command": self.show_analytics, "icon": "analytics"},
                {"text": "🔔 通知中心", "command": self.show_notifications, "icon": "notification"},
                {"text": "⚙️ 系统设置", "command": self.show_settings, "icon": "settings"}
            ],
            selected_index=0
        )
        self.sidebar.pack(side=LEFT, fill=Y, padx=(0, 2))
        
        # 内容区域
        self.content_area = ContentArea(content_container)
        self.content_area.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 显示默认页面
        self.show_dashboard()

    def load_notifications(self):
        """加载通知"""
        try:
            unread_count = self.notification_service.get_notification_count(
                self.user.id, unread_only=True
            )
            self.header.update_notification_count(unread_count)
        except Exception as e:
            print(f"加载通知失败: {e}")

    def refresh_notifications(self):
        """刷新通知"""
        self.load_notifications()
        # 继续定时刷新
        self.after(30000, self.refresh_notifications)

    def show_dashboard(self):
        """显示仪表板"""
        self.content_area.clear()
        
        # 创建仪表板框架
        dashboard_frame = ttk.Frame(self.content_area)
        dashboard_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 欢迎标题
        welcome_label = ttk.Label(
            dashboard_frame,
            text=f"欢迎回来，{self.user.nickname}老师！",
            font=("Helvetica", 18, "bold")
        )
        welcome_label.pack(anchor=W, pady=(0, 20))
        
        # 统计卡片容器
        stats_container = ttk.Frame(dashboard_frame)
        stats_container.pack(fill=X, pady=(0, 20))
        
        # 获取统计数据
        try:
            # 班级统计
            classes = self.class_service.get_classes_by_teacher(self.user.id)
            class_count = len(classes)
            total_students = sum(
                len(self.class_service.get_class_students(c.id)) 
                for c in classes
            )
            
            # 课程统计
            courses = self.course_service.get_courses_by_teacher(self.user.id)
            course_count = len(courses)
            published_courses = len([c for c in courses if c.status == 'published'])
            
            # 作业统计
            assignments = []
            for course in courses:
                course_assignments = self.assignment_service.get_assignments_by_course(course.id)
                assignments.extend(course_assignments)
            
            assignment_count = len(assignments)
            graded_assignments = len([a for a in assignments if a.status == 'graded'])
            
            # 待批改作业
            pending_grading = 0
            for assignment in assignments:
                if assignment.status == 'published':
                    submissions = self.submission_service.get_assignment_submissions(assignment.id)
                    pending_grading += len([s for s in submissions if s['grading_status'] == 'pending'])
            
        except Exception as e:
            print(f"获取统计数据失败: {e}")
            class_count = total_students = course_count = published_courses = 0
            assignment_count = graded_assignments = pending_grading = 0
        
        # 统计卡片
        stats_data = [
            {"title": "班级数量", "value": class_count, "icon": "👥", "color": "primary"},
            {"title": "学生总数", "value": total_students, "icon": "👨‍🎓", "color": "success"},
            {"title": "课程数量", "value": course_count, "icon": "📚", "color": "info"},
            {"title": "已发布课程", "value": published_courses, "icon": "📢", "color": "warning"},
            {"title": "作业总数", "value": assignment_count, "icon": "📝", "color": "danger"},
            {"title": "已批改作业", "value": graded_assignments, "icon": "✅", "color": "success"},
            {"title": "待批改作业", "value": pending_grading, "icon": "⏳", "color": "warning"},
            {"title": "今日通知", "value": "0", "icon": "🔔", "color": "info"}
        ]
        
        # 创建统计卡片
        from ui.components import StatCard
        for i, stat in enumerate(stats_data):
            row = i // 4
            col = i % 4
            
            card = StatCard(
                stats_container,
                title=stat["title"],
                value=stat["value"],
                icon=stat["icon"],
                color=stat["color"]
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # 设置网格权重
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # 快速操作区域
        quick_actions_frame = ttk.LabelFrame(dashboard_frame, text="快速操作", padding=10)
        quick_actions_frame.pack(fill=X, pady=(0, 20))
        
        actions = [
            {"text": "新建班级", "command": self.show_create_class, "icon": "➕"},
            {"text": "创建课程", "command": self.show_create_course, "icon": "📚"},
            {"text": "布置作业", "command": self.show_create_assignment, "icon": "📝"},
            {"text": "批改作业", "command": self.show_grading, "icon": "✏️"},
            {"text": "发布通知", "command": self.show_create_notification, "icon": "📢"},
            {"text": "查看讨论", "command": self.show_discussion_manager, "icon": "💬"}
        ]
        
        for i, action in enumerate(actions):
            btn = ttk.Button(
                quick_actions_frame,
                text=f"{action['icon']} {action['text']}",
                command=action["command"],
                bootstyle="outline"
            )
            btn.pack(side=LEFT, padx=5)
        
        # 最近活动
        recent_activity_frame = ttk.LabelFrame(dashboard_frame, text="最近活动", padding=10)
        recent_activity_frame.pack(fill=BOTH, expand=True)
        
        # 添加活动列表
        activity_tree = ttk.Treeview(
            recent_activity_frame,
            columns=("time", "activity", "details"),
            show="headings",
            height=8
        )
        
        activity_tree.heading("time", text="时间")
        activity_tree.heading("activity", text="活动")
        activity_tree.heading("details", text="详情")
        
        activity_tree.column("time", width=150)
        activity_tree.column("activity", width=200)
        activity_tree.column("details", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(recent_activity_frame, orient=VERTICAL, command=activity_tree.yview)
        activity_tree.configure(yscrollcommand=scrollbar.set)
        
        activity_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 添加示例活动
        sample_activities = [
            ("10:30", "批改作业", "Python基础测试 - 已批改15份"),
            ("09:15", "回复讨论", "回答了学生关于作业的问题"),
            ("昨天 16:45", "创建作业", "数据结构作业 - 链表专题"),
            ("昨天 14:20", "发布成绩", "算法设计练习成绩已发布"),
            ("前天 11:10", "更新课程", "Python高级编程 - 新增装饰器章节")
        ]
        
        for activity in sample_activities:
            activity_tree.insert("", END, values=activity)

    def show_class_manager(self):
        """显示班级管理"""
        self.content_area.clear()
        class_frame = ClassManagerFrame(
            self.content_area,
            self.user,
            self.class_service,
            self.course_service
        )
        class_frame.pack(fill=BOTH, expand=True)

    def show_course_manager(self):
        """显示课程管理"""
        self.content_area.clear()
        course_frame = CourseManagerFrame(
            self.content_area,
            self.user,
            self.course_service,
            self.class_service
        )
        course_frame.pack(fill=BOTH, expand=True)

    def show_assignment_manager(self):
        """显示作业管理"""
        self.content_area.clear()
        assignment_frame = AssignmentManagerFrame(
            self.content_area,
            self.user,
            self.assignment_service,
            self.course_service,
            self.class_service
        )
        assignment_frame.pack(fill=BOTH, expand=True)

    def show_grade_manager(self):
        """显示成绩管理"""
        self.content_area.clear()
        grade_frame = GradeManagerFrame(
            self.content_area,
            self.user,
            self.gradebook_service,
            self.assignment_service,
            self.course_service,
            self.submission_service
        )
        grade_frame.pack(fill=BOTH, expand=True)

    def show_discussion_manager(self):
        """显示讨论区管理"""
        self.content_area.clear()
        discussion_frame = DiscussionManagerFrame(
            self.content_area,
            self.user,
            self.discussion_service,
            self.course_service
        )
        discussion_frame.pack(fill=BOTH, expand=True)

    def show_analytics(self):
        """显示数据分析"""
        self.content_area.clear()
        analytics_frame = AnalyticsDashboardFrame(
            self.content_area,
            self.user,
            self.analytics_service,
            self.class_service,
            self.course_service,
            self.gradebook_service
        )
        analytics_frame.pack(fill=BOTH, expand=True)

    def show_notifications(self):
        """显示通知中心"""
        self.content_area.clear()
        
        from ui.notification_center import NotificationCenter
        notification_frame = NotificationCenter(
            self.content_area,
            self.user,
            self.notification_service
        )
        notification_frame.pack(fill=BOTH, expand=True)

    def show_settings(self):
        """显示系统设置"""
        self.content_area.clear()
        
        settings_frame = ttk.Frame(self.content_area)
        settings_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            settings_frame,
            text="系统设置",
            font=("Helvetica", 16, "bold")
        ).pack(anchor=W, pady=(0, 20))
        
        # 设置选项
        settings_options = [
            ("个人资料", self.show_profile_settings),
            ("账户安全", self.show_security_settings),
            ("通知设置", self.show_notification_settings),
            ("界面主题", self.show_theme_settings),
            ("数据备份", self.show_backup_settings),
            ("关于系统", self.show_about)
        ]
        
        for text, command in settings_options:
            btn = ttk.Button(
                settings_frame,
                text=text,
                command=command,
                width=20
            )
            btn.pack(anchor=W, pady=5)

    def show_create_class(self):
        """显示创建班级对话框"""
        from ui.dialogs import CreateClassDialog
        dialog = CreateClassDialog(self, self.user, self.class_service)
        dialog.grab_set()

    def show_create_course(self):
        """显示创建课程对话框"""
        from ui.dialogs import CreateCourseDialog
        dialog = CreateCourseDialog(self, self.user, self.course_service, self.class_service)
        dialog.grab_set()

    def show_create_assignment(self):
        """显示创建作业对话框"""
        from ui.dialogs import CreateAssignmentDialog
        dialog = CreateAssignmentDialog(
            self, 
            self.user, 
            self.assignment_service,
            self.course_service,
            self.class_service
        )
        dialog.grab_set()

    def show_grading(self):
        """显示批改作业界面"""
        self.show_grade_manager()

    def show_create_notification(self):
        """显示创建通知对话框"""
        from ui.dialogs import CreateNotificationDialog
        dialog = CreateNotificationDialog(
            self,
            self.user,
            self.notification_service,
            self.class_service
        )
        dialog.grab_set()

    def show_profile_settings(self):
        """显示个人资料设置"""
        from ui.dialogs import ProfileSettingsDialog
        dialog = ProfileSettingsDialog(self, self.user, self.db)
        dialog.grab_set()

    def show_security_settings(self):
        """显示安全设置"""
        from ui.dialogs import SecuritySettingsDialog
        dialog = SecuritySettingsDialog(self, self.user, self.db)
        dialog.grab_set()

    def show_notification_settings(self):
        """显示通知设置"""
        from ui.dialogs import NotificationSettingsDialog
        dialog = NotificationSettingsDialog(self, self.user)
        dialog.grab_set()

    def show_theme_settings(self):
        """显示主题设置"""
        from ui.dialogs import ThemeSettingsDialog
        dialog = ThemeSettingsDialog(self)
        dialog.grab_set()

    def show_backup_settings(self):
        """显示备份设置"""
        from ui.dialogs import BackupSettingsDialog
        dialog = BackupSettingsDialog(self, self.db)
        dialog.grab_set()

    def show_about(self):
        """显示关于对话框"""
        from ui.dialogs import AboutDialog
        dialog = AboutDialog(self)
        dialog.grab_set()