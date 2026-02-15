import tkinter as tk
from tkinter import ttk
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Windows font fix
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False 

class AnalyticsFrame(ttk.Frame):
    def __init__(self, parent, user, db_manager):
        super().__init__(parent)
        self.user = user
        self.db = db_manager
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()
        
    def create_widgets(self):
        # Control Panel
        controls = ttk.Frame(self, padding=10)
        controls.pack(fill=X)
        
        ttk.Label(controls, text="选择作业:").pack(side=LEFT)
        self.assignment_combo = ttk.Combobox(controls, state="readonly", width=30)
        self.assignment_combo.pack(side=LEFT, padx=5)
        self.assignment_combo.bind("<<ComboboxSelected>>", self.on_select_assignment)
        
        ttk.Button(controls, text="刷新作业列表", command=self.load_assignments).pack(side=LEFT, padx=5)

        # Plot Area
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.load_assignments()

    def load_assignments(self):
        query = "SELECT id, title FROM assignment WHERE teacher_id = ?"
        rows = self.db.execute_query(query, (self.user.id,))
        self.assignments = {row['title']: row['id'] for row in rows}
        self.assignment_combo['values'] = list(self.assignments.keys())
        if self.assignments:
            self.assignment_combo.current(0)
            self.on_select_assignment(None)

    def on_select_assignment(self, event):
        title = self.assignment_combo.get()
        if not title:
            return
            
        assignment_id = self.assignments[title]
        self.plot_scores(assignment_id, title)

    def plot_scores(self, assignment_id, title):
        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        # Get scores
        query = "SELECT total_score FROM submission WHERE assignment_id = ?"
        rows = self.db.execute_query(query, (assignment_id,))
        scores = [row['total_score'] for row in rows]
        
        if not scores:
            ttk.Label(self.plot_frame, text="暂无提交记录").pack(pady=20)
            return

        # Create plot
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Hist
        ax.hist(scores, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title(f"'{title}' 成绩分布")
        ax.set_xlabel("分数")
        ax.set_ylabel("人数")
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
