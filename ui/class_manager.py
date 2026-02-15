"""
班级管理界面
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

class ClassManagerFrame(ttk.Frame):
    def __init__(self, parent, user, class_service, course_service):
        super().__init__(parent)
        self.user = user
        self.class_service = class_service
        self.course_service = course_service
        
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        self.load_classes()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_container,
            text="班级管理",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # 工具栏
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 创建班级按钮
        create_btn = ttk.Button(
            toolbar,
            text="➕ 创建班级",
            command=self.create_class,
            bootstyle="success"
        )
        create_btn.pack(side=LEFT, padx=(0, 10))
        
        # 搜索栏
        self.search_bar = SearchBar(
            toolbar,
            placeholder="搜索班级名称、代码或描述...",
            on_search=self.search_classes
        )
        self.search_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            toolbar,
            text="🔄 刷新",
            command=self.load_classes,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 班级表格
        columns = [
            {"id": "id", "text": "ID", "width": 60},
            {"id": "name", "text": "班级名称", "width": 200},
            {"id": "code", "text": "班级代码", "width": 100},
            {"id": "student_count", "text": "学生人数", "width": 100},
            {"id": "max_students", "text": "人数上限", "width": 100},
            {"id": "status", "text": "状态", "width": 100},
            {"id": "created_at", "text": "创建时间", "width": 150}
        ]
        
        self.class_table = DataTable(
            main_container,
            columns=columns,
            height=15,
            selectmode="browse"
        )
        self.class_table.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 绑定双击事件
        self.class_table.tree.bind("<Double-1>", self.on_class_double_click)
        
        # 操作按钮区域
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=X, pady=(0, 10))
        
        # 查看详情按钮
        view_btn = ttk.Button(
            action_frame,
            text="👁️ 查看详情",
            command=self.view_class_details,
            bootstyle="outline"
        )
        view_btn.pack(side=LEFT, padx=(0, 5))
        
        # 编辑按钮
        edit_btn = ttk.Button(
            action_frame,
            text="✏️ 编辑",
            command=self.edit_class,
            bootstyle="outline"
        )
        edit_btn.pack(side=LEFT, padx=(0, 5))
        
        # 管理学生按钮
        manage_students_btn = ttk.Button(
            action_frame,
            text="👥 管理学生",
            command=self.manage_students,
            bootstyle="outline"
        )
        manage_students_btn.pack(side=LEFT, padx=(0, 5))
        
        # 删除按钮
        delete_btn = ttk.Button(
            action_frame,
            text="🗑️ 删除",
            command=self.delete_class,
            bootstyle="outline-danger"
        )
        delete_btn.pack(side=LEFT, padx=(0, 5))
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_container, text="统计信息", padding=10)
        stats_frame.pack(fill=X)
        
        # 创建统计标签
        self.stats_labels = {}
        stats_data = [
            ("total_classes", "班级总数", "0"),
            ("active_classes", "活跃班级", "0"),
            ("total_students", "学生总数", "0"),
            ("average_students", "平均人数", "0")
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

    def load_classes(self):
        """加载班级列表"""
        try:
            classes = self.class_service.get_classes_by_teacher(self.user.id)
            table_data = []
            
            for cls in classes:
                # 获取学生人数
                students = self.class_service.get_class_students(cls.id)
                student_count = len(students)
                
                table_data.append([
                    cls.id,
                    cls.name,
                    cls.code,
                    f"{student_count}/{cls.max_students}",
                    cls.max_students,
                    cls.status,
                    cls.created_at
                ])
            
            self.class_table.update_data(table_data)
            self.update_statistics(classes)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载班级失败: {e}")

    def update_statistics(self, classes):
        """更新统计信息"""
        if not classes:
            for key in self.stats_labels:
                self.stats_labels[key].configure(text="0")
            return
        
        total_classes = len(classes)
        active_classes = len([c for c in classes if c.status == 'active'])
        
        total_students = 0
        for cls in classes:
            students = self.class_service.get_class_students(cls.id)
            total_students += len(students)
        
        average_students = total_students / total_classes if total_classes > 0 else 0
        
        self.stats_labels["total_classes"].configure(text=str(total_classes))
        self.stats_labels["active_classes"].configure(text=str(active_classes))
        self.stats_labels["total_students"].configure(text=str(total_students))
        self.stats_labels["average_students"].configure(text=f"{average_students:.1f}")

    def search_classes(self, keyword):
        """搜索班级"""
        try:
            classes = self.class_service.search_classes(keyword=keyword, teacher_id=self.user.id)
            table_data = []
            
            for cls in classes:
                students = self.class_service.get_class_students(cls.id)
                student_count = len(students)
                
                table_data.append([
                    cls.id,
                    cls.name,
                    cls.code,
                    f"{student_count}/{cls.max_students}",
                    cls.max_students,
                    cls.status,
                    cls.created_at
                ])
            
            self.class_table.update_data(table_data)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"搜索班级失败: {e}")

    def create_class(self):
        """创建班级"""
        from ui.dialogs import CreateClassDialog
        dialog = CreateClassDialog(self, self.user, self.class_service)
        dialog.grab_set()
        self.wait_window(dialog)
        self.load_classes()

    def view_class_details(self):
        """查看班级详情"""
        selected = self.class_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个班级")
            return
        
        class_id = selected[0]
        from ui.dialogs import ClassDetailsDialog
        dialog = ClassDetailsDialog(self, class_id, self.class_service, self.course_service)
        dialog.grab_set()

    def edit_class(self):
        """编辑班级"""
        selected = self.class_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个班级")
            return
        
        class_id = selected[0]
        from ui.dialogs import EditClassDialog
        dialog = EditClassDialog(self, class_id, self.class_service)
        dialog.grab_set()
        self.wait_window(dialog)
        self.load_classes()

    def manage_students(self):
        """管理学生"""
        selected = self.class_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个班级")
            return
        
        class_id = selected[0]
        from ui.dialogs import ManageStudentsDialog
        dialog = ManageStudentsDialog(self, class_id, self.class_service)
        dialog.grab_set()
        self.wait_window(dialog)
        self.load_classes()

    def delete_class(self):
        """删除班级"""
        selected = self.class_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个班级")
            return
        
        class_id = selected[0]
        class_name = selected[1]
        
        if not MessageDialog.ask_yesno(self, "确认删除", f"确定要删除班级 '{class_name}' 吗？"):
            return
        
        try:
            success = self.class_service.delete_class(class_id)
            if success:
                MessageDialog.show_info(self, "成功", "班级已删除")
                self.load_classes()
            else:
                MessageDialog.show_error(self, "错误", "删除班级失败")
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"删除班级失败: {e}")

    def on_class_double_click(self, event):
        """班级双击事件"""
        self.view_class_details()