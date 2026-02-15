"""
对话框存根 - 用于暂时不需要完整实现的对话框
这些对话框会显示基本信息，但不会执行实际操作
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

class BaseStubDialog(tk.Toplevel):
    """基础存根对话框"""
    def __init__(self, parent, title="对话框", message="此功能正在开发中"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(main_frame, text=title, font=("Helvetica", 14, "bold")).pack(pady=(0, 20))
        ttk.Label(main_frame, text=message, font=("Helvetica", 11)).pack(pady=20)
        
        ttk.Button(main_frame, text="确定", command=self.destroy, bootstyle="primary").pack()
        
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

# 创建所有存根对话框类
class ClassDetailsDialog(BaseStubDialog):
    def __init__(self, parent, class_id, class_service, course_service):
        super().__init__(parent, "班级详情", f"班级ID: {class_id}\n\n此功能正在开发中...")

class EditClassDialog(BaseStubDialog):
    def __init__(self, parent, class_id, class_service):
        super().__init__(parent, "编辑班级", f"编辑班级ID: {class_id}\n\n此功能正在开发中...")

class ManageStudentsDialog(BaseStubDialog):
    def __init__(self, parent, class_id, class_service):
        super().__init__(parent, "管理学生", f"管理班级ID: {class_id} 的学生\n\n此功能正在开发中...")

class CourseDetailsDialog(BaseStubDialog):
    def __init__(self, parent, course_id, course_service, class_service):
        super().__init__(parent, "课程详情", f"课程ID: {course_id}\n\n此功能正在开发中...")

class EditCourseDialog(BaseStubDialog):
    def __init__(self, parent, course_id, course_service):
        super().__init__(parent, "编辑课程", f"编辑课程ID: {course_id}\n\n此功能正在开发中...")

class ManageCourseContentDialog(BaseStubDialog):
    def __init__(self, parent, course_id, course_service):
        super().__init__(parent, "管理课程内容", f"管理课程ID: {course_id} 的内容\n\n此功能正在开发中...")

class ImportGradesDialog(BaseStubDialog):
    def __init__(self, parent, assignment_id, gradebook_service):
        super().__init__(parent, "导入成绩", "导入成绩功能正在开发中...")

class ExportGradesDialog(BaseStubDialog):
    def __init__(self, parent, export_data):
        super().__init__(parent, "导出成绩", "导出成绩功能正在开发中...")

class BulkEditGradesDialog(BaseStubDialog):
    def __init__(self, parent, assignment_id, gradebook_service):
        super().__init__(parent, "批量编辑成绩", "批量编辑成绩功能正在开发中...")

class GradeDetailsDialog(BaseStubDialog):
    def __init__(self, parent, student_id, course_id, gradebook_service):
        super().__init__(parent, "成绩详情", f"学生ID: {student_id}\n课程ID: {course_id}\n\n此功能正在开发中...")

class EditGradeDialog(BaseStubDialog):
    def __init__(self, parent, student_id, course_id, assignment_id, gradebook_service):
        super().__init__(parent, "编辑成绩", "编辑成绩功能正在开发中...")

class GenerateReportDialog(BaseStubDialog):
    def __init__(self, parent, course_id, gradebook_service):
        super().__init__(parent, "生成报告", "生成报告功能正在开发中...")

class AssignmentDetailsDialog(BaseStubDialog):
    def __init__(self, parent, assignment_id, assignment_service):
        super().__init__(parent, "作业详情", f"作业ID: {assignment_id}\n\n此功能正在开发中...")

class SubmitAssignmentDialog(BaseStubDialog):
    def __init__(self, parent, assignment_id, user, assignment_service, submission_service):
        super().__init__(parent, "提交作业", f"提交作业ID: {assignment_id}\n\n此功能正在开发中...")

class ViewSubmissionDialog(BaseStubDialog):
    def __init__(self, parent, assignment_id, user, submission_service):
        super().__init__(parent, "查看提交", f"查看作业ID: {assignment_id} 的提交\n\n此功能正在开发中...")

class ResourceDetailsDialog(BaseStubDialog):
    def __init__(self, parent, resource_id, course_service):
        super().__init__(parent, "资源详情", f"资源ID: {resource_id}\n\n此功能正在开发中...")

class ExportReportCardDialog(BaseStubDialog):
    def __init__(self, parent, report_card):
        super().__init__(parent, "导出成绩单", "导出成绩单功能正在开发中...")

class GradeAnalysisDialog(BaseStubDialog):
    def __init__(self, parent, student_id, course_id, gradebook_service):
        super().__init__(parent, "成绩分析", "成绩分析功能正在开发中...")

class CourseLearningDialog(BaseStubDialog):
    def __init__(self, parent, course_id, user, course_service):
        super().__init__(parent, "课程学习", f"课程ID: {course_id}\n\n此功能正在开发中...")

class ProfileSettingsDialog(BaseStubDialog):
    def __init__(self, parent, user, db):
        super().__init__(parent, "个人资料", "个人资料设置功能正在开发中...")

class SecuritySettingsDialog(BaseStubDialog):
    def __init__(self, parent, user, db):
        super().__init__(parent, "账户安全", "账户安全设置功能正在开发中...")

class NotificationSettingsDialog(BaseStubDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "通知设置", "通知设置功能正在开发中...")

class ThemeSettingsDialog(BaseStubDialog):
    def __init__(self, parent):
        super().__init__(parent, "主题设置", "主题设置功能正在开发中...")

class BackupSettingsDialog(BaseStubDialog):
    def __init__(self, parent, db):
        super().__init__(parent, "数据备份", "数据备份功能正在开发中...")

class AboutDialog(BaseStubDialog):
    def __init__(self, parent):
        super().__init__(parent, "关于系统", "智能教学管理系统\n版本 2.0.0\n\n一个功能完善的教学管理平台")

class PreferenceSettingsDialog(BaseStubDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "学习偏好", "学习偏好设置功能正在开发中...")

class CreateNotificationDialog(BaseStubDialog):
    def __init__(self, parent, user, notification_service, class_service):
        super().__init__(parent, "创建通知", "创建通知功能正在开发中...")

class AnalyticsDashboardFrame(BaseStubDialog):
    def __init__(self, parent, user, analytics_service, class_service, course_service, gradebook_service):
        super().__init__(parent, "数据分析", "数据分析功能正在开发中...")
