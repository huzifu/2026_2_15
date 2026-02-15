"""
学生学习资源界面
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass

import os
from ui.components import DataTable, SearchBar, MessageDialog

class StudentResourcesFrame(ttk.Frame):
    def __init__(self, parent, user, course_service):
        super().__init__(parent)
        self.user = user
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
            text="学习资源",
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
        
        # 类型筛选
        type_frame = ttk.Frame(course_frame)
        type_frame.pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(type_frame, text="类型:").pack(side=LEFT, padx=(0, 5))
        
        self.type_var = tk.StringVar(value="all")
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.type_var,
            values=["all", "document", "video", "audio", "other"],
            state="readonly",
            width=10
        )
        type_combo.pack(side=LEFT)
        type_combo.bind("<<ComboboxSelected>>", self.on_type_changed)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            course_frame,
            text="🔄 刷新",
            command=self.load_courses,
            bootstyle="outline"
        )
        refresh_btn.pack(side=RIGHT)
        
        # 资源表格区域
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 资源表格
        columns = [
            {"id": "id", "text": "ID", "width": 60},
            {"id": "title", "text": "资源名称", "width": 250},
            {"id": "type", "text": "类型", "width": 100},
            {"id": "size", "text": "大小", "width": 100},
            {"id": "uploader", "text": "上传者", "width": 100},
            {"id": "upload_time", "text": "上传时间", "width": 150},
            {"id": "description", "text": "描述", "width": 200}
        ]
        
        self.resource_table = DataTable(
            table_frame,
            columns=columns,
            height=15,
            selectmode="browse"
        )
        self.resource_table.pack(fill=BOTH, expand=True)
        
        # 绑定双击事件
        self.resource_table.tree.bind("<Double-1>", self.on_resource_double_click)
        
        # 操作按钮区域
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=X)
        
        # 查看详情按钮
        view_btn = ttk.Button(
            action_frame,
            text="👁️ 查看详情",
            command=self.view_resource_details,
            bootstyle="outline"
        )
        view_btn.pack(side=LEFT, padx=(0, 5))
        
        # 下载按钮
        download_btn = ttk.Button(
            action_frame,
            text="⬇️ 下载",
            command=self.download_resource,
            bootstyle="success"
        )
        download_btn.pack(side=LEFT, padx=(0, 5))
        
        # 搜索栏
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill=X, pady=(10, 0))
        
        self.search_bar = SearchBar(
            search_frame,
            placeholder="搜索资源名称或描述...",
            on_search=self.search_resources
        )
        self.search_bar.pack(fill=X)

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
            self.load_resources(course_id)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载资源失败: {e}")

    def on_type_changed(self, event):
        """类型筛选改变事件"""
        if hasattr(self, 'current_course_id'):
            self.load_resources(self.current_course_id)

    def load_resources(self, course_id):
        """加载资源列表"""
        try:
            resources = self.course_service.get_course_resources(course_id)
            
            # 应用类型筛选
            type_filter = self.type_var.get()
            if type_filter != "all":
                resources = [r for r in resources if r.file_type and type_filter in r.file_type]
            
            table_data = []
            for resource in resources:
                # 格式化文件大小
                size_text = self.format_file_size(resource.file_size)
                
                # 文件类型图标
                type_icon = self.get_file_type_icon(resource.file_type)
                type_text = f"{type_icon} {resource.file_type or '未知'}"
                
                table_data.append([
                    resource.id,
                    resource.title,
                    type_text,
                    size_text,
                    resource.uploader_name or "未知",
                    resource.created_at,
                    resource.description or ""
                ])
            
            self.resource_table.update_data(table_data)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"加载资源失败: {e}")

    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes is None:
            return "未知"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def get_file_type_icon(self, file_type):
        """获取文件类型图标"""
        if not file_type:
            return "📄"
        
        file_type = file_type.lower()
        if file_type in ['.pdf', '.doc', '.docx', '.txt', '.ppt', '.pptx']:
            return "📄"
        elif file_type in ['.mp4', '.avi', '.mov', '.wmv']:
            return "🎬"
        elif file_type in ['.mp3', '.wav', '.flac']:
            return "🎵"
        elif file_type in ['.zip', '.rar', '.7z']:
            return "📦"
        elif file_type in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return "🖼️"
        else:
            return "📄"

    def search_resources(self, keyword):
        """搜索资源"""
        if not hasattr(self, 'current_course_id'):
            return
        
        try:
            resources = self.course_service.get_course_resources(self.current_course_id)
            
            # 应用搜索筛选
            if keyword:
                keyword_lower = keyword.lower()
                resources = [
                    r for r in resources 
                    if keyword_lower in r.title.lower() or 
                       (r.description and keyword_lower in r.description.lower())
                ]
            
            # 应用类型筛选
            type_filter = self.type_var.get()
            if type_filter != "all":
                resources = [r for r in resources if r.file_type and type_filter in r.file_type]
            
            table_data = []
            for resource in resources:
                # 格式化文件大小
                size_text = self.format_file_size(resource.file_size)
                
                # 文件类型图标
                type_icon = self.get_file_type_icon(resource.file_type)
                type_text = f"{type_icon} {resource.file_type or '未知'}"
                
                table_data.append([
                    resource.id,
                    resource.title,
                    type_text,
                    size_text,
                    resource.uploader_name or "未知",
                    resource.created_at,
                    resource.description or ""
                ])
            
            self.resource_table.update_data(table_data)
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"搜索资源失败: {e}")

    def view_resource_details(self):
        """查看资源详情"""
        selected = self.resource_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个资源")
            return
        
        resource_id = selected[0]
        from ui.dialogs import ResourceDetailsDialog
        dialog = ResourceDetailsDialog(self, resource_id, self.course_service)
        dialog.grab_set()

    def download_resource(self):
        """下载资源"""
        selected = self.resource_table.get_selected()
        if not selected:
            MessageDialog.show_warning(self, "提示", "请先选择一个资源")
            return
        
        resource_id = selected[0]
        resource_name = selected[1]
        
        try:
            # 获取资源详情
            resources = self.course_service.get_course_resources(self.current_course_id)
            resource = None
            for r in resources:
                if r.id == resource_id:
                    resource = r
                    break
            
            if not resource or not resource.file_path:
                MessageDialog.show_warning(self, "提示", "资源文件不存在")
                return
            
            # 检查文件是否存在
            if not os.path.exists(resource.file_path):
                MessageDialog.show_warning(self, "提示", "资源文件不存在或已被删除")
                return
            
            # 选择保存位置
            from tkinter import filedialog
            save_path = filedialog.asksaveasfilename(
                title="保存资源",
                initialfile=resource.title + (resource.file_type or ""),
                defaultextension=resource.file_type or ""
            )
            
            if save_path:
                # 复制文件
                import shutil
                shutil.copy2(resource.file_path, save_path)
                MessageDialog.show_info(self, "成功", f"资源 '{resource_name}' 下载成功")
            
        except Exception as e:
            MessageDialog.show_error(self, "错误", f"下载资源失败: {e}")

    def on_resource_double_click(self, event):
        """资源双击事件"""
        self.view_resource_details()