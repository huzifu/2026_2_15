"""
学生课程界面
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from ui.components import DataTable, SearchBar, MessageDialog

class StudentCoursesFrame(ttk.Frame):
    def __init__(self, parent, user, course_service, class_service):
        super().__init__(parent)
        self.user = user
        self.course_service = course_service
        self.class_service = class_service
        
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        self.load_courses()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_container,
            text="我的课程",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 工具栏
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 搜索栏
        self.search_bar = SearchBar(
            toolbar,
            placeholder="搜索课程标题或描述...",
            on_search=self.search_courses
        )
        self.search_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 状态筛选
        status_frame = ttk.Frame(toolbar)
        status_frame.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(status_frame, text="状态:").pack(side=LEFT, padx=(0, 5))
        
        self.status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=["all", "enrolled", "available"],
            state="readonly",
            width=10
        )
        status_combo.pack(side=LEFT)
        status_combo.bind("<<ComboboxSelected>>", self.on_status_changed)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            toolbar,
            text="🔄 刷新",
            command=self.load_courses,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 课程卡片容器
        self.courses_container = ttk.Frame(main_container)
        self.courses_container.pack(fill=BOTH, expand=True)
        
        # 创建网格布局
        self.courses_container.grid_columnconfigure(0, weight=1)
        self.courses_container.grid_columnconfigure(1, weight=1)
        self.courses_container.grid_columnconfigure(2, weight=1)

    def load_courses(self):
        """加载课程列表"""
        try:
            courses = self.course_service.get_available_courses(self.user.id)
            
            # 清除现有课程卡片
            for widget in self.courses_container.winfo_children():
                widget.destroy()
            
            if not courses:
                # 显示空状态
                empty_label = ttk.Label(
                    self.courses_container,
                    text="暂无课程",
                    font=("Helvetica", 14)
                )
                empty_label.pack(expand=True)
                return
            
            # 显示课程卡片
            for i, course in enumerate(courses):
                row = i // 3
                col = i % 3
                
                course_card = self.create_course_card(course)
                course_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载课程失败: {e}")

    def create_course_card(self, course):
        """创建课程卡片"""
        card = ttk.Frame(self.courses_container, padding=15)
        card.configure(bootstyle="light")
        
        # 课程标题
        title_label = ttk.Label(
            card,
            text=course['title'],
            font=("Helvetica", 14, "bold"),
            wraplength=250
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 教师信息
        teacher_frame = ttk.Frame(card)
        teacher_frame.pack(anchor=W, pady=(0, 5))
        
        ttk.Label(
            teacher_frame,
            text="👨‍🏫",
            font=("Helvetica", 12)
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Label(
            teacher_frame,
            text=f"教师: {course.get('teacher_name', '未知')}",
            font=("Helvetica", 10)
        ).pack(side=LEFT)
        
        # 章节信息
        chapter_frame = ttk.Frame(card)
        chapter_frame.pack(anchor=W, pady=(0, 5))
        
        ttk.Label(
            chapter_frame,
            text="📚",
            font=("Helvetica", 12)
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Label(
            chapter_frame,
            text=f"章节: {course.get('chapter_count', 0)}",
            font=("Helvetica", 10)
        ).pack(side=LEFT)
        
        # 学习进度
        if course.get('student_progress'):
            progress_frame = ttk.Frame(card)
            progress_frame.pack(anchor=W, pady=(0, 10))
            
            ttk.Label(
                progress_frame,
                text="📊",
                font=("Helvetica", 12)
            ).pack(side=LEFT, padx=(0, 5))
            
            progress = course.get('student_progress', 0)
            progress_label = ttk.Label(
                progress_frame,
                text=f"进度: {progress:.1f}%",
                font=("Helvetica", 10)
            )
            progress_label.pack(side=LEFT)
            
            # 进度条
            progress_bar = ttk.Progressbar(
                card,
                value=progress,
                bootstyle="success-striped"
            )
            progress_bar.pack(fill=X, pady=(0, 10))
        
        # 操作按钮
        button_frame = ttk.Frame(card)
        button_frame.pack(fill=X)
        
        if course.get('student_progress'):
            # 已选课程
            enter_btn = ttk.Button(
                button_frame,
                text="进入学习",
                command=lambda cid=course['id']: self.enter_course(cid),
                bootstyle="success"
            )
            enter_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
            
            drop_btn = ttk.Button(
                button_frame,
                text="退选",
                command=lambda cid=course['id']: self.drop_course(cid),
                bootstyle="outline-danger"
            )
            drop_btn.pack(side=RIGHT)
        else:
            # 可选课程
            enroll_btn = ttk.Button(
                button_frame,
                text="选课",
                command=lambda cid=course['id']: self.enroll_course(cid),
                bootstyle="primary"
            )
            enroll_btn.pack(fill=X)
        
        return card

    def search_courses(self, keyword):
        """搜索课程"""
        try:
            courses = self.course_service.search_courses(keyword=keyword, status='published')
            
            # 过滤已选课程
            available_courses = self.course_service.get_available_courses(self.user.id)
            enrolled_course_ids = {c['id'] for c in available_courses if c.get('student_progress')}
            
            # 清除现有课程卡片
            for widget in self.courses_container.winfo_children():
                widget.destroy()
            
            if not courses:
                # 显示空状态
                empty_label = ttk.Label(
                    self.courses_container,
                    text="未找到相关课程",
                    font=("Helvetica", 14)
                )
                empty_label.pack(expand=True)
                return
            
            # 显示搜索结果的课程卡片
            displayed_count = 0
            for i, course in enumerate(courses):
                # 标记是否已选
                course['student_progress'] = course['id'] in enrolled_course_ids
                
                row = displayed_count // 3
                col = displayed_count % 3
                
                course_card = self.create_course_card(course)
                course_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                displayed_count += 1
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"搜索课程失败: {e}")

    def on_status_changed(self, event):
        """状态筛选改变事件"""
        # 这里可以实现按状态筛选功能
        pass

    def enter_course(self, course_id):
        """进入课程学习"""
        from ui.dialogs import CourseLearningDialog
        dialog = CourseLearningDialog(self, course_id, self.user, self.course_service)
        dialog.grab_set()

    def enroll_course(self, course_id):
        """选课"""
        if not MessageDialog.ask_yesno(self, "确认选课", "确定要选择这门课程吗？"):
            return
        
        try:
            # 这里需要实现选课逻辑
            # 暂时显示成功消息
            MessageDialog.show_info(self, "成功", "选课成功")
            self.load_courses()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"选课失败: {e}")

    def drop_course(self, course_id):
        """退选课程"""
        if not MessageDialog.ask_yesno(self, "确认退选", "确定要退选这门课程吗？"):
            return
        
        try:
            # 这里需要实现退选逻辑
            # 暂时显示成功消息
            MessageDialog.show_info(self, "成功", "退选成功")
            self.load_courses()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"退选失败: {e}")