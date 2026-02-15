"""
通用UI组件
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

class Header(ttk.Frame):
    """头部组件"""
    def __init__(self, parent, title, user, on_logout, on_notification_click=None):
        super().__init__(parent, padding=10)
        self.user = user
        self.on_logout = on_logout
        self.on_notification_click = on_notification_click
        
        self.create_widgets(title)
    
    def create_widgets(self, title):
        # 左侧：标题和用户信息
        left_frame = ttk.Frame(self)
        left_frame.pack(side=LEFT, fill=Y)
        
        # 标题
        title_label = ttk.Label(
            left_frame,
            text=title,
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=LEFT, padx=(0, 20))
        
        # 用户信息
        user_frame = ttk.Frame(left_frame)
        user_frame.pack(side=LEFT)
        
        # 用户头像（使用文本占位）
        avatar_label = ttk.Label(
            user_frame,
            text="👤",
            font=("Helvetica", 14)
        )
        avatar_label.pack(side=LEFT, padx=(0, 5))
        
        # 用户名和角色
        user_info_frame = ttk.Frame(user_frame)
        user_info_frame.pack(side=LEFT)
        
        username_label = ttk.Label(
            user_info_frame,
            text=self.user.nickname,
            font=("Helvetica", 10, "bold")
        )
        username_label.pack(anchor=W)
        
        role_label = ttk.Label(
            user_info_frame,
            text=f"角色: {self.user.role}",
            font=("Helvetica", 8)
        )
        role_label.pack(anchor=W)
        
        # 右侧：操作按钮
        right_frame = ttk.Frame(self)
        right_frame.pack(side=RIGHT, fill=Y)
        
        # 通知按钮
        self.notification_btn = ttk.Button(
            right_frame,
            text="🔔",
            command=self.on_notification_click,
            bootstyle="link"
        )
        self.notification_btn.pack(side=LEFT, padx=5)
        
        # 通知徽章
        self.notification_badge = NotificationBadge(self.notification_btn, 0)
        
        # 设置按钮
        settings_btn = ttk.Button(
            right_frame,
            text="⚙️",
            command=self.show_settings,
            bootstyle="link"
        )
        settings_btn.pack(side=LEFT, padx=5)
        
        # 注销按钮
        logout_btn = ttk.Button(
            right_frame,
            text="注销",
            command=self.on_logout,
            bootstyle="outline-danger"
        )
        logout_btn.pack(side=LEFT, padx=5)
    
    def update_notification_count(self, count):
        """更新通知数量"""
        self.notification_badge.update_count(count)
    
    def show_settings(self):
        """显示设置菜单"""
        # 创建弹出菜单
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="个人资料", command=self.show_profile)
        menu.add_command(label="账户设置", command=self.show_account_settings)
        menu.add_separator()
        menu.add_command(label="主题设置", command=self.show_theme_settings)
        menu.add_command(label="关于系统", command=self.show_about)
        
        # 显示菜单
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()
    
    def show_profile(self):
        """显示个人资料"""
        print("显示个人资料")
    
    def show_account_settings(self):
        """显示账户设置"""
        print("显示账户设置")
    
    def show_theme_settings(self):
        """显示主题设置"""
        print("显示主题设置")
    
    def show_about(self):
        """显示关于"""
        print("显示关于")

class NotificationBadge:
    """通知徽章"""
    def __init__(self, parent, count=0):
        self.parent = parent
        self.count = count
        self.label = None
        
        if count > 0:
            self.create_badge()
    
    def create_badge(self):
        """创建徽章"""
        self.label = ttk.Label(
            self.parent,
            text=str(self.count) if self.count < 100 else "99+",
            font=("Helvetica", 8, "bold"),
            foreground="white",
            background="red",
            padding=(3, 1)
        )
        self.label.place(relx=0.7, rely=0.1)
    
    def update_count(self, count):
        """更新数量"""
        self.count = count
        
        if self.label:
            if count > 0:
                self.label.configure(
                    text=str(count) if count < 100 else "99+"
                )
                self.label.lift()
            else:
                self.label.place_forget()
        elif count > 0:
            self.create_badge()

class Sidebar(ttk.Frame):
    """侧边栏组件"""
    def __init__(self, parent, menu_items, selected_index=0):
        super().__init__(parent, padding=10, width=200)
        self.menu_items = menu_items
        self.selected_index = selected_index
        self.buttons = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # 侧边栏标题
        title_label = ttk.Label(
            self,
            text="导航菜单",
            font=("Helvetica", 12, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 菜单按钮
        for i, item in enumerate(self.menu_items):
            btn = ttk.Button(
                self,
                text=item["text"],
                command=lambda idx=i: self.on_menu_click(idx),
                bootstyle="light" if i != self.selected_index else "primary",
                width=20
            )
            btn.pack(fill=X, pady=2)
            self.buttons.append(btn)
    
    def on_menu_click(self, index):
        """菜单点击事件"""
        # 更新按钮样式
        for i, btn in enumerate(self.buttons):
            if i == index:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="light")
        
        # 执行菜单命令
        if self.menu_items[index]["command"]:
            self.menu_items[index]["command"]()

class ContentArea(ttk.Frame):
    """内容区域组件"""
    def __init__(self, parent):
        super().__init__(parent)
        self.current_content = None
    
    def clear(self):
        """清除当前内容"""
        if self.current_content:
            self.current_content.destroy()
            self.current_content = None
    
    def set_content(self, content_widget):
        """设置内容"""
        self.clear()
        self.current_content = content_widget
        self.current_content.pack(fill=BOTH, expand=True)

class StatCard(ttk.Frame):
    """统计卡片组件"""
    def __init__(self, parent, title, value, icon="📊", color="primary"):
        super().__init__(parent, padding=15)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        
        self.create_widgets()
    
    def create_widgets(self):
        # 卡片容器
        self.configure(bootstyle=self.color)
        
        # 图标
        icon_label = ttk.Label(
            self,
            text=self.icon,
            font=("Helvetica", 24)
        )
        icon_label.pack(anchor=W)
        
        # 数值
        value_label = ttk.Label(
            self,
            text=str(self.value),
            font=("Helvetica", 24, "bold")
        )
        value_label.pack(anchor=W, pady=(5, 0))
        
        # 标题
        title_label = ttk.Label(
            self,
            text=self.title,
            font=("Helvetica", 10)
        )
        title_label.pack(anchor=W)

class DataTable(ttk.Frame):
    """数据表格组件"""
    def __init__(self, parent, columns, data=None, height=10, selectmode="browse"):
        super().__init__(parent)
        self.columns = columns
        self.data = data or []
        self.height = height
        self.selectmode = selectmode
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        # 创建Treeview
        self.tree = ttk.Treeview(
            self,
            columns=[col["id"] for col in self.columns],
            show="headings",
            height=self.height,
            selectmode=self.selectmode
        )
        
        # 配置列
        for col in self.columns:
            self.tree.heading(col["id"], text=col["text"])
            self.tree.column(
                col["id"],
                width=col.get("width", 100),
                anchor=col.get("anchor", "w")
            )
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def load_data(self):
        """加载数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新数据
        for row in self.data:
            self.tree.insert("", END, values=row)
    
    def get_selected(self):
        """获取选中的行"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])["values"]
        return None
    
    def get_selected_index(self):
        """获取选中的索引"""
        selection = self.tree.selection()
        if selection:
            return self.tree.index(selection[0])
        return -1
    
    def clear_selection(self):
        """清除选择"""
        self.tree.selection_remove(self.tree.selection())
    
    def update_data(self, data):
        """更新数据"""
        self.data = data
        self.load_data()

class SearchBar(ttk.Frame):
    """搜索栏组件"""
    def __init__(self, parent, placeholder="搜索...", on_search=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self.on_search = on_search
        
        self.create_widgets()
    
    def create_widgets(self):
        # 搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self,
            textvariable=self.search_var,
            width=30
        )
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.configure(foreground="gray")
        
        # 绑定事件
        self.search_entry.bind("<FocusIn>", self.on_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_focus_out)
        self.search_entry.bind("<Return>", self.on_enter)
        
        # 搜索按钮
        search_btn = ttk.Button(
            self,
            text="🔍",
            command=self.perform_search,
            bootstyle="link"
        )
        
        # 布局
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        search_btn.pack(side=RIGHT)
    
    def on_focus_in(self, event):
        """获得焦点事件"""
        if self.search_entry.get() == self.placeholder:
            self.search_entry.delete(0, END)
            self.search_entry.configure(foreground="black")
    
    def on_focus_out(self, event):
        """失去焦点事件"""
        if not self.search_entry.get():
            self.search_entry.insert(0, self.placeholder)
            self.search_entry.configure(foreground="gray")
    
    def on_enter(self, event):
        """回车键事件"""
        self.perform_search()
    
    def perform_search(self):
        """执行搜索"""
        query = self.search_entry.get()
        if query != self.placeholder and self.on_search:
            self.on_search(query)
    
    def get_query(self):
        """获取搜索查询"""
        query = self.search_entry.get()
        return query if query != self.placeholder else ""

class Pagination(ttk.Frame):
    """分页组件"""
    def __init__(self, parent, total_pages=1, current_page=1, on_page_change=None):
        super().__init__(parent)
        self.total_pages = total_pages
        self.current_page = current_page
        self.on_page_change = on_page_change
        
        self.create_widgets()
    
    def create_widgets(self):
        # 上一页按钮
        self.prev_btn = ttk.Button(
            self,
            text="◀",
            command=self.go_prev,
            state="disabled" if self.current_page <= 1 else "normal",
            width=3
        )
        self.prev_btn.pack(side=LEFT, padx=2)
        
        # 页码显示
        self.page_label = ttk.Label(
            self,
            text=f"{self.current_page} / {self.total_pages}"
        )
        self.page_label.pack(side=LEFT, padx=10)
        
        # 下一页按钮
        self.next_btn = ttk.Button(
            self,
            text="▶",
            command=self.go_next,
            state="disabled" if self.current_page >= self.total_pages else "normal",
            width=3
        )
        self.next_btn.pack(side=LEFT, padx=2)
    
    def go_prev(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()
            if self.on_page_change:
                self.on_page_change(self.current_page)
    
    def go_next(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_buttons()
            if self.on_page_change:
                self.on_page_change(self.current_page)
    
    def update_buttons(self):
        """更新按钮状态"""
        self.prev_btn.configure(state="disabled" if self.current_page <= 1 else "normal")
        self.next_btn.configure(state="disabled" if self.current_page >= self.total_pages else "normal")
        self.page_label.configure(text=f"{self.current_page} / {self.total_pages}")
    
    def update_pagination(self, total_pages, current_page=1):
        """更新分页信息"""
        self.total_pages = total_pages
        self.current_page = current_page
        self.update_buttons()

class LoadingOverlay(ttk.Frame):
    """加载覆盖层"""
    def __init__(self, parent, message="加载中..."):
        super().__init__(parent)
        self.message = message
        
        # 半透明背景
        self.configure(bootstyle="inverse-light")
        
        # 加载内容
        self.create_widgets()
        
        # 居中显示
        self.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    def create_widgets(self):
        # 加载图标
        icon_label = ttk.Label(
            self,
            text="⏳",
            font=("Helvetica", 24)
        )
        icon_label.pack(pady=(0, 10))
        
        # 加载文字
        text_label = ttk.Label(
            self,
            text=self.message,
            font=("Helvetica", 10)
        )
        text_label.pack()
    
    def show(self):
        """显示加载层"""
        self.lift()
        self.update()
    
    def hide(self):
        """隐藏加载层"""
        self.place_forget()

class MessageDialog:
    """消息对话框"""
    @staticmethod
    def show_info(parent, title, message):
        """显示信息对话框"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(parent, title, message):
        """显示警告对话框"""
        from tkinter import messagebox
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_error(parent, title, message):
        """显示错误对话框"""
        from tkinter import messagebox
        messagebox.showerror(title, message)
    
    @staticmethod
    def ask_yesno(parent, title, message):
        """显示确认对话框"""
        from tkinter import messagebox
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def ask_yesnocancel(parent, title, message):
        """显示是/否/取消对话框"""
        from tkinter import messagebox
        return messagebox.askyesnocancel(title, message)