import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

class LoginFrame(ttk.Frame):
    def __init__(self, parent, auth_manager, on_login_success):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Container for centering content
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Title
        title_label = ttk.Label(container, text="AI 智能教学助手", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)

        # Tabs for Login / Register
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(pady=10, expand=True, fill=BOTH)

        self.login_tab = ttk.Frame(self.notebook, padding=20)
        self.register_tab = ttk.Frame(self.notebook, padding=20)

        self.notebook.add(self.login_tab, text="登录")
        self.notebook.add(self.register_tab, text="注册")

        self.create_login_widgets(self.login_tab)
        self.create_register_widgets(self.register_tab)

    def create_login_widgets(self, parent):
        ttk.Label(parent, text="用户名:").pack(fill=X, pady=5)
        self.username_entry = ttk.Entry(parent)
        self.username_entry.pack(fill=X, pady=5)

        ttk.Label(parent, text="密码:").pack(fill=X, pady=5)
        self.password_entry = ttk.Entry(parent, show="*")
        self.password_entry.pack(fill=X, pady=5)

        ttk.Button(parent, text="登录", command=self.login, bootstyle="primary").pack(fill=X, pady=20)

    def create_register_widgets(self, parent):
        ttk.Label(parent, text="用户名:").pack(fill=X, pady=5)
        self.reg_username_entry = ttk.Entry(parent)
        self.reg_username_entry.pack(fill=X, pady=5)

        ttk.Label(parent, text="密码:").pack(fill=X, pady=5)
        self.reg_password_entry = ttk.Entry(parent, show="*")
        self.reg_password_entry.pack(fill=X, pady=5)
        
        ttk.Label(parent, text="昵称:").pack(fill=X, pady=5)
        self.reg_nickname_entry = ttk.Entry(parent)
        self.reg_nickname_entry.pack(fill=X, pady=5)

        ttk.Label(parent, text="角色:").pack(fill=X, pady=5)
        self.role_var = tk.StringVar(value="student")
        ttk.Radiobutton(parent, text="学生", variable=self.role_var, value="student").pack(fill=X)
        ttk.Radiobutton(parent, text="教师", variable=self.role_var, value="teacher").pack(fill=X)

        ttk.Button(parent, text="注册", command=self.register, bootstyle="success").pack(fill=X, pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        success, msg = self.auth_manager.login(username, password)
        if success:
            # messagebox.showinfo("成功", f"欢迎回来, {self.auth_manager.current_user.nickname}")
            self.on_login_success(self.auth_manager.current_user)
        else:
            messagebox.showerror("错误", msg)

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        nickname = self.reg_nickname_entry.get()
        role = self.role_var.get()
        
        if not all([username, password, nickname, role]):
            messagebox.showwarning("提示", "请填写所有字段")
            return

        success, msg = self.auth_manager.register(username, password, role, nickname)
        if success:
            messagebox.showinfo("成功", "注册成功，请切换到登录页登录")
            self.notebook.select(0) # Store to login tab
        else:
            messagebox.showerror("错误", msg)
