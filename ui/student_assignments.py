"""
学生作业界面
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

class StudentAssignmentsFrame(ttk.Frame):
    def __init__(self, parent, user, assignment_service, submission_service, course_service):
        super().__init__(parent)
        self.user = user
        self.assignment_service = assignment_service
        self.submission_service = submission_service
        self.course_service = course_service
        
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        self.load_assignments()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_container,
            text="我的作业",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 工具栏
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 状态筛选
        status_frame = ttk.Frame(toolbar)
        status_frame.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(status_frame, text="状态:").pack(side=LEFT, padx=(0, 5))
        
        self.status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=["all", "pending", "submitted", "graded", "overdue"],
            state="readonly",
            width=10
        )
        status_combo.pack(side=LEFT)
        status_combo.bind("<<ComboboxSelected>>", self.on_status_changed)
        
        # 搜索栏
        self.search_bar = SearchBar(
            toolbar,
            placeholder="搜索作业标题...",
            on_search=self.search_assignments
        )
        self.search_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            toolbar,
            text="🔄 刷新",
            command=self.load_assignments,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 作业表格
        columns = [
            {"id": "id", "text": "ID", "width": 60},
            {"id": "title", "text": "作业标题", "width": 250},
            {"id": "course", "text": "课程", "width": 150},
            {"id": "deadline", "text": "截止时间", "width": 150},
            {"id": "status", "text": "状态", "width": 100},
            {"id": "score", "text": "成绩", "width": 80},
            {"id": "submission_time", "text": "提交时间", "width": 150}
        ]
        
        self.assignment_table = DataTable(
            main_container,
            columns=columns,
            height=15,
            selectmode="browse"
        )
        self.assignment_table.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 绑定双击事件
        self.assignment_table.tree.bind("<Double-1>", self.on_assignment_double_click)
        
        # 操作按钮区域
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=X)
        
        # 查看详情按钮
        view_btn = ttk.Button(
            action_frame,
            text="👁️ 查看详情",
            command=self.view_assignment_details,
            bootstyle="outline"
        )
        view_btn.pack(side=LEFT, padx=(0, 5))
        
        # 提交作业按钮
        submit_btn = ttk.Button(
            action_frame,
            text="📤 提交作业",
            command=self.submit_assignment,
            bootstyle="success"
        )
        submit_btn.pack(side=LEFT, padx=(0, 5))
        
        # 查看提交按钮
        view_submission_btn = ttk.Button(
            action_frame,
            text="📄 查看提交",
            command=self.view_submission,
            bootstyle="outline"
        )
        view_submission_btn.pack(side=LEFT, padx=(0, 5))
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_container, text="作业统计", padding=10)
        stats_frame.pack(fill=X, pady=(10, 0))
        
        # 创建统计标签
        self.stats_labels = {}
        stats_data = [
            ("total_assignments", "总作业数", "0"),
            ("pending_assignments", "待完成", "0"),
            ("submitted_assignments", "已提交", "0"),
            ("graded_assignments", "已批改", "0"),
            ("overdue_assignments", "已逾期", "0")
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

    def load_assignments(self):
        """加载作业列表"""
        try:
            # 获取学生已选课程
            courses = self.course_service.get_available_courses(self.user.id)
            enrolled_course_ids = [c['id'] for c in courses if c.get('student_progress')]
            
            table_data = []
            assignment_stats = {
                'total': 0,
                'pending': 0,
                'submitted': 0,
                'graded': 0,
                'overdue': 0
            }
            
            for course_id in enrolled_course_ids:
                # 获取课程作业
                assignments = self.assignment_service.get_assignments_by_course(course_id)
                
                for assignment in assignments:
                    assignment_stats['total'] += 1
                    
                    # 获取提交状态
                    submissions = self.submission_service.get_student_submissions(self.user.id)
                    submission = None
                    for sub in submissions:
                        if sub['assignment_id'] == assignment.id:
                            submission = sub
                            break
                    
                    # 确定状态
                    status = "未开始"
                    score = ""
                    submission_time = ""
                    
                    if submission:
                        if submission['grading_status'] == 'graded':
                            status = "已批改"
                            score = f"{submission['total_score']:.1f}"
                            assignment_stats['graded'] += 1
                        else:
                            status = "已提交"
                            assignment_stats['submitted'] += 1
                        submission_time = submission.get('submit_time', '')
                    else:
                        # 检查是否逾期
                        from datetime import datetime
                        if assignment.deadline:
                            deadline = datetime.strptime(assignment.deadline, '%Y-%m-%d %H:%M:%S')
                            if datetime.now() > deadline:
                                status = "已逾期"
                                assignment_stats['overdue'] += 1
                            else:
                                status = "待完成"
                                assignment_stats['pending'] += 1
                        else:
                            status = "待完成"
                            assignment_stats['pending'] += 1
                    
                    # 获取课程名称
                    course = self.course_service.get_course_by_id(course_id)
                    course_name = course.title if course else "未知课程"
                    
                    table_data.append([
                        assignment.id,
                        assignment.title,
                        course_name,
                        assignment.deadline or "无截止时间",
                        status,
                        score,
                        submission_time
                    ])
            
            # 应用状态筛选
            status_filter = self.status_var.get()
            if status_filter != "all":
                filtered_data = []
                for row in table_data:
                    if status_filter == "pending" and row[4] == "待完成":
                        filtered_data.append(row)
                    elif status_filter == "submitted" and row[4] == "已提交":
                        filtered_data.append(row)
                    elif status_filter == "graded" and row[4] == "已批改":
                        filtered_data.append(row)
                    elif status_filter == "overdue" and row[4] == "已逾期":
                        filtered_data.append(row)
                table_data = filtered_data
            
            self.assignment_table.update_data(table_data)
            self.update_statistics(assignment_stats)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载作业失败: {e}")

    def update_statistics(self, stats):
        """更新统计信息"""
        self.stats_labels["total_assignments"].configure(text=str(stats['total']))
        self.stats_labels["pending_assignments"].configure(text=str(stats['pending']))
        self.stats_labels["submitted_assignments"].configure(text=str(stats['submitted']))
        self.stats_labels["graded_assignments"].configure(text=str(stats['graded']))
        self.stats_labels["overdue_assignments"].configure(text=str(stats['overdue']))

    def on_status_changed(self, event):
        """状态筛选改变事件"""
        self.load_assignments()

    def search_assignments(self, keyword):
        """搜索作业"""
        # 这里可以实现作业搜索功能
        pass

    def view_assignment_details(self):
        """查看作业详情"""
        selected = self.assignment_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个作业")
            return
        
        assignment_id = selected[0]
        from ui.dialogs import AssignmentDetailsDialog
        dialog = AssignmentDetailsDialog(self, assignment_id, self.assignment_service)
        dialog.grab_set()

    def submit_assignment(self):
        """提交作业"""
        selected = self.assignment_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个作业")
            return
        
        assignment_id = selected[0]
        status = selected[4]
        
        if status in ["已提交", "已批改"]:
            MessageDialog.show_warning(self, "提示", "该作业已经提交")
            return
        
        from ui.dialogs import SubmitAssignmentDialog
        dialog = SubmitAssignmentDialog(
            self, 
            assignment_id, 
            self.user, 
            self.assignment_service,
            self.submission_service
        )
        dialog.grab_set()
        self.wait_window(dialog)
        self.load_assignments()

    def view_submission(self):
        """查看提交"""
        selected = self.assignment_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个作业")
            return
        
        assignment_id = selected[0]
        status = selected[4]
        
        if status == "未开始":
            MessageDialog.show_warning(self, "提示", "该作业尚未提交")
            return
        
        from ui.dialogs import ViewSubmissionDialog
        dialog = ViewSubmissionDialog(
            self, 
            assignment_id, 
            self.user, 
            self.submission_service
        )
        dialog.grab_set()

    def on_assignment_double_click(self, event):
        """作业双击事件"""
        self.view_assignment_details()