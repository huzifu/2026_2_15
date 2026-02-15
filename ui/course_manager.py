"""
课程管理界面
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from ui.components import DataTable, SearchBar, Pagination, MessageDialog

class CourseManagerFrame(ttk.Frame):
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
            text="课程管理",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 工具栏
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 创建课程按钮
        create_btn = ttk.Button(
            toolbar,
            text="➕ 创建课程",
            command=self.create_course,
            bootstyle="success"
        )
        create_btn.pack(side=LEFT, padx=(0, 10))
        
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
            values=["all", "draft", "published", "archived"],
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
        
        # 课程表格
        columns = [
            {"id": "id", "text": "ID", "width": 60},
            {"id": "title", "text": "课程标题", "width": 250},
            {"id": "class_name", "text": "关联班级", "width": 150},
            {"id": "chapter_count", "text": "章节数", "width": 80},
            {"id": "status", "text": "状态", "width": 100},
            {"id": "enrolled_count", "text": "学习人数", "width": 100},
            {"id": "created_at", "text": "创建时间", "width": 150}
        ]
        
        self.course_table = DataTable(
            main_container,
            columns=columns,
            height=15,
            selectmode="browse"
        )
        self.course_table.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 绑定双击事件
        self.course_table.tree.bind("<Double-1>", self.on_course_double_click)
        
        # 操作按钮区域
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=X, pady=(0, 10))
        
        # 查看详情按钮
        view_btn = ttk.Button(
            action_frame,
            text="👁️ 查看详情",
            command=self.view_course_details,
            bootstyle="outline"
        )
        view_btn.pack(side=LEFT, padx=(0, 5))
        
        # 编辑按钮
        edit_btn = ttk.Button(
            action_frame,
            text="✏️ 编辑",
            command=self.edit_course,
            bootstyle="outline"
        )
        edit_btn.pack(side=LEFT, padx=(0, 5))
        
        # 管理内容按钮
        manage_content_btn = ttk.Button(
            action_frame,
            text="📚 管理内容",
            command=self.manage_content,
            bootstyle="outline"
        )
        manage_content_btn.pack(side=LEFT, padx=(0, 5))
        
        # 发布/归档按钮
        self.publish_btn = ttk.Button(
            action_frame,
            text="📢 发布",
            command=self.publish_course,
            bootstyle="outline-success"
        )
        self.publish_btn.pack(side=LEFT, padx=(0, 5))
        
        # 删除按钮
        delete_btn = ttk.Button(
            action_frame,
            text="🗑️ 删除",
            command=self.delete_course,
            bootstyle="outline-danger"
        )
        delete_btn.pack(side=LEFT, padx=(0, 5))
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_container, text="统计信息", padding=10)
        stats_frame.pack(fill=X)
        
        # 创建统计标签
        self.stats_labels = {}
        stats_data = [
            ("total_courses", "课程总数", "0"),
            ("published_courses", "已发布", "0"),
            ("draft_courses", "草稿", "0"),
            ("total_enrolled", "总学习人数", "0")
        ]
        
        for i, (key, label, value) in enumerate(stats_data):
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.pack(side=LEFT, padx=20)
            
            ttk.Label(
                stat_frame,
                text=label,
                font=("Helvetica", 9)
            ).pack()
            
            self.stats_labels[key] = ttk.Label(
                stat_frame,
                text=value,
                font=("Helvetica", 14, "bold")
            )
            self.stats_labels[key].pack()

    def load_courses(self):
        """加载课程列表"""
        try:
            status = self.status_var.get()
            if status == "all":
                courses = self.course_service.get_courses_by_teacher(self.user.id)
            else:
                courses = self.course_service.get_courses_by_teacher(self.user.id, status=status)
            
            table_data = []
            
            for course in courses:
                # 获取班级名称
                class_name = "未关联"
                if course.class_id:
                    class_info = self.class_service.get_class_by_id(course.class_id)
                    if class_info:
                        class_name = class_info.name
                
                # 获取章节数
                chapters = self.course_service.get_chapters(course.id)
                chapter_count = len(chapters)
                
                # 获取学习人数
                stats = self.course_service.get_course_statistics(course.id)
                enrolled_count = stats.get('student_stats', {}).get('enrolled_students', 0)
                
                table_data.append([
                    course.id,
                    course.title,
                    class_name,
                    chapter_count,
                    course.status,
                    enrolled_count,
                    course.created_at
                ])
            
            self.course_table.update_data(table_data)
            self.update_statistics(courses)
            self.update_button_states()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载课程失败: {e}")

    def update_statistics(self, courses):
        """更新统计信息"""
        if not courses:
            for key in self.stats_labels:
                self.stats_labels[key].configure(text="0")
            return
        
        total_courses = len(courses)
        published_courses = len([c for c in courses if c.status == 'published'])
        draft_courses = len([c for c in courses if c.status == 'draft'])
        
        total_enrolled = 0
        for course in courses:
            stats = self.course_service.get_course_statistics(course.id)
            total_enrolled += stats.get('student_stats', {}).get('enrolled_students', 0)
        
        self.stats_labels["total_courses"].configure(text=str(total_courses))
        self.stats_labels["published_courses"].configure(text=str(published_courses))
        self.stats_labels["draft_courses"].configure(text=str(draft_courses))
        self.stats_labels["total_enrolled"].configure(text=str(total_enrolled))

    def update_button_states(self):
        """更新按钮状态"""
        selected = self.course_table.get_selected()
        if not selected:
            self.publish_btn.configure(state="disabled")
            return
        
        status = selected[4]  # 状态列
        if status == 'draft':
            self.publish_btn.configure(text="📢 发布", bootstyle="outline-success", state="normal")
        elif status == 'published':
            self.publish_btn.configure(text="📁 归档", bootstyle="outline-warning", state="normal")
        elif status == 'archived':
            self.publish_btn.configure(text="📤 恢复", bootstyle="outline-info", state="normal")
        else:
            self.publish_btn.configure(state="disabled")

    def search_courses(self, keyword):
        """搜索课程"""
        try:
            courses = self.course_service.search_courses(keyword=keyword, teacher_id=self.user.id)
            table_data = []
            
            for course in courses:
                # 获取班级名称
                class_name = "未关联"
                if course.get('class_id'):
                    class_info = self.class_service.get_class_by_id(course['class_id'])
                    if class_info:
                        class_name = class_info.name
                
                table_data.append([
                    course['id'],
                    course['title'],
                    class_name,
                    course.get('chapter_count', 0),
                    course['status'],
                    course.get('enrolled_count', 0),
                    course['created_at']
                ])
            
            self.course_table.update_data(table_data)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"搜索课程失败: {e}")

    def on_status_changed(self, event):
        """状态筛选改变事件"""
        self.load_courses()

    def create_course(self):
        """创建课程"""
        from ui.dialogs import CreateCourseDialog
        dialog = CreateCourseDialog(self, self.user, self.course_service, self.class_service)
        dialog.grab_set()
        self.wait_window(dialog)
        self.load_courses()

    def view_course_details(self):
        """查看课程详情"""
        selected = self.course_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")
            return
        
        course_id = selected[0]
        from ui.dialogs import CourseDetailsDialog
        dialog = CourseDetailsDialog(self, course_id, self.course_service, self.class_service)
        dialog.grab_set()

    def edit_course(self):
        """编辑课程"""
        selected = self.course_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")
            return
        
        course_id = selected[0]
        from ui.dialogs import EditCourseDialog
        dialog = EditCourseDialog(self, course_id, self.course_service)
        dialog.grab_set()
        self.wait_window(dialog)
        self.load_courses()

    def manage_content(self):
        """管理课程内容"""
        selected = self.course_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")
            return
        
        course_id = selected[0]
        from ui.dialogs import ManageCourseContentDialog
        dialog = ManageCourseContentDialog(self, course_id, self.course_service)
        dialog.grab_set()

    def publish_course(self):
        """发布/归档/恢复课程"""
        selected = self.course_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")
            return
        
        course_id = selected[0]
        course_title = selected[1]
        current_status = selected[4]
        
        try:
            if current_status == 'draft':
                # 发布课程
                if MessageDialog.ask_yesno(self, "确认发布", f"确定要发布课程 '{course_title}' 吗？"):
                    success = self.course_service.publish_course(course_id)
                    if success:
                        MessageDialog.show_info(self, "成功", "课程已发布")
                        self.load_courses()
                    else:
                        MessageDialog.show_error(self, "错误", "发布课程失败")
            
            elif current_status == 'published':
                # 归档课程
                if MessageDialog.ask_yesno(self, "确认归档", f"确定要归档课程 '{course_title}' 吗？"):
                    success = self.course_service.archive_course(course_id)
                    if success:
                        MessageDialog.show_info(self, "成功", "课程已归档")
                        self.load_courses()
                    else:
                        MessageDialog.show_error(self, "错误", "归档课程失败")
            
            elif current_status == 'archived':
                # 恢复课程
                if MessageDialog.ask_yesno(self, "确认恢复", f"确定要恢复课程 '{course_title}' 吗？"):
                    success = self.course_service.update_course(course_id, status='draft')
                    if success:
                        MessageDialog.show_info(self, "成功", "课程已恢复为草稿")
                        self.load_courses()
                    else:
                        MessageDialog.show_error(self, "错误", "恢复课程失败")
        
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"操作失败: {e}")

    def delete_course(self):
        """删除课程"""
        selected = self.course_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")
            return
        
        course_id = selected[0]
        course_title = selected[1]
        
        if not MessageDialog.ask_yesno(self, "确认删除", f"确定要删除课程 '{course_title}' 吗？"):
            return
        
        try:
            success = self.course_service.archive_course(course_id)
            if success:
                MessageDialog.show_info(self, "成功", "课程已删除")
                self.load_courses()
            else:
                MessageDialog.show_error(self, "错误", "删除课程失败")
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"删除课程失败: {e}")

    def on_course_double_click(self, event):
        """课程双击��件"""
        self.view_course_details()