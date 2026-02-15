"""
创建作业对话框
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from datetime import datetime
from ui.components import MessageDialog

class CreateAssignmentDialog(tk.Toplevel):
    def __init__(self, parent, user, assignment_service, course_service, class_service):
        super().__init__(parent)
        self.title("创建作业")
        self.geometry("600x550")
        self.user = user
        self.assignment_service = assignment_service
        self.course_service = course_service
        self.class_service = class_service
        
        self.create_widgets()
        
        # 居中显示
        self.transient(parent)
        self.grab_set()
        self.center_window()
        
        # 加载课程列表
        self.load_courses()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

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
            MessageDialog.show_error(self, "错误", f"加载课程列表失败: {e}")

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="创建新作业",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 20))
        
        # 表单容器
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=BOTH, expand=True)
        
        # 作业标题
        title_frame = ttk.Frame(form_frame)
        title_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            title_frame,
            text="作业标题:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(
            title_frame,
            textvariable=self.title_var,
            font=("Helvetica", 11)
        )
        self.title_entry.pack(fill=X)
        
        # 关联课程
        course_frame = ttk.Frame(form_frame)
        course_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            course_frame,
            text="关联课程:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(
            course_frame,
            textvariable=self.course_var,
            state="readonly",
            font=("Helvetica", 11)
        )
        self.course_combo.pack(fill=X)
        self.course_combo.bind("<<ComboboxSelected>>", self.on_course_selected)
        
        # 关联班级
        class_frame = ttk.Frame(form_frame)
        class_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            class_frame,
            text="关联班级:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(
            class_frame,
            textvariable=self.class_var,
            state="readonly",
            font=("Helvetica", 11)
        )
        self.class_combo.pack(fill=X)
        ttk.Label(
            class_frame,
            text="选择关联班级（可选）",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor=W, pady=(2, 0))
        
        # 作业描述
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            desc_frame,
            text="作业描述:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.desc_text = tk.Text(
            desc_frame,
            height=4,
            font=("Helvetica", 11)
        )
        self.desc_text.pack(fill=X)
        
        # 截止时间
        deadline_frame = ttk.Frame(form_frame)
        deadline_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            deadline_frame,
            text="截止时间:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        deadline_input_frame = ttk.Frame(deadline_frame)
        deadline_input_frame.pack(fill=X)
        
        # 日期选择
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(
            deadline_input_frame,
            textvariable=self.date_var,
            font=("Helvetica", 11),
            width=12
        )
        date_entry.pack(side=LEFT, padx=(0, 5))
        ttk.Label(
            deadline_input_frame,
            text="YYYY-MM-DD",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(side=LEFT, padx=(0, 10))
        
        # 时间选择
        self.time_var = tk.StringVar(value="23:59")
        time_entry = ttk.Entry(
            deadline_input_frame,
            textvariable=self.time_var,
            font=("Helvetica", 11),
            width=8
        )
        time_entry.pack(side=LEFT, padx=(0, 5))
        ttk.Label(
            deadline_input_frame,
            text="HH:MM",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(side=LEFT)
        
        # 总分
        total_frame = ttk.Frame(form_frame)
        total_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            total_frame,
            text="总分:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.total_var = tk.IntVar(value=100)
        total_spinbox = ttk.Spinbox(
            total_frame,
            from_=1,
            to=1000,
            textvariable=self.total_var,
            font=("Helvetica", 11),
            width=10
        )
        total_spinbox.pack(anchor=W)
        
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
            command=self.create_assignment,
            bootstyle="primary",
            width=10
        )
        create_btn.pack(side=RIGHT)
        
        # 设置焦点
        self.title_entry.focus_set()

    def on_course_selected(self, event):
        """课程选择事件"""
        course_text = self.course_var.get()
        if not course_text:
            return
        
        try:
            course_id = int(course_text.split(":")[0])
            course = self.course_map.get(course_id)
            
            if course and course.class_id:
                # 加载关联班级
                class_info = self.class_service.get_class_by_id(course.class_id)
                if class_info:
                    self.class_var.set(f"{class_info.id}: {class_info.name}")
                else:
                    self.class_var.set("")
            else:
                self.class_var.set("")
                
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载班级信息失败: {e}")

    def create_assignment(self):
        """创建作业"""
        title = self.title_var.get().strip()
        description = self.desc_text.get("1.0", END).strip()
        total_score = self.total_var.get()
        
        # 获取课程ID
        course_text = self.course_var.get()
        if not course_text:
            MessageDialog.show_warning(self, "提示", "请选择关联课程")
            self.course_combo.focus_set()
            return
        
        try:
            course_id = int(course_text.split(":")[0])
        except:
            MessageDialog.show_warning(self, "提示", "无效的课程选择")
            self.course_combo.focus_set()
            return
        
        # 获取班级ID
        class_text = self.class_var.get()
        class_id = None
        if class_text:
            try:
                class_id = int(class_text.split(":")[0])
            except:
                pass
        
        # 处理截止时间
        deadline = None
        date_str = self.date_var.get().strip()
        time_str = self.time_var.get().strip()
        
        if date_str and time_str:
            try:
                deadline = f"{date_str} {time_str}:00"
                # 验证日期时间格式
                datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                MessageDialog.show_warning(self, "提示", "截止时间格式错误，请使用 YYYY-MM-DD HH:MM 格式")
                return
        
        # 验证输入
        if not title:
            MessageDialog.show_warning(self, "提示", "请输入作业标题")
            self.title_entry.focus_set()
            return
        
        try:
            # 创建作业
            assignment_id = self.assignment_service.create_assignment(
                title=title,
                description=description,
                course_id=course_id,
                class_id=class_id,
                teacher_id=self.user.id,
                total_score=total_score,
                deadline=deadline
            )
            
            if assignment_id:
                MessageDialog.show_info(self, "成功", "作业创建成功！")
                self.destroy()
            else:
                MessageDialog.show_error(self, "错误", "创建作业失败")
                
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"创建作业失败: {e}")