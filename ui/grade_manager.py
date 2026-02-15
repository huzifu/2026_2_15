"""
成绩管理界面
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.components import DataTable, SearchBar, MessageDialog

# Windows 中文字体修复
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class GradeManagerFrame(ttk.Frame):
    def __init__(self, parent, user, gradebook_service, assignment_service, 
                 course_service, submission_service):
        super().__init__(parent)
        self.user = user
        self.gradebook_service = gradebook_service
        self.assignment_service = assignment_service
        self.course_service = course_service
        self.submission_service = submission_service
        
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
            text="成绩管理",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 课程选择区域
        course_frame = ttk.LabelFrame(main_container, text="选择课程", padding=10)
        course_frame.pack(fill=X, pady=(0, 10))
        
        # 课程选择下拉框
        ttk.Label(course_frame, text="课程:").pack(side=LEFT, padx=(0, 5))
        
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(
            course_frame,
            textvariable=self.course_var,
            state="readonly",
            width=40
        )
        self.course_combo.pack(side=LEFT, padx=(0, 10))
        self.course_combo.bind("<<ComboboxSelected>>", self.on_course_selected)
        
        # 作业选择下拉框
        ttk.Label(course_frame, text="作业:").pack(side=LEFT, padx=(0, 5))
        
        self.assignment_var = tk.StringVar()
        self.assignment_combo = ttk.Combobox(
            course_frame,
            textvariable=self.assignment_var,
            state="readonly",
            width=30
        )
        self.assignment_combo.pack(side=LEFT, padx=(0, 10))
        self.assignment_combo.bind("<<ComboboxSelected>>", self.on_assignment_selected)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            course_frame,
            text="🔄 刷新",
            command=self.load_courses,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 成绩表格区域
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 左侧：成绩表格
        left_frame = ttk.Frame(table_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 工具栏
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 导入成绩按钮
        import_btn = ttk.Button(
            toolbar,
            text="📥 导入成绩",
            command=self.import_grades,
            bootstyle="outline"
        )
        import_btn.pack(side=LEFT, padx=(0, 5))
        
        # 导出成绩按钮
        export_btn = ttk.Button(
            toolbar,
            text="📤 导出成绩",
            command=self.export_grades,
            bootstyle="outline"
        )
        export_btn.pack(side=LEFT, padx=(0, 5))
        
        # 批量编辑按钮
        bulk_edit_btn = ttk.Button(
            toolbar,
            text="✏️ 批量编辑",
            command=self.bulk_edit_grades,
            bootstyle="outline"
        )
        bulk_edit_btn.pack(side=LEFT, padx=(0, 5))
        
        # 搜索栏
        self.search_bar = SearchBar(
            toolbar,
            placeholder="搜索学生姓名...",
            on_search=self.search_students
        )
        self.search_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 成绩表格
        columns = [
            {"id": "student_id", "text": "学号", "width": 100},
            {"id": "name", "text": "姓名", "width": 120},
            {"id": "score", "text": "成绩", "width": 80},
            {"id": "grade", "text": "等级", "width": 80},
            {"id": "submission_time", "text": "提交时间", "width": 150},
            {"id": "status", "text": "状态", "width": 100},
            {"id": "comment", "text": "评语", "width": 200}
        ]
        
        self.grade_table = DataTable(
            left_frame,
            columns=columns,
            height=15,
            selectmode="browse"
        )
        self.grade_table.pack(fill=BOTH, expand=True)
        
        # 绑定双击事件
        self.grade_table.tree.bind("<Double-1>", self.on_grade_double_click)
        
        # 右侧：统计图表
        right_frame = ttk.Frame(table_frame, width=400)
        right_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        
        # 统计信息
        stats_frame = ttk.LabelFrame(right_frame, text="统计信息", padding=10)
        stats_frame.pack(fill=X, pady=(0, 10))
        
        self.stats_labels = {}
        stats_data = [
            ("total_students", "总人数", "0"),
            ("average_score", "平均分", "0"),
            ("highest_score", "最高分", "0"),
            ("lowest_score", "最低分", "0"),
            ("grade_a", "A等级", "0"),
            ("grade_b", "B等级", "0"),
            ("grade_c", "C等级", "0"),
            ("grade_d", "D等级", "0"),
            ("grade_f", "F等级", "0")
        ]
        
        for i, (key, label, value) in enumerate(stats_data):
            row = i // 3
            col = i % 3
            
            if col == 0:
                stat_row_frame = ttk.Frame(stats_frame)
                stat_row_frame.pack(fill=X, pady=2)
            
            stat_frame = ttk.Frame(stat_row_frame)
            stat_frame.pack(side=LEFT, padx=5, fill=X, expand=True)
            
            ttk.Label(
                stat_frame,
                text=label,
                font=("Helvetica", 9)
            ).pack(anchor=W)
            
            self.stats_labels[key] = ttk.Label(
                stat_frame,
                text=value,
                font=("Helvetica", 11, "bold")
            )
            self.stats_labels[key].pack(anchor=W)
        
        # 成绩分布图表
        chart_frame = ttk.LabelFrame(right_frame, text="成绩分布", padding=10)
        chart_frame.pack(fill=BOTH, expand=True)
        
        self.chart_canvas = None
        
        # 操作按钮区域
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=X)
        
        # 查看详情按钮
        view_btn = ttk.Button(
            action_frame,
            text="👁️ 查看详情",
            command=self.view_grade_details,
            bootstyle="outline"
        )
        view_btn.pack(side=LEFT, padx=(0, 5))
        
        # 编辑成绩按钮
        edit_btn = ttk.Button(
            action_frame,
            text="✏️ 编辑成绩",
            command=self.edit_grade,
            bootstyle="outline"
        )
        edit_btn.pack(side=LEFT, padx=(0, 5))
        
        # 生成报告按钮
        report_btn = ttk.Button(
            action_frame,
            text="📊 生成报告",
            command=self.generate_report,
            bootstyle="outline"
        )
        report_btn.pack(side=LEFT, padx=(0, 5))
        
        # 发布成绩按钮
        publish_btn = ttk.Button(
            action_frame,
            text="📢 发布成绩",
            command=self.publish_grades,
            bootstyle="success"
        )
        publish_btn.pack(side=LEFT, padx=(0, 5))

    def load_courses(self):
        """加载课程列表"""
        try:
            courses = self.course_service.get_courses_by_teacher(self.user.id, status='published')
            course_options = []
            self.course_map = {}
            
            for course in courses:
                course_options.append(f"{course.id}: {course.title}")
                self.course_map[course.id] = course
            
            self.course_combo['values'] = course_options
            
            if course_options:
                self.course_combo.current(0)
                self.on_course_selected(None)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载课程失败: {e}")

    def on_course_selected(self, event):
        """课程选择事件"""
        course_text = self.course_var.get()
        if not course_text:
            return
        
        try:
            course_id = int(course_text.split(":")[0])
            self.current_course_id = course_id
            
            # 加载作业列表
            assignments = self.assignment_service.get_assignments_by_course(course_id)
            assignment_options = ["全部作业"]
            self.assignment_map = {"全部作业": None}
            
            for assignment in assignments:
                assignment_options.append(f"{assignment.id}: {assignment.title}")
                self.assignment_map[assignment.id] = assignment
            
            self.assignment_combo['values'] = assignment_options
            self.assignment_combo.current(0)
            self.on_assignment_selected(None)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载作业失败: {e}")

    def on_assignment_selected(self, event):
        """作业选择事件"""
        assignment_text = self.assignment_var.get()
        if not assignment_text or not hasattr(self, 'current_course_id'):
            return
        
        try:
            if assignment_text == "全部作业":
                self.current_assignment_id = None
                self.load_course_grades()
            else:
                assignment_id = int(assignment_text.split(":")[0])
                self.current_assignment_id = assignment_id
                self.load_assignment_grades()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载成绩失败: {e}")

    def load_course_grades(self):
        """加载课程所有成绩"""
        try:
            grades_data = self.gradebook_service.get_course_grades(self.current_course_id)
            
            table_data = []
            for student in grades_data['students']:
                student_id = student['student_id']
                student_stats = grades_data['student_stats'].get(student_id, {})
                
                table_data.append([
                    student['username'],
                    student['nickname'],
                    student_stats.get('average_score', ''),
                    student_stats.get('average_grade', ''),
                    '',  # 提交时间
                    '已统计',  # 状态
                    ''  # 评语
                ])
            
            self.grade_table.update_data(table_data)
            self.update_statistics(grades_data)
            self.update_chart(grades_data)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载课程成绩失败: {e}")

    def load_assignment_grades(self):
        """加载作业成绩"""
        try:
            grades = self.gradebook_service.get_assignment_grades(self.current_assignment_id)
            
            table_data = []
            for grade in grades:
                table_data.append([
                    grade['username'],
                    grade['student_name'],
                    grade['score'] if grade['score'] is not None else '未评分',
                    grade['grade'] if grade['grade'] else '未评级',
                    grade.get('submit_time', ''),
                    '已提交' if grade.get('submit_time') else '未提交',
                    grade.get('comment', '')
                ])
            
            self.grade_table.update_data(table_data)
            self.update_assignment_statistics(grades)
            self.update_assignment_chart(grades)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载作业成绩失败: {e}")

    def update_statistics(self, grades_data):
        """更新统计信息"""
        overall_stats = grades_data.get('overall', {})
        
        self.stats_labels["total_students"].configure(
            text=str(overall_stats.get('total_students', 0))
        )
        self.stats_labels["average_score"].configure(
            text=f"{overall_stats.get('average_score', 0):.1f}"
        )
        self.stats_labels["highest_score"].configure(
            text=f"{overall_stats.get('max_score', 0):.1f}"
        )
        self.stats_labels["lowest_score"].configure(
            text=f"{overall_stats.get('min_score', 0):.1f}"
        )
        
        # 等级统计
        distribution = grades_data.get('distribution', [])
        grade_counts = {d['grade']: d['count'] for d in distribution}
        
        for grade in ['A', 'B', 'C', 'D', 'F']:
            self.stats_labels[f"grade_{grade.lower()}"].configure(
                text=str(grade_counts.get(grade, 0))
            )

    def update_assignment_statistics(self, grades):
        """更新作业统计信息"""
        if not grades:
            for key in self.stats_labels:
                self.stats_labels[key].configure(text="0")
            return
        
        total_students = len(grades)
        scores = [g['score'] for g in grades if g['score'] is not None]
        
        if scores:
            average_score = sum(scores) / len(scores)
            highest_score = max(scores)
            lowest_score = min(scores)
        else:
            average_score = highest_score = lowest_score = 0
        
        # 等级统计
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for grade in grades:
            if grade['grade'] in grade_counts:
                grade_counts[grade['grade']] += 1
        
        self.stats_labels["total_students"].configure(text=str(total_students))
        self.stats_labels["average_score"].configure(text=f"{average_score:.1f}")
        self.stats_labels["highest_score"].configure(text=f"{highest_score:.1f}")
        self.stats_labels["lowest_score"].configure(text=f"{lowest_score:.1f}")
        
        for grade, count in grade_counts.items():
            self.stats_labels[f"grade_{grade.lower()}"].configure(text=str(count))

    def update_chart(self, grades_data):
        """更新课程成绩分布图表"""
        # 清除旧图表
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        # 创建新图表
        distribution = grades_data.get('distribution', [])
        if not distribution:
            return
        
        grades = [d['grade'] for d in distribution]
        counts = [d['count'] for d in distribution]
        
        fig = plt.Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']
        ax.bar(grades, counts, color=colors[:len(grades)])
        ax.set_title("成绩等级分布")
        ax.set_xlabel("等级")
        ax.set_ylabel("人数")
        
        # 嵌入到Tkinter
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.master.winfo_children()[0].winfo_children()[3])
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def update_assignment_chart(self, grades):
        """更新作业成绩分布图表"""
        # 清除旧图表
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        # 创建新图表
        scores = [g['score'] for g in grades if g['score'] is not None]
        if not scores:
            return
        
        fig = plt.Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.hist(scores, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title("成绩分数分布")
        ax.set_xlabel("分数")
        ax.set_ylabel("人数")
        
        # 嵌入到Tkinter
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.master.winfo_children()[0].winfo_children()[3])
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def search_students(self, keyword):
        """搜索学生"""
        # 这里可以实现学生搜索功能
        pass

    def import_grades(self):
        """导入成绩"""
        from ui.dialogs import ImportGradesDialog
        if hasattr(self, 'current_assignment_id') and self.current_assignment_id:
            dialog = ImportGradesDialog(self, self.current_assignment_id, self.gradebook_service)
            dialog.grab_set()
            self.wait_window(dialog)
            self.on_assignment_selected(None)
        else:
            MessageDialog.show_warning(self, "提示", "请先选择一个作业")

    def export_grades(self):
        """导出成绩"""
        if hasattr(self, 'current_course_id'):
            try:
                export_data = self.gradebook_service.export_grades(self.current_course_id)
                from ui.dialogs import ExportGradesDialog
                dialog = ExportGradesDialog(self, export_data)
                dialog.grab_set()
            except Exception as e:
                MessageDialog.show_error(self, "错误", f"导出成绩失败: {e}")
        else:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")

    def bulk_edit_grades(self):
        """批量编辑成绩"""
        if hasattr(self, 'current_assignment_id') and self.current_assignment_id:
            from ui.dialogs import BulkEditGradesDialog
            dialog = BulkEditGradesDialog(self, self.current_assignment_id, self.gradebook_service)
            dialog.grab_set()
            self.wait_window(dialog)
            self.on_assignment_selected(None)
        else:
            MessageDialog.show_warning(self, "提示", "请先选择一个作业")

    def view_grade_details(self):
        """查看成绩详情"""
        selected = self.grade_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个学生")
            return
        
        student_id = selected[0]  # 学号
        from ui.dialogs import GradeDetailsDialog
        dialog = GradeDetailsDialog(self, student_id, self.current_course_id, self.gradebook_service)
        dialog.grab_set()

    def edit_grade(self):
        """编辑成绩"""
        selected = self.grade_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个学生")
            return
        
        student_id = selected[0]  # 学号
        from ui.dialogs import EditGradeDialog
        dialog = EditGradeDialog(
            self, 
            student_id, 
            self.current_course_id, 
            self.current_assignment_id,
            self.gradebook_service
        )
        dialog.grab_set()
        self.wait_window(dialog)
        self.on_assignment_selected(None)

    def generate_report(self):
        """生成成绩报告"""
        if hasattr(self, 'current_course_id'):
            from ui.dialogs import GenerateReportDialog
            dialog = GenerateReportDialog(self, self.current_course_id, self.gradebook_service)
            dialog.grab_set()
        else:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")

    def publish_grades(self):
        """发布成绩"""
        if hasattr(self, 'current_assignment_id') and self.current_assignment_id:
            if MessageDialog.ask_yesno(self, "确认发布", "确定要发布成绩吗？学生将能看到自己的成绩。"):
                try:
                    # 这里可以添加发布成绩的逻辑
                    MessageDialog.show_info(self, "成功", "成绩已发布")
                except Exception as e:
                    MessageDialog.show_error(self, "错误", f"发布成绩失败: {e}")
        else:
            MessageDialog.show_warning(self, "提示", "请先选择一个作业")

    def on_grade_double_click(self, event):
        """成绩双击事件"""
        self.view_grade_details()