import tkinter as tk
from tkinter import ttk
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from ui.student_frames import StudentAssignmentListFrame, SubmissionHistoryFrame

class StudentDashboard(ttk.Frame):
    def __init__(self, parent, user, db_manager, logout_callback):
        super().__init__(parent)
        self.user = user
        self.db = db_manager
        self.logout_callback = logout_callback
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ttk.Frame(self, padding=10)
        header.pack(fill=X)
        
        ttk.Label(header, text=f"学生端 - {self.user.nickname}", font=("Helvetica", 16, "bold")).pack(side=LEFT)
        ttk.Button(header, text="注销", command=self.logout_callback, bootstyle="danger-outline").pack(side=RIGHT)

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.assignment_tab = StudentAssignmentListFrame(self.notebook, self.user, self.db)
        self.history_tab = SubmissionHistoryFrame(self.notebook, self.user, self.db)

        self.notebook.add(self.assignment_tab, text="我的作业")
        self.notebook.add(self.history_tab, text="历史提交")
