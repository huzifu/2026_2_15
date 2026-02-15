"""
创建帖子对话框
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

class CreatePostDialog(tk.Toplevel):
    def __init__(self, parent, user, course_id, discussion_service):
        super().__init__(parent)
        self.title("新建帖子")
        self.geometry("600x500")
        self.user = user
        self.course_id = course_id
        self.discussion_service = discussion_service
        
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
            text="新建讨论帖子",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 20))
        
        # 表单容器
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=BOTH, expand=True)
        
        # 帖子标题
        post_title_frame = ttk.Frame(form_frame)
        post_title_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            post_title_frame,
            text="帖子标题:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.post_title_var = tk.StringVar()
        self.post_title_entry = ttk.Entry(
            post_title_frame,
            textvariable=self.post_title_var,
            font=("Helvetica", 11)
        )
        self.post_title_entry.pack(fill=X)
        
        # 帖子内容
        content_frame = ttk.Frame(form_frame)
        content_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(
            content_frame,
            text="帖子内容:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        # 创建滚动文本框
        text_container = ttk.Frame(content_frame)
        text_container.pack(fill=BOTH, expand=True)
        
        # 添加滚动条
        text_scrollbar = ttk.Scrollbar(text_container)
        text_scrollbar.pack(side=RIGHT, fill=Y)
        
        self.content_text = tk.Text(
            text_container,
            height=10,
            font=("Helvetica", 11),
            wrap=WORD,
            yscrollcommand=text_scrollbar.set
        )
        self.content_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        text_scrollbar.config(command=self.content_text.yview)
        
        # 帖子类型
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            type_frame,
            text="帖子类型:",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        self.type_var = tk.StringVar(value="question")
        type_frame_inner = ttk.Frame(type_frame)
        type_frame_inner.pack(fill=X)
        
        # 问题类型
        question_radio = ttk.Radiobutton(
            type_frame_inner,
            text="问题求助",
            variable=self.type_var,
            value="question",
            bootstyle="primary-toolbutton"
        )
        question_radio.pack(side=LEFT, padx=(0, 10))
        
        # 讨论类型
        discussion_radio = ttk.Radiobutton(
            type_frame_inner,
            text="学习讨论",
            variable=self.type_var,
            value="discussion",
            bootstyle="primary-toolbutton"
        )
        discussion_radio.pack(side=LEFT, padx=(0, 10))
        
        # 分享类型
        share_radio = ttk.Radiobutton(
            type_frame_inner,
            text="资源分享",
            variable=self.type_var,
            value="share",
            bootstyle="primary-toolbutton"
        )
        share_radio.pack(side=LEFT)
        
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
        
        # 发布按钮
        post_btn = ttk.Button(
            button_frame,
            text="发布",
            command=self.create_post,
            bootstyle="primary",
            width=10
        )
        post_btn.pack(side=RIGHT)
        
        # 设置焦点
        self.post_title_entry.focus_set()

    def create_post(self):
        """创建帖子"""
        title = self.post_title_var.get().strip()
        content = self.content_text.get("1.0", END).strip()
        post_type = self.type_var.get()
        
        # 根据类型添加前缀
        type_prefixes = {
            "question": "[问题] ",
            "discussion": "[讨论] ",
            "share": "[分享] "
        }
        
        if post_type in type_prefixes:
            title = type_prefixes[post_type] + title
        
        # 验证输入
        if not title:
            MessageDialog.show_warning(self, "提示", "请输入帖子标题")
            self.post_title_entry.focus_set()
            return
        
        if not content:
            MessageDialog.show_warning(self, "提示", "请输入帖子内容")
            self.content_text.focus_set()
            return
        
        if len(content) < 10:
            MessageDialog.show_warning(self, "提示", "帖子内容至少需要10个字符")
            self.content_text.focus_set()
            return
        
        try:
            # 创建帖子
            post_id = self.discussion_service.create_post(
                user_id=self.user.id,
                content=content,
                title=title,
                course_id=self.course_id
            )
            
            if post_id:
                MessageDialog.show_info(self, "成功", "帖子发布成功！")
                self.destroy()
            else:
                MessageDialog.show_error(self, "错误", "发布帖子失败")
                
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"发布帖子失败: {e}")