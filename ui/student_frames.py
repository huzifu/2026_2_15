import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.constants import *
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    pass
from modules.models import Assignment, Question
from modules.ai_grader import AIGrader

class StudentAssignmentListFrame(ttk.Frame):
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
        ttk.Button(toolbar, text="刷新", command=self.load_assignments).pack(side=LEFT)

        # Assignment List
        columns = ("id", "title", "teacher", "deadline", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="标题")
        self.tree.heading("teacher", text="教师")
        self.tree.heading("deadline", text="截止时间")
        self.tree.heading("status", text="状态")
        
        self.tree.column("id", width=50)
        self.tree.column("title", width=250)
        
        self.tree.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_assignments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get all assignments
        # In a real app, join with submission table to check status
        query = """
            SELECT a.*, u.nickname as teacher_name 
            FROM assignment a 
            JOIN user u ON a.teacher_id = u.id 
            ORDER BY a.create_time DESC
        """
        rows = self.db.execute_query(query)
        
        for row in rows:
            # Check if submitted
            sub_query = "SELECT id FROM submission WHERE student_id = ? AND assignment_id = ?"
            sub = self.db.execute_query(sub_query, (self.user.id, row['id']))
            status = "已提交" if sub else "未完成"
            
            self.tree.insert("", END, values=(row['id'], row['title'], row['teacher_name'], row['deadline'], status))

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        assignment_id = values[0]
        status = values[4]
        
        if status == "已提交":
            messagebox.showinfo("提示", "您已经提交过该作业")
            return

        TakingAssignmentDialog(self, assignment_id, self.user, self.db, self.load_assignments)

class TakingAssignmentDialog(tk.Toplevel):
    def __init__(self, parent, assignment_id, user, db_manager, callback):
        super().__init__(parent)
        self.title("答题中...")
        self.geometry("800x600")
        self.assignment_id = assignment_id
        self.user = user
        self.db = db_manager
        self.callback = callback
        self.answers = {} # question_id -> answer
        
        self.create_widgets()
        self.load_questions()
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        # Header
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        # Submit Button Frame (at bottom, outside scroll)
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(side=BOTTOM, fill=X) # This won't work well with pack side LEFT canvas.
        # Fix layout: Main container with Canvas and Bottom Frame
        
    def create_widgets(self):
        # Layout fix
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True)
        
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(side=BOTTOM, fill=X)
        ttk.Button(bottom_frame, text="提交作业", command=self.submit_assignment).pack(side=RIGHT)

        # Scrollable area
        self.canvas = tk.Canvas(main_container)
        self.scrollbar = ttk.Scrollbar(main_container, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Mousewheel
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))


    def load_questions(self):
        query = "SELECT * FROM question WHERE assignment_id = ?"
        rows = self.db.execute_query(query, (self.assignment_id,))
        self.questions = [Question.from_row(row) for row in rows]
        
        row_idx = 0
        for i, q in enumerate(self.questions):
            q_frame = ttk.LabelFrame(self.scrollable_frame, text=f"第 {i+1} 题 ({q.score} 分)", padding=10)
            q_frame.pack(fill=X, expand=True, padx=10, pady=5)
            
            ttk.Label(q_frame, text=q.content, wraplength=700).pack(anchor=W)
            
            answer_var = tk.StringVar()
            self.answers[q.id] = answer_var
            
            if q.type == 'single_choice':
                ttk.Entry(q_frame, textvariable=answer_var).pack(fill=X, pady=5)
                ttk.Label(q_frame, text="请输入选项 (如 A, B)").pack(anchor=W)
            else:
                # Text widget for subjective, need to handle differently as it relies on StringVar
                # For simplicity in this demo, use Entry for short answers or implement custom binding
                # Let's use specific handling
                self.answers[q.id] = ttk.Text(q_frame, height=3)
                self.answers[q.id].pack(fill=X, pady=5)
                
            row_idx += 1


    def submit_assignment(self):
        if not messagebox.askyesno("确认", "确定要提交吗？提交后不可修改。"):
            return

        total_score = 0
        submission_id = self.db.execute_update(
            "INSERT INTO submission (student_id, assignment_id, total_score) VALUES (?, ?, ?)",
            (self.user.id, self.assignment_id, 0) # Score updated later
        )

        # Process answers
        for q in self.questions:
            student_ans = ""
            if isinstance(self.answers[q.id], tk.StringVar):
                student_ans = self.answers[q.id].get().strip()
            else:
                student_ans = self.answers[q.id].get("1.0", END).strip()
            
            is_correct = False
            score = 0
            ai_feedback = ""
            
            # Object Questions
            if q.type == 'single_choice':
                if AIGrader.grade_objective(student_ans, q.answer):
                    is_correct = True
                    score = q.score
            
            # Subjective Questions (AI Grading)
            elif q.type == 'subjective':
                # Use standard answer + analysis as reference
                reference = q.answer + " " + (q.analysis or "")
                score, ai_feedback = AIGrader.grade_subjective(student_ans, reference, q.score)
            
            total_score += score
            
            self.db.execute_update(
                "INSERT INTO submission_detail (submission_id, question_id, student_answer, is_correct, score, ai_feedback) VALUES (?, ?, ?, ?, ?, ?)",
                (submission_id, q.id, student_ans, is_correct, score, ai_feedback)
            )

        # Update total score
        self.db.execute_update("UPDATE submission SET total_score = ? WHERE id = ?", (total_score, submission_id))
        
        messagebox.showinfo("成功", f"提交成功！初步得分: {total_score:.1f}")
        self.callback()
        self.destroy()

class SubmissionHistoryFrame(ttk.Frame):
    def __init__(self, parent, user, db_manager):
        super().__init__(parent)
        self.user = user
        self.db = db_manager
        self.pack(fill=BOTH, expand=True)
        
        columns = ("id", "title", "score", "time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="提交ID")
        self.tree.heading("title", text="作业标题")
        self.tree.heading("score", text="得分")
        self.tree.heading("time", text="提交时间")
        self.tree.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        title = ttk.Label(self, text="历史提交记录", font=("Helvetica", 14))
        title.pack(before=self.tree, pady=10)
        
        self.load_history()
        
    def load_history(self):
        query = """
            SELECT s.id, a.title, s.total_score, s.submit_time 
            FROM submission s
            JOIN assignment a ON s.assignment_id = a.id
            WHERE s.student_id = ?
            ORDER BY s.submit_time DESC
        """
        rows = self.db.execute_query(query, (self.user.id,))
        for row in rows:
            self.tree.insert("", END, values=(row['id'], row['title'], row['total_score'], row['submit_time']))
