"""
创建班级对话框
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from ui.components import MessageDialog

class CreateClassDialog(tk.Toplevel):
    def __init__(self, parent, user, class_service):
        super().__init__(parent)
        self.title("创建班级")
        self.geometry("500x400")
        self.user = user
        self.class_service = class_service
        
        self.create_widgets()
        
        # 居中显示
        self.transient(parent)
        self.grab_set()
        self.center_window()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="创建新班级",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 20))
        
        # 表单容器
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=BOTH, expand=True)
        
        # 班级名称
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            name_frame,
            text="班级名称:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(
            name_frame,
            textvariable=self.name_var,
            font=("Helvetica", 11)
        )
        self.name_entry.pack(fill=X)
        
        # 班级代码
        code_frame = ttk.Frame(form_frame)
        code_frame.pack(fill=X, pady=(0, 15))
        
        code_label_frame = ttk.Frame(code_frame)
        code_label_frame.pack(fill=X, pady=(0, 5))
        
        ttk.Label(
            code_label_frame,
            text="班级代码:",
            font=("Helvetica", 11)
        ).pack(side=LEFT)
        
        # 生成代码按钮
        generate_btn = ttk.Button(
            code_label_frame,
            text="生成代码",
            command=self.generate_code,
            bootstyle="outline",
            padding=(10, 0)
        )
        generate_btn.pack(side=RIGHT)
        
        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(
            code_frame,
            textvariable=self.code_var,
            font=("Helvetica", 11)
        )
        self.code_entry.pack(fill=X)
        ttk.Label(
            code_frame,
            text="学生使用此代码加入班级",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor=W, pady=(2, 0))
        
        # 班级描述
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            desc_frame,
            text="班级描述:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.desc_text = tk.Text(
            desc_frame,
            height=4,
            font=("Helvetica", 11)
        )
        self.desc_text.pack(fill=X)
        
        # 人数限制
        limit_frame = ttk.Frame(form_frame)
        limit_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            limit_frame,
            text="人数限制:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.limit_var = tk.IntVar(value=50)
        limit_spinbox = ttk.Spinbox(
            limit_frame,
            from_=1,
            to=200,
            textvariable=self.limit_var,
            font=("Helvetica", 11),
            width=10
        )
        limit_spinbox.pack(anchor=W)
        ttk.Label(
            limit_frame,
            text="(1-200人)",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor=W, pady=(2, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=(20, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame,
            text="取消",
            command=self.destroy,
            bootstyle="outline",
            width=10
        )
        cancel_btn.pack(side=RIGHT, padx=(10, 0))
        
        # 创建按钮
        create_btn = ttk.Button(
            button_frame,
            text="创建",
            command=self.create_class,
            bootstyle="primary",
            width=10
        )
        create_btn.pack(side=RIGHT)
        
        # 设置焦点
        self.name_entry.focus_set()

    def generate_code(self):
        """生成班级代码"""
        try:
            code = self.class_service.generate_class_code()
            self.code_var.set(code)
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"生成代码失败: {e}")

    def create_class(self):
        """创建班级"""
        name = self.name_var.get().strip()
        code = self.code_var.get().strip()
        description = self.desc_text.get("1.0", END).strip()
        max_students = self.limit_var.get()
        
        # 验证输入
        if not name:
            MessageDialog.show_warning(self, "提示", "请输入班级名称")
            self.name_entry.focus_set()
            return
        
        if not code:
            MessageDialog.show_warning(self, "提示", "请输入班级代码")
            self.code_entry.focus_set()
            return
        
        try:
            # 创建班级
            class_id = self.class_service.create_class(
                name=name,
                description=description,
                teacher_id=self.user.id,
                max_students=max_students,
                code=code
            )
            
            if class_id:
                MessageDialog.show_info(self, "成功", f"班级创建成功！\n班级代码: {code}")
                self.destroy()
            else:
                MessageDialog.show_error(self, "错误", "创建班级失败")
                
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"创建班级失败: {e}")