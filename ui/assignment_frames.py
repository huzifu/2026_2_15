import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass
from modules.models import Assignment

class AssignmentManagerFrame(ttk.Frame):
    def __init__(self, parent, user, db_manager):
        super().__init__(parent)
        self.user = user
        self.db = db_manager
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()
        self.load_assignments()

    def create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill=X)
        ttk.Button(toolbar, text="新建作业", command=self.create_assignment, bootstyle="success").pack(side=LEFT)
        ttk.Button(toolbar, text="刷新", command=self.load_assignments, bootstyle="info-outline").pack(side=LEFT, padx=5)

        # Assignment List
        columns = ("id", "title", "deadline", "create_time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="标题")
        self.tree.heading("deadline", text="截止时间")
        self.tree.heading("create_time", text="创建时间")
        
        self.tree.column("id", width=50)
        self.tree.column("title", width=300)
        
        self.tree.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_assignments(self):
        # Cleaner way to clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        query = "SELECT * FROM assignment WHERE teacher_id = ? ORDER BY create_time DESC"
        rows = self.db.execute_query(query, (self.user.id,))
        for row in rows:
            assign = Assignment.from_row(row)
            self.tree.insert("", END, values=(assign.id, assign.title, assign.deadline, assign.create_time))

    def create_assignment(self):
        CreateAssignmentDialog(self, self.user, self.db, self.load_assignments)

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        assignment_id = values[0]
        # Open Assignment Editor/Details
        AssignmentEditorDialog(self, assignment_id, self.db)


class CreateAssignmentDialog(tk.Toplevel):
    def __init__(self, parent, user, db_manager, callback):
        super().__init__(parent)
        self.title("新建作业")
        self.geometry("400x300")
        self.user = user
        self.db = db_manager
        self.callback = callback
        
        self.create_widgets()
        
        # Center dialog
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        padding = 10
        ttk.Label(self, text="作业标题:").pack(fill=X, padx=padding, pady=(padding, 2))
        self.title_entry = ttk.Entry(self)
        self.title_entry.pack(fill=X, padx=padding, pady=2)

        ttk.Label(self, text="作业描述:").pack(fill=X, padx=padding, pady=(padding, 2))
        self.desc_entry = ttk.Text(self, height=5)
        self.desc_entry.pack(fill=X, padx=padding, pady=2)

        ttk.Label(self, text="截止时间 (YYYY-MM-DD HH:MM):").pack(fill=X, padx=padding, pady=(padding, 2))
        self.deadline_entry = ttk.Entry(self)
        self.deadline_entry.pack(fill=X, padx=padding, pady=2)
        # Set default deadline (e.g., 7 days from now)
        # For simplicity, leave empty for now or use placeholder

        ttk.Button(self, text="创建", command=self.save, bootstyle="primary").pack(pady=20)

    def save(self):
        title = self.title_entry.get()
        description = self.desc_entry.get("1.0", END).strip()
        deadline = self.deadline_entry.get()
        
        if not title:
            messagebox.showwarning("提示", "标题不能为空")
            return

        query = "INSERT INTO assignment (title, description, teacher_id, deadline) VALUES (?, ?, ?, ?)"
        try:
            self.db.execute_update(query, (title, description, self.user.id, deadline))
            messagebox.showinfo("成功", "作业创建成功")
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"创建失败: {e}")

class AssignmentEditorDialog(tk.Toplevel):
    def __init__(self, parent, assignment_id, db_manager):
        super().__init__(parent)
        self.title("作业详情 & 题目管理")
        self.geometry("800x600")
        self.assignment_id = assignment_id
        self.db = db_manager
        
        self.create_widgets()
        self.load_questions()
        
    def create_widgets(self):
        # Header Info
        info_frame = ttk.LabelFrame(self, text="基本信息", padding=10)
        info_frame.pack(fill=X, padx=10, pady=5)
        
        # Fetch assignment details
        query = "SELECT * FROM assignment WHERE id = ?"
        row = self.db.execute_query(query, (self.assignment_id,))
        if row:
            self.assignment = Assignment.from_row(row[0])
            ttk.Label(info_frame, text=f"标题: {self.assignment.title}").pack(anchor=W)
            ttk.Label(info_frame, text=f"描述: {self.assignment.description}").pack(anchor=W)
        
        # Questions List
        list_frame = ttk.LabelFrame(self, text="题目列表", padding=5)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill=X)
        ttk.Button(toolbar, text="添加单选题", command=lambda: self.add_question("single_choice")).pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="添加主观题", command=lambda: self.add_question("subjective")).pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="删除题目", command=self.delete_question, bootstyle="danger").pack(side=RIGHT)

        columns = ("id", "type", "content", "score")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="类型")
        self.tree.heading("content", text="内容")
        self.tree.heading("score", text="分值")
        
        self.tree.column("id", width=50)
        self.tree.column("type", width=100)
        
        self.tree.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def load_questions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        query = "SELECT * FROM question WHERE assignment_id = ?"
        rows = self.db.execute_query(query, (self.assignment_id,))
        for row in rows:
            self.tree.insert("", END, values=(row['id'], row['type'], row['content'][:50]+"...", row['score']))

    def add_question(self, q_type):
        AddQuestionDialog(self, self.assignment_id, q_type, self.db, self.load_questions)

    def delete_question(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要删除的题目")
            return
            
        if not messagebox.askyesno("确认", "确定要删除选中的题目吗？"):
            return

        item = selected[0]
        q_id = self.tree.item(item, "values")[0]
        
        query = "DELETE FROM question WHERE id = ?"
        self.db.execute_update(query, (q_id,))
        self.load_questions()

class AddQuestionDialog(tk.Toplevel):
    def __init__(self, parent, assignment_id, q_type, db_manager, callback):
        super().__init__(parent)
        self.title(f"添加题目 - {q_type}")
        self.geometry("500x400")
        self.assignment_id = assignment_id
        self.q_type = q_type
        self.db = db_manager
        self.callback = callback
        
        self.create_widgets()
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        padding = 10
        
        ttk.Label(self, text="题目内容:").pack(fill=X, padx=padding)
        self.content_text = ttk.Text(self, height=4)
        self.content_text.pack(fill=X, padx=padding, pady=5)
        
        ttk.Label(self, text="标准答案:").pack(fill=X, padx=padding)
        self.answer_text = ttk.Entry(self) if self.q_type == 'single_choice' else ttk.Text(self, height=3)
        self.answer_text.pack(fill=X, padx=padding, pady=5)
        if self.q_type == 'single_choice':
            ttk.Label(self, text="(请输入选项，例如 A)").pack(anchor=W, padx=padding)
        
        # New Field: Analysis / Keywords for AI
        ttk.Label(self, text="题目解析/评分参考(AI用于主观题评分):").pack(fill=X, padx=padding)
        self.analysis_text = ttk.Text(self, height=3)
        self.analysis_text.pack(fill=X, padx=padding, pady=5)

        ttk.Label(self, text="分值:").pack(fill=X, padx=padding)
        self.score_entry = ttk.Entry(self)
        self.score_entry.pack(fill=X, padx=padding, pady=5)
        self.score_entry.insert(0, "10")

        ttk.Button(self, text="保存", command=self.save, bootstyle="primary").pack(pady=20)

    def save(self):
        content = self.content_text.get("1.0", END).strip()
        if self.q_type == 'single_choice':
             answer = self.answer_text.get().strip()
        else:
             answer = self.answer_text.get("1.0", END).strip()
             
        analysis = self.analysis_text.get("1.0", END).strip()
        score = self.score_entry.get().strip()
        
        if not content:
            messagebox.showwarning("提示", "内容不能为空")
            return
            
        try:
            score = float(score)
        except ValueError:
             messagebox.showwarning("提示", "分值必须是数字")
             return

        query = "INSERT INTO question (assignment_id, type, content, answer, score, analysis) VALUES (?, ?, ?, ?, ?, ?)"
        try:
            self.db.execute_update(query, (self.assignment_id, self.q_type, content, answer, score, analysis))
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {e}")
