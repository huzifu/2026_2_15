"""
对话框模块
"""
# 导入已实现的对话框类
from .create_class_dialog import CreateClassDialog
from .create_course_dialog import CreateCourseDialog
from .create_assignment_dialog import CreateAssignmentDialog
from .create_post_dialog import CreatePostDialog
from .reply_post_dialog import ReplyPostDialog
from .edit_reply_dialog import EditReplyDialog

# 导入存根对话框类（暂未完整实现的功能）
from ._dialog_stubs import (
    ClassDetailsDialog,
    EditClassDialog,
    ManageStudentsDialog,
    CourseDetailsDialog,
    EditCourseDialog,
    ManageCourseContentDialog,
    ImportGradesDialog,
    ExportGradesDialog,
    BulkEditGradesDialog,
    GradeDetailsDialog,
    EditGradeDialog,
    GenerateReportDialog,
    AssignmentDetailsDialog,
    SubmitAssignmentDialog,
    ViewSubmissionDialog,
    ResourceDetailsDialog,
    ExportReportCardDialog,
    GradeAnalysisDialog,
    CourseLearningDialog,
    ProfileSettingsDialog,
    SecuritySettingsDialog,
    NotificationSettingsDialog,
    ThemeSettingsDialog,
    BackupSettingsDialog,
    AboutDialog,
    PreferenceSettingsDialog,
    CreateNotificationDialog,
    AnalyticsDashboardFrame
)

__all__ = [
    'CreateClassDialog',
    'CreateCourseDialog',
    'CreateAssignmentDialog',
    'CreatePostDialog',
    'ReplyPostDialog',
    'EditReplyDialog',
    'ClassDetailsDialog',
    'EditClassDialog',
    'ManageStudentsDialog',
    'CourseDetailsDialog',
    'EditCourseDialog',
    'ManageCourseContentDialog',
    'ImportGradesDialog',
    'ExportGradesDialog',
    'BulkEditGradesDialog',
    'GradeDetailsDialog',
    'EditGradeDialog',
    'GenerateReportDialog',
    'AssignmentDetailsDialog',
    'SubmitAssignmentDialog',
    'ViewSubmissionDialog',
    'ResourceDetailsDialog',
    'ExportReportCardDialog',
    'GradeAnalysisDialog',
    'CourseLearningDialog',
    'ProfileSettingsDialog',
    'SecuritySettingsDialog',
    'NotificationSettingsDialog',
    'ThemeSettingsDialog',
    'BackupSettingsDialog',
    'AboutDialog',
    'PreferenceSettingsDialog',
    'CreateNotificationDialog'
]