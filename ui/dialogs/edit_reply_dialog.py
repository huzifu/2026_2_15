"""
编辑回复对话框
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

class EditReplyDialog(tk.Toplevel):
    def __init__(self, parent, reply_id, user, discussion_service):
        super().__init__(parent)
        self.title("编辑回复")
        self.geometry("500x400")
        self.reply_id = reply_id
        self.user = user
        self.discussion_service = discussion_service
        
        self.create_widgets()
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(main_frame, text="编辑回复", font=("Helvetica", 16, "bold")).pack(anchor=W, pady=(0, 20))
        
        ttk.Label(main_frame, text="回复内容:", font=("Helvetica", 11)).pack(anchor=W, pady=(0, 5))
        
        self.content_text = tk.Text(main_frame, height=10, font=("Helvetica", 11), wrap=WORD)
        self.content_text.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X)
        
        ttk.Button(button_frame, text="取消", command=self.destroy, bootstyle="outline", width=10).pack(side=RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="保存", command=self.save_reply, bootstyle="primary", width=10).pack(side=RIGHT)

    def save_reply(self):
        """保存回复"""
        content = self.content_text.get("1.0", END).strip()
        if not content:
            MessageDialog.show_warning(self, "提示", "请输入回复内容")
            return
        
        try:
            success = self.discussion_service.update_post(self.reply_id, self.user.id, content=content)
            if success:
                MessageDialog.show_info(self, "成功", "回复已更新")
                self.destroy()
            else:
                MessageDialog.show_error(self, "错误", "更新失败")
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"更新失败: {e}")
