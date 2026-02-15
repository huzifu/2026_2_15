"""
学生讨论区界面
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

from ui.components import DataTable, SearchBar, Pagination, MessageDialog

class StudentDiscussionFrame(ttk.Frame):
    def __init__(self, parent, user, discussion_service, course_service):
        super().__init__(parent)
        self.user = user
        self.discussion_service = discussion_service
        self.course_service = course_service
        
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        self.load_courses()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_container,
            text="讨论区",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 课程选择区域
        course_frame = ttk.LabelFrame(main_container, text="选择课程", padding=10)
        course_frame.pack(fill=X, pady=(0, 10))
        
        # 课程选择下拉框
        ttk.Label(course_frame, text="课程:").pack(side=LEFT, padx=(0, 5))
        
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(
            course_frame,
            textvariable=self.course_var,
            state="readonly",
            width=40
        )
        self.course_combo.pack(side=LEFT, padx=(0, 10))
        self.course_combo.bind("<<ComboboxSelected>>", self.on_course_selected)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            course_frame,
            text="🔄 刷新",
            command=self.load_courses,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 讨论帖子区域
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 左侧：帖子列表
        left_frame = ttk.Frame(table_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 工具栏
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 新建帖子按钮
        new_post_btn = ttk.Button(
            toolbar,
            text="💬 新建帖子",
            command=self.create_post,
            bootstyle="success"
        )
        new_post_btn.pack(side=LEFT, padx=(0, 5))
        
        # 搜索栏
        self.search_bar = SearchBar(
            toolbar,
            placeholder="搜索帖子标题或内容...",
            on_search=self.search_posts
        )
        self.search_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 状态筛选
        status_frame = ttk.Frame(toolbar)
        status_frame.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(status_frame, text="状态:").pack(side=LEFT, padx=(0, 5))
        
        self.status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=["all", "active", "closed"],
            state="readonly",
            width=10
        )
        status_combo.pack(side=LEFT)
        status_combo.bind("<<ComboboxSelected>>", self.on_status_changed)
        
        # 帖子表格
        columns = [
            {"id": "id", "text": "ID", "width": 60},
            {"id": "title", "text": "标题", "width": 250},
            {"id": "author", "text": "作者", "width": 100},
            {"id": "reply_count", "text": "回复数", "width": 80},
            {"id": "status", "text": "状态", "width": 100},
            {"id": "created_at", "text": "发布时间", "width": 150},
            {"id": "last_reply", "text": "最后回复", "width": 150}
        ]
        
        self.post_table = DataTable(
            left_frame,
            columns=columns,
            height=15,
            selectmode="browse"
        )
        self.post_table.pack(fill=BOTH, expand=True)
        
        # 绑定双击事件
        self.post_table.tree.bind("<Double-1>", self.on_post_double_click)
        
        # 分页控件
        self.pagination = Pagination(
            left_frame,
            total_pages=1,
            current_page=1,
            on_page_change=self.on_page_changed
        )
        self.pagination.pack(fill=X, pady=(10, 0))
        
        # 右侧：帖子详情和回复
        right_frame = ttk.Frame(table_frame, width=500)
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))
        
        # 帖子详情区域
        self.post_detail_frame = ttk.LabelFrame(right_frame, text="帖子详情", padding=10)
        self.post_detail_frame.pack(fill=BOTH, expand=True)
        
        # 默认显示提示
        self.default_label = ttk.Label(
            self.post_detail_frame,
            text="请选择一个帖子查看详情",
            font=("Helvetica", 12)
        )
        self.default_label.pack(expand=True)
        
        # 操作按钮区域
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=X)
        
        # 查看详情按钮
        view_btn = ttk.Button(
            action_frame,
            text="👁️ 查看详情",
            command=self.view_post_details,
            bootstyle="outline"
        )
        view_btn.pack(side=LEFT, padx=(0, 5))
        
        # 回复帖子按钮
        reply_btn = ttk.Button(
            action_frame,
            text="💬 回复",
            command=self.reply_post,
            bootstyle="outline"
        )
        reply_btn.pack(side=LEFT, padx=(0, 5))
        
        # 我的帖子按钮
        my_posts_btn = ttk.Button(
            action_frame,
            text="📝 我的帖子",
            command=self.show_my_posts,
            bootstyle="outline"
        )
        my_posts_btn.pack(side=LEFT, padx=(0, 5))
        
        # 删除按钮（仅对自己的帖子）
        delete_btn = ttk.Button(
            action_frame,
            text="🗑️ 删除",
            command=self.delete_post,
            bootstyle="outline-danger"
        )
        delete_btn.pack(side=LEFT, padx=(0, 5))

    def load_courses(self):
        """加载课程列表"""
        try:
            courses = self.course_service.get_available_courses(self.user.id)
            enrolled_courses = [c for c in courses if c.get('student_progress')]
            
            course_options = []
            self.course_map = {}
            
            for course in enrolled_courses:
                course_options.append(f"{course['id']}: {course['title']}")
                self.course_map[course['id']] = course
            
            self.course_combo['values'] = course_options
            
            if course_options:
                self.course_combo.current(0)
                self.on_course_selected(None)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载课程失败: {e}")

    def on_course_selected(self, event):
        """课程选择事件"""
        course_text = self.course_var.get()
        if not course_text:
            return
        
        try:
            course_id = int(course_text.split(":")[0])
            self.current_course_id = course_id
            self.load_posts(page=1)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载讨论帖子失败: {e}")

    def on_status_changed(self, event):
        """状态筛选改变事件"""
        if hasattr(self, 'current_course_id'):
            self.load_posts(page=1)

    def on_page_changed(self, page):
        """分页改变事件"""
        self.load_posts(page=page)

    def load_posts(self, page=1):
        """加载讨论帖子"""
        if not hasattr(self, 'current_course_id'):
            return
        
        try:
            status = self.status_var.get()
            if status == 'all':
                status = None
            
            discussions = self.discussion_service.get_course_discussions(
                self.current_course_id, page=page
            )
            
            table_data = []
            for post in discussions['posts']:
                table_data.append([
                    post['id'],
                    post['title'],
                    post['author_name'],
                    post['reply_count'],
                    post['status'],
                    post['created_at'],
                    post.get('last_reply_time', '')
                ])
            
            self.post_table.update_data(table_data)
            self.pagination.update_pagination(
                discussions['total_pages'],
                discussions['page']
            )
            
            # 清除帖子详情
            self.clear_post_details()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载讨论帖子失败: {e}")

    def search_posts(self, keyword):
        """搜索帖子"""
        if not hasattr(self, 'current_course_id'):
            return
        
        try:
            search_results = self.discussion_service.search_discussions(
                keyword=keyword,
                course_id=self.current_course_id,
                page=1
            )
            
            table_data = []
            for post in search_results['posts']:
                table_data.append([
                    post['id'],
                    post['title'],
                    post['author_name'],
                    post['reply_count'],
                    post['status'],
                    post['created_at'],
                    post.get('last_reply_time', '')
                ])
            
            self.post_table.update_data(table_data)
            self.pagination.update_pagination(
                search_results['total_pages'],
                search_results['page']
            )
            
            # 清除帖子详情
            self.clear_post_details()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"搜索帖子失败: {e}")

    def clear_post_details(self):
        """清除帖子详情"""
        # 移除默认标签
        if self.default_label.winfo_ismapped():
            self.default_label.pack_forget()
        
        # 清除现有内容
        for widget in self.post_detail_frame.winfo_children():
            widget.destroy()
        
        # 重新添加默认标签
        self.default_label = ttk.Label(
            self.post_detail_frame,
            text="请选择一个帖子查看详情",
            font=("Helvetica", 12)
        )
        self.default_label.pack(expand=True)

    def show_post_details(self, post_id):
        """显示帖子详情"""
        try:
            post_details = self.discussion_service.get_post_by_id(post_id)
            if not post_details:
                MessageDialog.show_warning(self, "提示", "帖子不存在")
                return
            
            # 清除现有内容
            for widget in self.post_detail_frame.winfo_children():
                widget.destroy()
            
            # 创建滚动区域
            canvas = tk.Canvas(self.post_detail_frame)
            scrollbar = ttk.Scrollbar(self.post_detail_frame, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            # 帖子标题
            title_label = ttk.Label(
                scrollable_frame,
                text=post_details['title'],
                font=("Helvetica", 14, "bold"),
                wraplength=450
            )
            title_label.pack(anchor=W, pady=(0, 10))
            
            # 作者信息
            author_frame = ttk.Frame(scrollable_frame)
            author_frame.pack(anchor=W, pady=(0, 10))
            
            ttk.Label(
                author_frame,
                text=f"作者: {post_details['author_name']}",
                font=("Helvetica", 10)
            ).pack(side=LEFT, padx=(0, 10))
            
            ttk.Label(
                author_frame,
                text=f"发布时间: {post_details['created_at']}",
                font=("Helvetica", 10)
            ).pack(side=LEFT)
            
            # 状态标签
            status_color = "success" if post_details['status'] == 'closed' else "primary"
            status_label = ttk.Label(
                author_frame,
                text=post_details['status'].upper(),
                font=("Helvetica", 9, "bold"),
                bootstyle=status_color
            )
            status_label.pack(side=LEFT, padx=(10, 0))
            
            # 帖子内容
            content_label = ttk.Label(
                scrollable_frame,
                text=post_details['content'],
                font=("Helvetica", 11),
                wraplength=450,
                justify=LEFT
            )
            content_label.pack(anchor=W, pady=(0, 20))
            
            # 回复列表
            replies = self.discussion_service.get_post_replies(post_id)
            if replies:
                ttk.Label(
                    scrollable_frame,
                    text=f"回复 ({len(replies)})",
                    font=("Helvetica", 12, "bold")
                ).pack(anchor=W, pady=(0, 10))
                
                for reply in replies:
                    reply_frame = ttk.Frame(scrollable_frame, padding=10)
                    reply_frame.pack(fill=X, pady=5)
                    reply_frame.configure(bootstyle="light")
                    
                    # 回复作者
                    author_info = ttk.Frame(reply_frame)
                    author_info.pack(anchor=W, pady=(0, 5))
                    
                    ttk.Label(
                        author_info,
                        text=f"{reply['author_name']}",
                        font=("Helvetica", 9, "bold")
                    ).pack(side=LEFT, padx=(0, 10))
                    
                    ttk.Label(
                        author_info,
                        text=reply['created_at'],
                        font=("Helvetica", 9)
                    ).pack(side=LEFT)
                    
                    # 如果是自己的回复，显示编辑按钮
                    if reply['user_id'] == self.user.id:
                        edit_btn = ttk.Button(
                            author_info,
                            text="编辑",
                            command=lambda rid=reply['id']: self.edit_reply(rid),
                            bootstyle="link",
                            padding=0
                        )
                        edit_btn.pack(side=RIGHT)
                    
                    # 回复内容
                    ttk.Label(
                        reply_frame,
                        text=reply['content'],
                        font=("Helvetica", 10),
                        wraplength=430,
                        justify=LEFT
                    ).pack(anchor=W)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载帖子详情失败: {e}")

    def create_post(self):
        """创建新帖子"""
        if not hasattr(self, 'current_course_id'):
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")
            return
        
        from ui.dialogs import CreatePostDialog
        dialog = CreatePostDialog(
            self, 
            self.user, 
            self.current_course_id, 
            self.discussion_service
        )
        dialog.grab_set()
        self.wait_window(dialog)
        self.load_posts(page=1)

    def view_post_details(self):
        """查看帖子详情"""
        selected = self.post_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个帖子")
            return
        
        post_id = selected[0]
        self.show_post_details(post_id)

    def reply_post(self):
        """回复帖子"""
        selected = self.post_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个帖子")
            return
        
        post_id = selected[0]
        from ui.dialogs import ReplyPostDialog
        dialog = ReplyPostDialog(
            self, 
            self.user, 
            post_id, 
            self.discussion_service
        )
        dialog.grab_set()
        self.wait_window(dialog)
        self.show_post_details(post_id)

    def show_my_posts(self):
        """显示我的帖子"""
        if not hasattr(self, 'current_course_id'):
            MessageDialog.show_warning(self, "提示", "请先选择一个课程")
            return
        
        try:
            my_posts = self.discussion_service.get_user_discussions(self.user.id, page=1)
            
            table_data = []
            for post in my_posts['posts']:
                table_data.append([
                    post['id'],
                    post['title'],
                    post['author_name'],
                    post['reply_count'],
                    post['status'],
                    post['created_at'],
                    post.get('last_reply_time', '')
                ])
            
            self.post_table.update_data(table_data)
            self.pagination.update_pagination(
                my_posts['total_pages'],
                my_posts['page']
            )
            
            # 清除帖子详情
            self.clear_post_details()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载我的帖子失败: {e}")

    def delete_post(self):
        """删除帖子"""
        selected = self.post_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个帖子")
            return
        
        post_id = selected[0]
        post_title = selected[1]
        post_author = selected[2]
        
        # 检查是否是自己的帖子
        if post_author != self.user.nickname:
            MessageDialog.show_warning(self, "提示", "只能删除自己的帖子")
            return
        
        if not MessageDialog.ask_yesno(self, "确认删除", f"确定要删除帖子 '{post_title}' 吗？"):
            return
        
        try:
            success = self.discussion_service.delete_post(post_id, self.user.id)
            if success:
                MessageDialog.show_info(self, "成功", "帖子已删除")
                self.load_posts(page=self.pagination.current_page)
                self.clear_post_details()
            else:
                MessageDialog.show_error(self, "错误", "删除失败")
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"删除失败: {e}")

    def edit_reply(self, reply_id):
        """编辑回复"""
        from ui.dialogs import EditReplyDialog
        dialog = EditReplyDialog(self, reply_id, self.user, self.discussion_service)
        dialog.grab_set()
        self.wait_window(dialog)
        
        # 刷新当前帖子详情
        selected = self.post_table.get_selected()
        if selected:
            self.show_post_details(selected[0])

    def on_post_double_click(self, event):
        """帖子双击事件"""
        self.view_post_details()