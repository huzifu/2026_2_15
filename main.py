import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
# 尝试导入 ttkbootstrap，如果不存在则回退到标准 tkinter
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from config import WINDOW_TITLE, WINDOW_SIZE, THEME_NAME
from modules.db_manager import DBManager
from modules.auth import AuthManager

class App(ttk.Window if 'ttkbootstrap' in globals() else tk.Tk):
    def __init__(self):
        if 'ttkbootstrap' in globals():
            super().__init__(themename=THEME_NAME)
        else:
            super().__init__()
            
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        
        # 初始化数据库和认证管理
        self.db = DBManager()
        self.auth_manager = AuthManager(self.db)
        
        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        from ui.login_frame import LoginFrame
        self.current_frame = LoginFrame(self, self.auth_manager, self.on_login_success)

    def on_login_success(self, user):
        if self.current_frame:
            self.current_frame.destroy()
            
        if user.role == 'teacher':
            self.show_teacher_dashboard()
        elif user.role == 'student':
            self.show_student_dashboard()
        elif user.role == 'admin':
            # Admin can see teacher dashboard for simplicity or a separate one
            self.show_teacher_dashboard() 

    def show_teacher_dashboard(self):
        from ui.teacher_dashboard import TeacherDashboard
        self.current_frame = TeacherDashboard(self, self.auth_manager.current_user, self.db, self.logout)

    def show_student_dashboard(self):
        from ui.student_dashboard import StudentDashboard
        self.current_frame = StudentDashboard(self, self.auth_manager.current_user, self.db, self.logout)

    def logout(self):
        self.auth_manager.logout()
        self.show_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()
