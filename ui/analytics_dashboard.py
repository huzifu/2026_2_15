"""
数据分析仪表板
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
from ui.components import MessageDialog

# Windows 中文字体修复
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class AnalyticsDashboardFrame(ttk.Frame):
    def __init__(self, parent, user, analytics_service, class_service, 
                 course_service, gradebook_service):
        super().__init__(parent)
        self.user = user
        self.analytics_service = analytics_service
        self.class_service = class_service
        self.course_service = course_service
        self.gradebook_service = gradebook_service
        
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        self.load_analytics()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_container,
            text="数据分析",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 统计卡片区域
        stats_frame = ttk.Frame(main_container)
        stats_frame.pack(fill=X, pady=(0, 20))
        
        # 创建统计卡片
        from ui.components import StatCard
        
        self.stat_cards = {}
        stats_data = [
            ("total_students", "学生总数", "0", "👨‍🎓", "primary"),
            ("total_courses", "课程总数", "0", "📚", "success"),
            ("total_assignments", "作业总数", "0", "📝", "info"),
            ("average_score", "平均成绩", "0", "📊", "warning")
        ]
        
        for i, (key, title, value, icon, color) in enumerate(stats_data):
            card = StatCard(stats_frame, title=title, value=value, icon=icon, color=color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.stat_cards[key] = card
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # 图表区域
        charts_frame = ttk.Frame(main_container)
        charts_frame.pack(fill=BOTH, expand=True)
        
        # 左侧图表
        left_chart_frame = ttk.LabelFrame(charts_frame, text="成绩分布", padding=10)
        left_chart_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        self.left_chart_canvas = None
        
        # 右侧图表
        right_chart_frame = ttk.LabelFrame(charts_frame, text="作业完成率", padding=10)
        right_chart_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        self.right_chart_canvas = None

    def load_analytics(self):
        """加载分析数据"""
        try:
            # 获取统计数据
            classes = self.class_service.get_classes_by_teacher(self.user.id)
            courses = self.course_service.get_courses_by_teacher(self.user.id)
            
            total_students = 0
            for cls in classes:
                students = self.class_service.get_class_students(cls.id)
                total_students += len(students)
            
            total_courses = len(courses)
            
            # 获取作业统计
            total_assignments = 0
            all_scores = []
            
            for course in courses:
                from modules.assignment_service import AssignmentService
                assignments = self.analytics_service.db.execute_query(
                    "SELECT * FROM assignment WHERE course_id = ?", (course.id,)
                )
                total_assignments += len(assignments)
                
                # 获取成绩
                for assignment in assignments:
                    scores = self.analytics_service.db.execute_query(
                        "SELECT total_score FROM submission WHERE assignment_id = ? AND total_score IS NOT NULL",
                        (assignment['id'],)
                    )
                    all_scores.extend([s['total_score'] for s in scores])
            
            # 计算平均成绩
            average_score = sum(all_scores) / len(all_scores) if all_scores else 0
            
            # 更新统计卡片
            self.update_stat_card("total_students", total_students)
            self.update_stat_card("total_courses", total_courses)
            self.update_stat_card("total_assignments", total_assignments)
            self.update_stat_card("average_score", f"{average_score:.1f}")
            
            # 绘制图表
            self.draw_grade_distribution(all_scores)
            self.draw_completion_rate()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载分析数据失败: {e}")

    def update_stat_card(self, key, value):
        """更新统计卡片"""
        if key in self.stat_cards:
            # 找到卡片中的值标签并更新
            for widget in self.stat_cards[key].winfo_children():
                if isinstance(widget, ttk.Label) and widget.cget("font")[1] == 24:
                    widget.configure(text=str(value))
                    break

    def draw_grade_distribution(self, scores):
        """绘制成绩分布图"""
        if not scores:
            return
        
        # 清除旧图表
        if self.left_chart_canvas:
            self.left_chart_canvas.get_tk_widget().destroy()
        
        # 创建新图表
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.hist(scores, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title("成绩分布")
        ax.set_xlabel("分数")
        ax.set_ylabel("人数")
        
        # 嵌入到Tkinter
        parent_frame = self.winfo_children()[0].winfo_children()[2].winfo_children()[0]
        self.left_chart_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        self.left_chart_canvas.draw()
        self.left_chart_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def draw_completion_rate(self):
        """绘制作业完成率图"""
        # 清除旧图表
        if self.right_chart_canvas:
            self.right_chart_canvas.get_tk_widget().destroy()
        
        # 创建新图表
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # 示例数据
        labels = ['已完成', '进行中', '未开始']
        sizes = [60, 25, 15]
        colors = ['#4CAF50', '#FFC107', '#F44336']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title("作业完成率")
        
        # 嵌入到Tkinter
        parent_frame = self.winfo_children()[0].winfo_children()[2].winfo_children()[1]
        self.right_chart_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        self.right_chart_canvas.draw()
        self.right_chart_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
