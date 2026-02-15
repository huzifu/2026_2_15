"""
学生仪表板
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
from ui.student_courses import StudentCoursesFrame
from ui.student_assignments import StudentAssignmentsFrame
from ui.student_grades import StudentGradesFrame
from ui.student_discussion import StudentDiscussionFrame
from ui.student_resources import StudentResourcesFrame

class StudentDashboard(ttk.Frame):
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
        self.after(30000, self.refresh_notifications)

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True)
        
        # 头部
        self.header = Header(
            main_container,
            title=f"学生端 - {self.user.nickname}",
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
                {"text": "📊 学习仪表板", "command": self.show_dashboard, "icon": "dashboard"},
                {"text": "📚 我的课程", "command": self.show_courses, "icon": "course"},
                {"text": "📝 我的作业", "command": self.show_assignments, "icon": "assignment"},
                {"text": "📊 我的成绩", "command": self.show_grades, "icon": "grade"},
                {"text": "💬 讨论区", "command": self.show_discussion, "icon": "discussion"},
                {"text": "📁 学习资源", "command": self.show_resources, "icon": "resource"},
                {"text": "📈 学习分析", "command": self.show_analytics, "icon": "analytics"},
                {"text": "🔔 通知中心", "command": self.show_notifications, "icon": "notification"},
                {"text": "⚙️ 个人设置", "command": self.show_settings, "icon": "settings"}
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
        """显示学习仪表板"""
        self.content_area.clear()
        
        # 创建仪表板框架
        dashboard_frame = ttk.Frame(self.content_area)
        dashboard_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 欢迎标题
        welcome_label = ttk.Label(
            dashboard_frame,
            text=f"欢迎，{self.user.nickname}同学！",
            font=("Helvetica", 18, "bold")
        )
        welcome_label.pack(anchor=W, pady=(0, 20))
        
        # 统计卡片容器
        stats_container = ttk.Frame(dashboard_frame)
        stats_container.pack(fill=X, pady=(0, 20))
        
        # 获取统计数据
        try:
            # 课程统计
            courses = self.course_service.get_available_courses(self.user.id)
            course_count = len(courses)
            enrolled_courses = len([c for c in courses if c.get('student_progress')])
            
            # 作业统计
            assignments = []
            pending_assignments = 0
            submitted_assignments = 0
            
            for course in courses:
                if course.get('student_progress'):
                    course_assignments = self.assignment_service.get_assignments_by_course(course['id'])
                    assignments.extend(course_assignments)
            
            assignment_count = len(assignments)
            
            # 检查每个作业的提交状态
            for assignment in assignments:
                submissions = self.submission_service.get_student_submissions(self.user.id)
                submitted = any(s['assignment_id'] == assignment.id for s in submissions)
                
                if submitted:
                    submitted_assignments += 1
                else:
                    pending_assignments += 1
            
            # 成绩统计
            grades = self.gradebook_service.get_student_grades(self.user.id)
            grade_count = len(grades)
            average_score = sum(g['score'] for g in grades if g['score']) / grade_count if grade_count > 0 else 0
            
        except Exception as e:
            print(f"获取统计数据失败: {e}")
            course_count = enrolled_courses = assignment_count = 0
            pending_assignments = submitted_assignments = grade_count = average_score = 0
        
        # 统计卡片
        stats_data = [
            {"title": "可选课程", "value": course_count, "icon": "📚", "color": "primary"},
            {"title": "已选课程", "value": enrolled_courses, "icon": "✅", "color": "success"},
            {"title": "总作业数", "value": assignment_count, "icon": "📝", "color": "info"},
            {"title": "待完成作业", "value": pending_assignments, "icon": "⏳", "color": "warning"},
            {"title": "已提交作业", "value": submitted_assignments, "icon": "📤", "color": "success"},
            {"title": "已获成绩", "value": grade_count, "icon": "📊", "color": "danger"},
            {"title": "平均成绩", "value": f"{average_score:.1f}", "icon": "⭐", "color": "warning"},
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
            {"text": "查看课程", "command": self.show_courses, "icon": "📚"},
            {"text": "完成作业", "command": self.show_assignments, "icon": "📝"},
            {"text": "查看成绩", "command": self.show_grades, "icon": "📊"},
            {"text": "参与讨论", "command": self.show_discussion, "icon": "💬"},
            {"text": "学习资源", "command": self.show_resources, "icon": "📁"},
            {"text": "学习分析", "command": self.show_analytics, "icon": "📈"}
        ]
        
        for i, action in enumerate(actions):
            btn = ttk.Button(
                quick_actions_frame,
                text=f"{action['icon']} {action['text']}",
                command=action["command"],
                bootstyle="outline"
            )
            btn.pack(side=LEFT, padx=5)
        
        # 最近学习
        recent_learning_frame = ttk.LabelFrame(dashboard_frame, text="最近学习", padding=10)
        recent_learning_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        # 添加学习记录列表
        learning_tree = ttk.Treeview(
            recent_learning_frame,
            columns=("time", "course", "activity", "progress"),
            show="headings",
            height=8
        )
        
        learning_tree.heading("time", text="时间")
        learning_tree.heading("course", text="课程")
        learning_tree.heading("activity", text="活动")
        learning_tree.heading("progress", text="进度")
        
        learning_tree.column("time", width=150)
        learning_tree.column("course", width=200)
        learning_tree.column("activity", width=200)
        learning_tree.column("progress", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(recent_learning_frame, orient=VERTICAL, command=learning_tree.yview)
        learning_tree.configure(yscrollcommand=scrollbar.set)
        
        learning_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 添加示例学习记录
        sample_learning = [
            ("今天 10:30", "Python编程", "完成第3章练习", "100%"),
            ("今天 09:15", "数据结构", "观看链表视频", "75%"),
            ("昨天 16:45", "算法设计", "提交作业", "已提交"),
            ("昨天 14:20", "数据库原理", "参与讨论", "新回复"),
            ("前天 11:10", "Web开发", "完成项目", "95%")
        ]
        
        for record in sample_learning:
            learning_tree.insert("", END, values=record)
        
        # 待完成作业
        pending_frame = ttk.LabelFrame(dashboard_frame, text="即将到期的作业", padding=10)
        pending_frame.pack(fill=BOTH, expand=True)
        
        # 添加作业列表
        assignment_tree = ttk.Treeview(
            pending_frame,
            columns=("course", "assignment", "deadline", "status"),
            show="headings",
            height=5
        )
        
        assignment_tree.heading("course", text="课程")
        assignment_tree.heading("assignment", text="作业")
        assignment_tree.heading("deadline", text="截止时间")
        assignment_tree.heading("status", text="状态")
        
        assignment_tree.column("course", width=150)
        assignment_tree.column("assignment", width=200)
        assignment_tree.column("deadline", width=150)
        assignment_tree.column("status", width=100)
        
        # 添加滚动条
        scrollbar2 = ttk.Scrollbar(pending_frame, orient=VERTICAL, command=assignment_tree.yview)
        assignment_tree.configure(yscrollcommand=scrollbar2.set)
        
        assignment_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar2.pack(side=RIGHT, fill=Y)
        
        # 添加示例作业
        sample_assignments = [
            ("Python编程", "函数与模块练习", "2024-12-20", "未开始"),
            ("数据结构", "链表实现作业", "2024-12-22", "进行中"),
            ("算法设计", "排序算法分析", "2024-12-25", "未开始"),
            ("数据库原理", "SQL查询练习", "2024-12-28", "已完成"),
            ("Web开发", "前端项目", "2024-12-30", "进行中")
        ]
        
        for assignment in sample_assignments:
            assignment_tree.insert("", END, values=assignment)

    def show_courses(self):
        """显示我的课程"""
        self.content_area.clear()
        courses_frame = StudentCoursesFrame(
            self.content_area,
            self.user,
            self.course_service,
            self.class_service
        )
        courses_frame.pack(fill=BOTH, expand=True)

    def show_assignments(self):
        """显示我的作业"""
        self.content_area.clear()
        assignments_frame = StudentAssignmentsFrame(
            self.content_area,
            self.user,
            self.assignment_service,
            self.submission_service,
            self.course_service
        )
        assignments_frame.pack(fill=BOTH, expand=True)

    def show_grades(self):
        """显示我的成绩"""
        self.content_area.clear()
        grades_frame = StudentGradesFrame(
            self.content_area,
            self.user,
            self.gradebook_service,
            self.course_service
        )
        grades_frame.pack(fill=BOTH, expand=True)

    def show_discussion(self):
        """显示讨论区"""
        self.content_area.clear()
        discussion_frame = StudentDiscussionFrame(
            self.content_area,
            self.user,
            self.discussion_service,
            self.course_service
        )
        discussion_frame.pack(fill=BOTH, expand=True)

    def show_resources(self):
        """显示学习资源"""
        self.content_area.clear()
        resources_frame = StudentResourcesFrame(
            self.content_area,
            self.user,
            self.course_service
        )
        resources_frame.pack(fill=BOTH, expand=True)

    def show_analytics(self):
        """显示学习分析"""
        self.content_area.clear()
        
        analytics_frame = ttk.Frame(self.content_area)
        analytics_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            analytics_frame,
            text="学习分析",
            font=("Helvetica", 16, "bold")
        ).pack(anchor=W, pady=(0, 20))
        
        # 这里可以添加学习分析图表
        ttk.Label(
            analytics_frame,
            text="学习分析功能正在开发中...",
            font=("Helvetica", 12)
        ).pack(expand=True)

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
        """显示个人设置"""
        self.content_area.clear()
        
        settings_frame = ttk.Frame(self.content_area)
        settings_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            settings_frame,
            text="个人设置",
            font=("Helvetica", 16, "bold")
        ).pack(anchor=W, pady=(0, 20))
        
        # 设置选项
        settings_options = [
            ("个人资料", self.show_profile_settings),
            ("账户安全", self.show_security_settings),
            ("通知设置", self.show_notification_settings),
            ("学习偏好", self.show_preference_settings),
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

    def show_preference_settings(self):
        """显示学习偏好设置"""
        from ui.dialogs import PreferenceSettingsDialog
        dialog = PreferenceSettingsDialog(self, self.user)
        dialog.grab_set()

    def show_about(self):
        """显示关于对话框"""
        from ui.dialogs import AboutDialog
        dialog = AboutDialog(self)
        dialog.grab_set()