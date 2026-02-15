"""
回复帖子对话框
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

class ReplyPostDialog(tk.Toplevel):
    def __init__(self, parent, user, post_id, discussion_service):
        super().__init__(parent)
        self.title("回复帖子")
        self.geometry("500x400")
        self.user = user
        self.post_id = post_id
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
            text="回复帖子",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 20))
        
        # 获取帖子信息
        try:
            post_info = self.discussion_service.get_post_by_id(self.post_id)
            if post_info:
                # 显示原帖信息
                original_frame = ttk.LabelFrame(main_frame, text="原帖", padding=10)
                original_frame.pack(fill=X, pady=(0, 15))
                
                # 原帖标题
                ttk.Label(
                    original_frame,
                    text=f"标题: {post_info['title']}",
                    font=("Helvetica", 11, "bold"),
                    wraplength=450
                ).pack(anchor=W, pady=(0, 5))
                
                # 原帖作者
                ttk.Label(
                    original_frame,
                    text=f"作者: {post_info['author_name']}",
                    font=("Helvetica", 10)
                ).pack(anchor=W, pady=(0, 5))
                
                # 原帖内容（预览）
                content_preview = post_info['content']
                if len(content_preview) > 100:
                    content_preview = content_preview[:100] + "..."
                
                ttk.Label(
                    original_frame,
                    text=f"内容: {content_preview}",
                    font=("Helvetica", 10),
                    wraplength=450
                ).pack(anchor=W)
        except Exception as e:
            print(f"获取帖子信息失败: {e}")
        
        # 回复内容
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(
            content_frame,
            text="回复内容:",
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
            height=8,
            font=("Helvetica", 11),
            wrap=WORD,
            yscrollcommand=text_scrollbar.set
        )
        self.content_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        text_scrollbar.config(command=self.content_text.yview)
        
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
        
        # 回复按钮
        reply_btn = ttk.Button(
            button_frame,
            text="回复",
            command=self.reply_post,
            bootstyle="primary",
            width=10
        )
        reply_btn.pack(side=RIGHT)
        
        # 设置焦点
        self.content_text.focus_set()

    def reply_post(self):
        """回复帖子"""
        content = self.content_text.get("1.0", END).strip()
        
        # 验证输入
        if not content:
            MessageDialog.show_warning(self, "提示", "请输入回复内容")
            self.content_text.focus_set()
            return
        
        if len(content) < 5:
            MessageDialog.show_warning(self, "提示", "回复内容至少需要5个字符")
            self.content_text.focus_set()
            return
        
        try:
            # 创建回复
            reply_id = self.discussion_service.create_post(
                user_id=self.user.id,
                content=content,
                parent_id=self.post_id
            )
            
            if reply_id:
                MessageDialog.show_info(self, "成功", "回复成功！")
                self.destroy()
            else:
                MessageDialog.show_error(self, "错误", "回复失败")
                
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"回复失败: {e}")