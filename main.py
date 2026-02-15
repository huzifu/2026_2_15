"""
智能教学管理系统 - 主程序
"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 尝试导入 ttkbootstrap，如果不存在则回退到标准 tkinter
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from config import WINDOW_TITLE, WINDOW_SIZE, THEME_NAME, APP_NAME, APP_VERSION
from modules.db_manager import DBManager
from modules.auth import AuthManager
from modules.logger import setup_logger

# 配置日志
logger = setup_logger(__name__)

class App(ttk.Window if HAS_TTKBOOTSTRAP else tk.Tk):
    def __init__(self):
        try:
            if HAS_TTKBOOTSTRAP:
                super().__init__(themename=THEME_NAME)
            else:
                super().__init__()
                logger.warning("ttkbootstrap not installed, using standard tkinter")
            
            self.title(f"{WINDOW_TITLE} v{APP_VERSION}")
            self.geometry(WINDOW_SIZE)
            self.minsize(1024, 768)
            
            # 设置窗口图标
            self.set_window_icon()
            
            # 初始化数据库和认证管理
            self.db = DBManager()
            self.auth_manager = AuthManager(self.db)
            
            # 初始化服务
            self.init_services()
            
            self.current_frame = None
            self.show_splash_screen()
            
            logger.info(f"{APP_NAME} v{APP_VERSION} started successfully")
            
        except Exception as e:
            logger.error(f"Application initialization failed: {e}", exc_info=True)
            self.show_error_dialog("系统初始化失败", str(e))
            raise

    def set_window_icon(self):
        """设置窗口图标"""
        try:
            # 尝试加载图标文件
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass  # 图标文件不存在也没关系

    def init_services(self):
        """初始化服务模块"""
        try:
            # 导入服务模块
            from modules.class_service import ClassService
            from modules.course_service import CourseService
            from modules.assignment_service import AssignmentService
            from modules.submission_service import SubmissionService
            from modules.discussion_service import DiscussionService
            from modules.notification_service import NotificationService
            from modules.gradebook_service import GradebookService
            from modules.analytics_service import AnalyticsService
            
            # 初始化服务实例
            self.class_service = ClassService(self.db)
            self.course_service = CourseService(self.db)
            self.assignment_service = AssignmentService(self.db)
            self.submission_service = SubmissionService(self.db)
            self.discussion_service = DiscussionService(self.db)
            self.notification_service = NotificationService(self.db)
            self.gradebook_service = GradebookService(self.db)
            self.analytics_service = AnalyticsService(self.db)
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}", exc_info=True)
            raise

    def show_splash_screen(self):
        """显示启动画面"""
        splash = tk.Toplevel(self)
        splash.title("正在启动...")
        splash.geometry("400x300")
        splash.overrideredirect(True)  # 无边框
        
        # 居中显示
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        splash.geometry(f"400x300+{x}+{y}")
        
        # 添加内容
        title_label = ttk.Label(splash, text=APP_NAME, font=("Helvetica", 24, "bold"))
        title_label.pack(pady=50)
        
        version_label = ttk.Label(splash, text=f"版本 {APP_VERSION}")
        version_label.pack()
        
        loading_label = ttk.Label(splash, text="正在加载系统...")
        loading_label.pack(pady=20)
        
        # 进度条
        progress = ttk.Progressbar(splash, mode='indeterminate', length=200)
        progress.pack(pady=10)
        progress.start(10)
        
        # 更新窗口
        splash.update()
        
        # 延迟后关闭启动画面并显示登录界面
        self.after(1500, lambda: self.close_splash_and_login(splash))

    def close_splash_and_login(self, splash):
        """关闭启动画面并显示登录界面"""
        splash.destroy()
        self.show_login()

    def show_login(self):
        """显示登录界面"""
        if self.current_frame:
            self.current_frame.destroy()
        
        from ui.login_frame import LoginFrame
        self.current_frame = LoginFrame(self, self.auth_manager, self.on_login_success)
        self.current_frame.pack(fill=BOTH, expand=True)

    def on_login_success(self, user):
        """登录成功回调"""
        logger.info(f"User logged in: {user.username} ({user.role})")
        
        # 发送欢迎通知
        try:
            self.notification_service.send_welcome_notification(user.id)
        except Exception as e:
            logger.warning(f"Failed to send welcome notification: {e}")
        
        if self.current_frame:
            self.current_frame.destroy()
        
        # 根据角色显示不同的主界面
        if user.role == 'teacher':
            self.show_teacher_dashboard()
        elif user.role == 'student':
            self.show_student_dashboard()
        elif user.role == 'admin':
            self.show_admin_dashboard()
        elif user.role == 'assistant':
            self.show_assistant_dashboard()

    def show_teacher_dashboard(self):
        """显示教师仪表板"""
        from ui.teacher_dashboard import TeacherDashboard
        self.current_frame = TeacherDashboard(
            self, 
            self.auth_manager.current_user, 
            self.db,
            self.class_service,
            self.course_service,
            self.assignment_service,
            self.submission_service,
            self.discussion_service,
            self.notification_service,
            self.gradebook_service,
            self.analytics_service,
            self.logout
        )
        self.current_frame.pack(fill=BOTH, expand=True)

    def show_student_dashboard(self):
        """显示学生仪表板"""
        from ui.student_dashboard import StudentDashboard
        self.current_frame = StudentDashboard(
            self,
            self.auth_manager.current_user,
            self.db,
            self.class_service,
            self.course_service,
            self.assignment_service,
            self.submission_service,
            self.discussion_service,
            self.notification_service,
            self.gradebook_service,
            self.analytics_service,
            self.logout
        )
        self.current_frame.pack(fill=BOTH, expand=True)

    def show_admin_dashboard(self):
        """显示管理员仪表板"""
        from ui.admin_dashboard import AdminDashboard
        self.current_frame = AdminDashboard(
            self,
            self.auth_manager.current_user,
            self.db,
            self.logout
        )
        self.current_frame.pack(fill=BOTH, expand=True)

    def show_assistant_dashboard(self):
        """显示助教仪表板"""
        from ui.assistant_dashboard import AssistantDashboard
        self.current_frame = AssistantDashboard(
            self,
            self.auth_manager.current_user,
            self.db,
            self.class_service,
            self.course_service,
            self.assignment_service,
            self.submission_service,
            self.discussion_service,
            self.notification_service,
            self.gradebook_service,
            self.analytics_service,
            self.logout
        )
        self.current_frame.pack(fill=BOTH, expand=True)

    def logout(self):
        """退出登录"""
        if self.auth_manager.current_user:
            logger.info(f"User logged out: {self.auth_manager.current_user.username}")
            self.auth_manager.logout()
        
        # 清除当前界面
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
        
        # 显示登录界面
        self.show_login()

    def show_error_dialog(self, title, message):
        """显示错误对话框"""
        from tkinter import messagebox
        messagebox.showerror(title, message)

    def show_info_dialog(self, title, message):
        """显示信息对话框"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)

    def show_warning_dialog(self, title, message):
        """显示警告对话框"""
        from tkinter import messagebox
        messagebox.showwarning(title, message)

    def confirm_dialog(self, title, message):
        """显示确认对话框"""
        from tkinter import messagebox
        return messagebox.askyesno(title, message)

def main():
    """主函数"""
    try:
        app = App()
        
        # 绑定关闭事件
        def on_closing():
            if app.confirm_dialog("确认退出", "确定要退出系统吗？"):
                logger.info("Application closed by user")
                app.destroy()
        
        app.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 启动主循环
        app.mainloop()
        
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        
        # 显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            from tkinter import messagebox
            messagebox.showerror("系统错误", f"程序发生严重错误：\n{str(e)}\n\n请查看日志文件获取详细信息。")
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
