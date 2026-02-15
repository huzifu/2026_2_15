"""
创建课程对话框
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

class CreateCourseDialog(tk.Toplevel):
    def __init__(self, parent, user, course_service, class_service):
        super().__init__(parent)
        self.title("创建课程")
        self.geometry("600x500")
        self.user = user
        self.course_service = course_service
        self.class_service = class_service
        
        self.create_widgets()
        
        # 居中显示
        self.transient(parent)
        self.grab_set()
        self.center_window()
        
        # 加载班级列表
        self.load_classes()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_classes(self):
        """加载班级列表"""
        try:
            classes = self.class_service.get_classes_by_teacher(self.user.id)
            class_options = ["不关联班级"]
            self.class_map = {0: None}
            
            for cls in classes:
                if cls.status == 'active':
                    class_options.append(f"{cls.id}: {cls.name}")
                    self.class_map[cls.id] = cls
            
            self.class_combo['values'] = class_options
            self.class_combo.current(0)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载班级列表失败: {e}")

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="创建新课程",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 20))
        
        # 表单容器
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=BOTH, expand=True)
        
        # 课程标题
        title_frame = ttk.Frame(form_frame)
        title_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            title_frame,
            text="课程标题:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(
            title_frame,
            textvariable=self.title_var,
            font=("Helvetica", 11)
        )
        self.title_entry.pack(fill=X)
        
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
        
        # 课程描述
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            desc_frame,
            text="课程描述:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.desc_text = tk.Text(
            desc_frame,
            height=6,
            font=("Helvetica", 11)
        )
        self.desc_text.pack(fill=X)
        
        # 封面图片
        cover_frame = ttk.Frame(form_frame)
        cover_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            cover_frame,
            text="封面图片:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        cover_input_frame = ttk.Frame(cover_frame)
        cover_input_frame.pack(fill=X)
        
        self.cover_var = tk.StringVar()
        self.cover_entry = ttk.Entry(
            cover_input_frame,
            textvariable=self.cover_var,
            font=("Helvetica", 11)
        )
        self.cover_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            cover_input_frame,
            text="浏览",
            command=self.browse_cover_image,
            bootstyle="outline",
            width=8
        )
        browse_btn.pack(side=RIGHT)
        
        ttk.Label(
            cover_frame,
            text="支持 JPG、PNG 格式（可选）",
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
            command=self.create_course,
            bootstyle="primary",
            width=10
        )
        create_btn.pack(side=RIGHT)
        
        # 设置焦点
        self.title_entry.focus_set()

    def browse_cover_image(self):
        """浏览封面图片"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择封面图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            self.cover_var.set(file_path)

    def create_course(self):
        """创建课程"""
        title = self.title_var.get().strip()
        description = self.desc_text.get("1.0", END).strip()
        cover_image = self.cover_var.get().strip()
        
        # 获取班级ID
        class_text = self.class_var.get()
        class_id = None
        if class_text and class_text != "不关联班级":
            try:
                class_id = int(class_text.split(":")[0])
            except:
                pass
        
        # 验证输入
        if not title:
            MessageDialog.show_warning(self, "提示", "请输入课程标题")
            self.title_entry.focus_set()
            return
        
        try:
            # 创建课程
            course_id = self.course_service.create_course(
                title=title,
                description=description,
                teacher_id=self.user.id,
                class_id=class_id,
                cover_image=cover_image if cover_image else None
            )
            
            if course_id:
                MessageDialog.show_info(self, "成功", "课程创建成功！")
                self.destroy()
            else:
                MessageDialog.show_error(self, "错误", "创建课程失败")
                
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"创建课程失败: {e}")