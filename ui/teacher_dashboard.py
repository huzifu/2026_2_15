import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from ui.assignment_frames import AssignmentManagerFrame
from ui.analytics_frame import AnalyticsFrame

class TeacherDashboard(ttk.Frame):
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
        
        ttk.Label(header, text=f"教师端 - {self.user.nickname}", font=("Helvetica", 16, "bold")).pack(side=LEFT)
        ttk.Button(header, text="注销", command=self.logout_callback).pack(side=RIGHT)

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.assignment_tab = AssignmentManagerFrame(self.notebook, self.user, self.db)
        self.analytics_tab = AnalyticsFrame(self.notebook, self.user, self.db)

        self.notebook.add(self.assignment_tab, text="作业管理")
        self.notebook.add(self.analytics_tab, text="学情分析")
