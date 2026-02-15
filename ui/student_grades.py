"""
学生成绩界面
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

class StudentGradesFrame(ttk.Frame):
    def __init__(self, parent, user, gradebook_service, course_service):
        super().__init__(parent)
        self.user = user
        self.gradebook_service = gradebook_service
        self.course_service = course_service
        
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
            text="我的成绩",
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
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            course_frame,
            text="🔄 刷新",
            command=self.load_courses,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 成绩显示区域
        display_frame = ttk.Frame(main_container)
        display_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 左侧：成绩表格
        left_frame = ttk.Frame(display_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 成绩表格
        columns = [
            {"id": "assignment", "text": "作业", "width": 250},
            {"id": "type", "text": "类型", "width": 100},
            {"id": "score", "text": "成绩", "width": 80},
            {"id": "grade", "text": "等级", "width": 80},
            {"id": "weight", "text": "权重", "width": 80},
            {"id": "comment", "text": "评语", "width": 200}
        ]
        
        self.grade_table = DataTable(
            left_frame,
            columns=columns,
            height=12,
            selectmode="browse"
        )
        self.grade_table.pack(fill=BOTH, expand=True)
        
        # 右侧：统计图表
        right_frame = ttk.Frame(display_frame, width=400)
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))
        
        # 总体统计
        overall_frame = ttk.LabelFrame(right_frame, text="总体统计", padding=10)
        overall_frame.pack(fill=X, pady=(0, 10))
        
        self.overall_labels = {}
        overall_data = [
            ("final_score", "最终成绩", "0"),
            ("final_grade", "最终等级", "-"),
            ("average_score", "平均分", "0"),
            ("assignment_count", "作业数", "0")
        ]
        
        for i, (key, label, value) in enumerate(overall_data):
            row = i // 2
            col = i % 2
            
            if col == 0:
                overall_row_frame = ttk.Frame(overall_frame)
                overall_row_frame.pack(fill=X, pady=2)
            
            stat_frame = ttk.Frame(overall_row_frame)
            stat_frame.pack(side=LEFT, padx=5, fill=X, expand=True)
            
            ttk.Label(
                stat_frame,
                text=label,
                font=("Helvetica", 9)
            ).pack(anchor=W)
            
            self.overall_labels[key] = ttk.Label(
                stat_frame,
                text=value,
                font=("Helvetica", 11, "bold")
            )
            self.overall_labels[key].pack(anchor=W)
        
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
        
        # 导出成绩按钮
        export_btn = ttk.Button(
            action_frame,
            text="📤 导出成绩单",
            command=self.export_report_card,
            bootstyle="outline"
        )
        export_btn.pack(side=LEFT, padx=(0, 5))
        
        # 成绩分析按钮
        analyze_btn = ttk.Button(
            action_frame,
            text="📈 成绩分析",
            command=self.analyze_grades,
            bootstyle="outline"
        )
        analyze_btn.pack(side=LEFT, padx=(0, 5))

    def load_courses(self):
        """加载课程列表"""
        try:
            courses = self.course_service.get_available_courses(self.user.id)
            enrolled_courses = [c for c in courses if c.get('student_progress')]
            
            course_options = []
            self.course_map = {}
            
            for course in enrolled_courses:
                course_options.append(f"{course['id']}: {course['title']}")
                self.course_map[course['id']] = course
            
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
            self.load_grades(course_id)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载成绩失败: {e}")

    def load_grades(self, course_id):
        """加载成绩"""
        try:
            # 获取成绩数据
            grades = self.gradebook_service.get_student_grades(self.user.id, course_id)
            
            table_data = []
            for grade in grades:
                table_data.append([
                    grade.get('assignment_title', '课程总评'),
                    grade.get('assignment_type', '总评'),
                    f"{grade['score']:.1f}" if grade['score'] is not None else '未评分',
                    grade['grade'] or '未评级',
                    grade.get('weight', 1.0),
                    grade.get('comment', '')
                ])
            
            self.grade_table.update_data(table_data)
            
            # 计算最终成绩
            final_grade = self.gradebook_service.calculate_final_grade(self.user.id, course_id)
            
            # 更新总体统计
            self.overall_labels["final_score"].configure(
                text=f"{final_grade['final_score']:.1f}" if final_grade['final_score'] else "未评分"
            )
            self.overall_labels["final_grade"].configure(
                text=final_grade['final_grade'] or "-"
            )
            
            # 计算平均分
            if grades:
                scores = [g['score'] for g in grades if g['score'] is not None]
                if scores:
                    average_score = sum(scores) / len(scores)
                    self.overall_labels["average_score"].configure(text=f"{average_score:.1f}")
                else:
                    self.overall_labels["average_score"].configure(text="0")
                
                self.overall_labels["assignment_count"].configure(text=str(len(grades)))
            else:
                self.overall_labels["average_score"].configure(text="0")
                self.overall_labels["assignment_count"].configure(text="0")
            
            # 更新图表
            self.update_chart(grades)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载成绩失败: {e}")

    def update_chart(self, grades):
        """更新成绩分布图表"""
        # 清除旧图表
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        if not grades:
            # 显示空状态
            empty_label = ttk.Label(
                self.master.winfo_children()[0].winfo_children()[3],
                text="暂无成绩数据",
                font=("Helvetica", 12)
            )
            empty_label.pack(expand=True)
            return
        
        # 提取成绩数据
        scores = [g['score'] for g in grades if g['score'] is not None]
        if not scores:
            # 显示空状态
            empty_label = ttk.Label(
                self.master.winfo_children()[0].winfo_children()[3],
                text="暂无成绩数据",
                font=("Helvetica", 12)
            )
            empty_label.pack(expand=True)
            return
        
        # 创建新图表
        fig = plt.Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # 成绩分布直方图
        ax.hist(scores, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title("成绩分布")
        ax.set_xlabel("分数")
        ax.set_ylabel("作业数")
        
        # 添加平均线
        avg_score = sum(scores) / len(scores)
        ax.axvline(avg_score, color='red', linestyle='--', linewidth=2, label=f'平均分: {avg_score:.1f}')
        ax.legend()
        
        # 嵌入到Tkinter
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.master.winfo_children()[0].winfo_children()[3])
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def view_grade_details(self):
        """查看成绩详情"""
        selected = self.grade_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个成绩记录")
            return
        
        assignment_name = selected[0]
        from ui.dialogs import GradeDetailsDialog
        dialog = GradeDetailsDialog(self, self.user.id, self.current_course_id, self.gradebook_service)
        dialog.grab_set()

    def export_report_card(self):
        """导出成绩单"""
        if hasattr(self, 'current_course_id'):
            try:
                report_card = self.gradebook_service.generate_report_card(self.user.id, self.current_course_id)
                from ui.dialogs import ExportReportCardDialog
                dialog = ExportReportCardDialog(self, report_card)
                dialog.grab_set()
            except Exception as e:
                MessageDialog.show_error(self, "错误", f"导出成绩单失败: {e}")
        else:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")

    def analyze_grades(self):
        """成绩分析"""
        if hasattr(self, 'current_course_id'):
            from ui.dialogs import GradeAnalysisDialog
            dialog = GradeAnalysisDialog(self, self.user.id, self.current_course_id, self.gradebook_service)
            dialog.grab_set()
        else:
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")