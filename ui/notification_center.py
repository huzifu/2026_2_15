"""
通知中心界面
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

class NotificationCenter(ttk.Frame):
    def __init__(self, parent, user, notification_service):
        super().__init__(parent)
        self.user = user
        self.notification_service = notification_service
        
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        self.load_notifications()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_container,
            text="通知中心",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 工具栏
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 标记全部已读按钮
        mark_all_read_btn = ttk.Button(
            toolbar,
            text="✅ 标记全部已读",
            command=self.mark_all_as_read,
            bootstyle="outline"
        )
        mark_all_read_btn.pack(side=LEFT, padx=(0, 10))
        
        # 删除已读按钮
        delete_read_btn = ttk.Button(
            toolbar,
            text="🗑️ 删除已读通知",
            command=self.delete_read_notifications,
            bootstyle="outline"
        )
        delete_read_btn.pack(side=LEFT, padx=(0, 10))
        
        # 搜索栏
        self.search_bar = SearchBar(
            toolbar,
            placeholder="搜索通知标题或内容...",
            on_search=self.search_notifications
        )
        self.search_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 类型筛选
        type_frame = ttk.Frame(toolbar)
        type_frame.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(type_frame, text="类型:").pack(side=LEFT, padx=(0, 5))
        
        self.type_var = tk.StringVar(value="all")
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.type_var,
            values=["all", "assignment", "grade", "discussion", "system", "reminder"],
            state="readonly",
            width=10
        )
        type_combo.pack(side=LEFT)
        type_combo.bind("<<ComboboxSelected>>", self.on_type_changed)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            toolbar,
            text="🔄 刷新",
            command=self.load_notifications,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 通知表格区域
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 左侧：通知列表
        left_frame = ttk.Frame(table_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 通知表格
        columns = [
            {"id": "id", "text": "ID", "width": 60},
            {"id": "type", "text": "类型", "width": 100},
            {"id": "title", "text": "标题", "width": 250},
            {"id": "is_read", "text": "状态", "width": 80},
            {"id": "created_at", "text": "时间", "width": 150}
        ]
        
        self.notification_table = DataTable(
            left_frame,
            columns=columns,
            height=15,
            selectmode="browse"
        )
        self.notification_table.pack(fill=BOTH, expand=True)
        
        # 绑定双击事件
        self.notification_table.tree.bind("<Double-1>", self.on_notification_double_click)
        
        # 分页控件
        self.pagination = Pagination(
            left_frame,
            total_pages=1,
            current_page=1,
            on_page_change=self.on_page_changed
        )
        self.pagination.pack(fill=X, pady=(10, 0))
        
        # 右侧：通知详情
        right_frame = ttk.Frame(table_frame, width=500)
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))
        
        # 通知详情区域
        self.detail_frame = ttk.LabelFrame(right_frame, text="通知详情", padding=10)
        self.detail_frame.pack(fill=BOTH, expand=True)
        
        # 默认显示提示
        self.default_label = ttk.Label(
            self.detail_frame,
            text="请选择一个通知查看详情",
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
            command=self.view_notification_details,
            bootstyle="outline"
        )
        view_btn.pack(side=LEFT, padx=(0, 5))
        
        # 标记已读按钮
        mark_read_btn = ttk.Button(
            action_frame,
            text="✅ 标记已读",
            command=self.mark_as_read,
            bootstyle="outline"
        )
        mark_read_btn.pack(side=LEFT, padx=(0, 5))
        
        # 删除按钮
        delete_btn = ttk.Button(
            action_frame,
            text="🗑️ 删除",
            command=self.delete_notification,
            bootstyle="outline-danger"
        )
        delete_btn.pack(side=LEFT, padx=(0, 5))
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_container, text="通知统计", padding=10)
        stats_frame.pack(fill=X, pady=(10, 0))
        
        # 创建统计标签
        self.stats_labels = {}
        stats_data = [
            ("total_notifications", "通知总数", "0"),
            ("unread_notifications", "未读通知", "0"),
            ("today_notifications", "今日通知", "0"),
            ("week_notifications", "本周通知", "0")
        ]
        
        for i, (key, label, value) in enumerate(stats_data):
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.pack(side=LEFT, padx=20)
            
            ttk.Label(
                stat_frame,
                text=label,
                font=("Helvetica", 9)
            ).pack()
            
            self.stats_labels[key] = ttk.Label(
                stat_frame,
                text=value,
                font=("Helvetica", 14, "bold")
            )
            self.stats_labels[key].pack()

    def load_notifications(self):
        """加载通知列表"""
        try:
            notifications = self.notification_service.get_user_notifications(
                self.user.id, unread_only=False, limit=100
            )
            
            table_data = []
            for notification in notifications:
                # 类型图标
                type_icons = {
                    'assignment': '📝',
                    'grade': '��',
                    'discussion': '💬',
                    'system': '⚙️',
                    'reminder': '⏰'
                }
                type_icon = type_icons.get(notification['type'], '📌')
                type_text = f"{type_icon} {notification['type']}"
                
                # 状态文本
                status_text = "未读" if not notification['is_read'] else "已读"
                
                table_data.append([
                    notification['id'],
                    type_text,
                    notification['title'],
                    status_text,
                    notification['created_at']
                ])
            
            self.notification_table.update_data(table_data)
            self.update_statistics(notifications)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载通知失败: {e}")

    def update_statistics(self, notifications):
        """更新统计信息"""
        if not notifications:
            for key in self.stats_labels:
                self.stats_labels[key].configure(text="0")
            return
        
        total_notifications = len(notifications)
        unread_notifications = len([n for n in notifications if not n['is_read']])
        
        # 计算今日和本周通知
        from datetime import datetime, timedelta
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        today_count = 0
        week_count = 0
        
        for notification in notifications:
            created_date = datetime.strptime(notification['created_at'], '%Y-%m-%d %H:%M:%S').date()
            if created_date == today:
                today_count += 1
            if created_date >= week_ago:
                week_count += 1
        
        self.stats_labels["total_notifications"].configure(text=str(total_notifications))
        self.stats_labels["unread_notifications"].configure(text=str(unread_notifications))
        self.stats_labels["today_notifications"].configure(text=str(today_count))
        self.stats_labels["week_notifications"].configure(text=str(week_count))

    def on_type_changed(self, event):
        """类型筛选改变事件"""
        # 这里可以实现按类型筛选功能
        pass

    def on_page_changed(self, page):
        """分页改变事件"""
        # 这里可以实现分页功能
        pass

    def search_notifications(self, keyword):
        """搜索通知"""
        # 这里可以实现通知搜索功能
        pass

    def clear_notification_details(self):
        """清除通知详情"""
        # 移除默认标签
        if self.default_label.winfo_ismapped():
            self.default_label.pack_forget()
        
        # 清除现有内容
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        # 重新添加默认标签
        self.default_label = ttk.Label(
            self.detail_frame,
            text="请选择一个通知查看详情",
            font=("Helvetica", 12)
        )
        self.default_label.pack(expand=True)

    def show_notification_details(self, notification_id):
        """显示通知详情"""
        try:
            # 获取通知详情
            notifications = self.notification_service.get_user_notifications(
                self.user.id, unread_only=False, limit=100
            )
            
            notification = None
            for n in notifications:
                if n['id'] == notification_id:
                    notification = n
                    break
            
            if not notification:
                MessageDialog.show_warning(self, "提示", "通知不存在")
                return
            
            # 清除现有内容
            for widget in self.detail_frame.winfo_children():
                widget.destroy()
            
            # 创建滚动区域
            canvas = tk.Canvas(self.detail_frame)
            scrollbar = ttk.Scrollbar(self.detail_frame, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            # 类型图标
            type_icons = {
                'assignment': '📝',
                'grade': '📊',
                'discussion': '💬',
                'system': '⚙️',
                'reminder': '⏰'
            }
            type_icon = type_icons.get(notification['type'], '📌')
            
            # 通知标题
            title_label = ttk.Label(
                scrollable_frame,
                text=f"{type_icon} {notification['title']}",
                font=("Helvetica", 14, "bold"),
                wraplength=450
            )
            title_label.pack(anchor=W, pady=(0, 10))
            
            # 时间信息
            time_frame = ttk.Frame(scrollable_frame)
            time_frame.pack(anchor=W, pady=(0, 10))
            
            ttk.Label(
                time_frame,
                text=f"时间: {notification['created_at']}",
                font=("Helvetica", 10)
            ).pack(side=LEFT, padx=(0, 10))
            
            # 状态
            status_text = "未读" if not notification['is_read'] else "已读"
            status_color = "danger" if not notification['is_read'] else "success"
            status_label = ttk.Label(
                time_frame,
                text=status_text,
                font=("Helvetica", 10, "bold"),
                bootstyle=status_color
            )
            status_label.pack(side=LEFT)
            
            # 通知内容
            if notification['content']:
                content_label = ttk.Label(
                    scrollable_frame,
                    text=notification['content'],
                    font=("Helvetica", 11),
                    wraplength=450,
                    justify=LEFT
                )
                content_label.pack(anchor=W, pady=(0, 20))
            
            # 相关操作按钮
            if notification['related_id'] and notification['related_type']:
                action_frame = ttk.Frame(scrollable_frame)
                action_frame.pack(anchor=W, pady=(0, 10))
                
                ttk.Label(
                    action_frame,
                    text="相关操作:",
                    font=("Helvetica", 10, "bold")
                ).pack(side=LEFT, padx=(0, 10))
                
                # 根据类型显示不同的操作按钮
                if notification['related_type'] == 'assignment':
                    view_btn = ttk.Button(
                        action_frame,
                        text="查看作业",
                        command=lambda: self.view_related_assignment(notification['related_id']),
                        bootstyle="outline"
                    )
                    view_btn.pack(side=LEFT)
                
                elif notification['related_type'] == 'submission':
                    view_btn = ttk.Button(
                        action_frame,
                        text="查看提交",
                        command=lambda: self.view_related_submission(notification['related_id']),
                        bootstyle="outline"
                    )
                    view_btn.pack(side=LEFT)
                
                elif notification['related_type'] == 'discussion':
                    view_btn = ttk.Button(
                        action_frame,
                        text="查看讨论",
                        command=lambda: self.view_related_discussion(notification['related_id']),
                        bootstyle="outline"
                    )
                    view_btn.pack(side=LEFT)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载通知详情失败: {e}")

    def view_related_assignment(self, assignment_id):
        """查看相关作业"""
        # 这里可以实现查看作业的功能
        MessageDialog.show_info(self, "提示", f"查看作业 ID: {assignment_id}")

    def view_related_submission(self, submission_id):
        """查看相关提交"""
        # 这里可以实现查看提交的功能
        MessageDialog.show_info(self, "提示", f"查看提交 ID: {submission_id}")

    def view_related_discussion(self, discussion_id):
        """查看相关讨论"""
        # 这里可以实现查看讨论的功能
        MessageDialog.show_info(self, "提示", f"查看讨论 ID: {discussion_id}")

    def view_notification_details(self):
        """查看通知详情"""
        selected = self.notification_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个通知")
            return
        
        notification_id = selected[0]
        self.show_notification_details(notification_id)

    def mark_as_read(self):
        """标记为已读"""
        selected = self.notification_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个通知")
            return
        
        notification_id = selected[0]
        
        try:
            success = self.notification_service.mark_as_read(notification_id, self.user.id)
            if success:
                MessageDialog.show_info(self, "成功", "通知已标记为已读")
                self.load_notifications()
                if hasattr(self, 'current_notification_id') and self.current_notification_id == notification_id:
                    self.show_notification_details(notification_id)
            else:
                MessageDialog.show_error(self, "错误", "标记失败")
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"标记失败: {e}")

    def mark_all_as_read(self):
        """标记全部为已读"""
        if not MessageDialog.ask_yesno(self, "确认标记", "确定要标记所有通知为已读吗？"):
            return
        
        try:
            success = self.notification_service.mark_all_as_read(self.user.id)
            if success:
                MessageDialog.show_info(self, "成功", "所有通知已标记为已读")
                self.load_notifications()
            else:
                MessageDialog.show_error(self, "错误", "标记失败")
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"标记失败: {e}")

    def delete_notification(self):
        """删除通知"""
        selected = self.notification_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个通知")
            return
        
        notification_id = selected[0]
        notification_title = selected[2]
        
        if not MessageDialog.ask_yesno(self, "确认删除", f"确定要删除通知 '{notification_title}' 吗？"):
            return
        
        try:
            success = self.notification_service.delete_notification(notification_id, self.user.id)
            if success:
                MessageDialog.show_info(self, "成功", "通知已删除")
                self.load_notifications()
                self.clear_notification_details()
            else:
                MessageDialog.show_error(self, "错误", "删除失败")
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"删除失败: {e}")

    def delete_read_notifications(self):
        """删除已读通知"""
        if not MessageDialog.ask_yesno(self, "确认删除", "确定要删除所有已读通知吗？"):
            return
        
        try:
            # 获取所有已读通知
            notifications = self.notification_service.get_user_notifications(
                self.user.id, unread_only=False, limit=1000
            )
            
            deleted_count = 0
            for notification in notifications:
                if notification['is_read']:
                    success = self.notification_service.delete_notification(notification['id'], self.user.id)
                    if success:
                        deleted_count += 1
            
            MessageDialog.show_info(self, "成功", f"已删除 {deleted_count} 条已读通知")
            self.load_notifications()
            self.clear_notification_details()
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"删除失败: {e}")

    def on_notification_double_click(self, event):
        """通知双击事件"""
        self.view_notification_details()