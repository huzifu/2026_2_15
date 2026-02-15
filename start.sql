-- 智能教学管理系统 数据库初始化脚本
-- 数据库类型: SQLite

-- 1. 用户表 (User) - 扩展
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('teacher', 'student', 'admin', 'assistant')),
    nickname TEXT,
    email TEXT,
    phone TEXT,
    avatar TEXT,
    bio TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended')),
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 班级表 (Class)
CREATE TABLE IF NOT EXISTS class (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT UNIQUE,
    description TEXT,
    teacher_id INTEGER NOT NULL,
    max_students INTEGER DEFAULT 50,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'closed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES user(id)
);

-- 3. 班级成员表 (ClassMember)
CREATE TABLE IF NOT EXISTS class_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'left', 'removed')),
    FOREIGN KEY (class_id) REFERENCES class(id),
    FOREIGN KEY (student_id) REFERENCES user(id),
    UNIQUE(class_id, student_id)
);

-- 4. 课程表 (Course)
CREATE TABLE IF NOT EXISTS course (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    teacher_id INTEGER NOT NULL,
    class_id INTEGER,
    cover_image TEXT,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES user(id),
    FOREIGN KEY (class_id) REFERENCES class(id)
);

-- 5. 章节表 (Chapter)
CREATE TABLE IF NOT EXISTS chapter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE
);

-- 6. 课程内容表 (CourseContent)
CREATE TABLE IF NOT EXISTS course_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK(content_type IN ('text', 'video', 'audio', 'document', 'quiz', 'assignment')),
    content TEXT,
    file_path TEXT,
    duration INTEGER, -- 视频/音频时长（秒）
    order_index INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapter(id) ON DELETE CASCADE
);

-- 7. 作业表 (Assignment) - 扩展
CREATE TABLE IF NOT EXISTS assignment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    course_id INTEGER,
    chapter_id INTEGER,
    teacher_id INTEGER NOT NULL,
    type TEXT DEFAULT 'homework' CHECK(type IN ('homework', 'quiz', 'exam', 'project')),
    total_score REAL DEFAULT 100,
    deadline DATETIME,
    time_limit INTEGER, -- 时间限制（分钟）
    allow_late_submission BOOLEAN DEFAULT FALSE,
    late_penalty REAL DEFAULT 0, -- 迟交扣分比例
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'closed', 'graded')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (chapter_id) REFERENCES chapter(id),
    FOREIGN KEY (teacher_id) REFERENCES user(id)
);

-- 8. 题目表 (Question) - 扩展
CREATE TABLE IF NOT EXISTS question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('single_choice', 'multi_choice', 'true_false', 'fill_in', 'short_answer', 'essay', 'code', 'file_upload')),
    content TEXT NOT NULL,
    options TEXT, -- JSON格式存储选项
    answer TEXT,
    score REAL DEFAULT 0,
    difficulty TEXT DEFAULT 'medium' CHECK(difficulty IN ('easy', 'medium', 'hard')),
    tags TEXT, -- 标签，逗号分隔
    analysis TEXT,
    hint TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignment(id) ON DELETE CASCADE
);

-- 9. 提交记录表 (Submission) - 扩展
CREATE TABLE IF NOT EXISTS submission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    total_score REAL,
    grade TEXT, -- 等级 A/B/C/D/F
    feedback TEXT,
    submit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    late_submission BOOLEAN DEFAULT FALSE,
    grading_status TEXT DEFAULT 'pending' CHECK(grading_status IN ('pending', 'graded', 'reviewing', 'rejected')),
    graded_by INTEGER,
    graded_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (assignment_id) REFERENCES assignment(id),
    FOREIGN KEY (graded_by) REFERENCES user(id)
);

-- 10. 提交详情表 (SubmissionDetail)
CREATE TABLE IF NOT EXISTS submission_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    student_answer TEXT,
    attachments TEXT, -- JSON格式存储附件信息
    is_correct BOOLEAN,
    score REAL,
    ai_feedback TEXT,
    teacher_feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submission(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES question(id)
);

-- 11. 讨论区表 (Discussion)
CREATE TABLE IF NOT EXISTS discussion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    assignment_id INTEGER,
    user_id INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    parent_id INTEGER, -- 回复的父帖子ID
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'closed', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (assignment_id) REFERENCES assignment(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (parent_id) REFERENCES discussion(id)
);

-- 12. 通知表 (Notification)
CREATE TABLE IF NOT EXISTS notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('assignment', 'grade', 'discussion', 'system', 'reminder')),
    title TEXT NOT NULL,
    content TEXT,
    related_id INTEGER, -- 相关实体ID
    related_type TEXT, -- 相关实体类型
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- 13. 学习进度表 (LearningProgress)
CREATE TABLE IF NOT EXISTS learning_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    chapter_id INTEGER,
    content_id INTEGER,
    progress REAL DEFAULT 0, -- 进度百分比
    status TEXT DEFAULT 'in_progress' CHECK(status IN ('not_started', 'in_progress', 'completed', 'reviewing')),
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    time_spent INTEGER DEFAULT 0, -- 学习时长（秒）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (chapter_id) REFERENCES chapter(id),
    FOREIGN KEY (content_id) REFERENCES course_content(id),
    UNIQUE(student_id, content_id)
);

-- 14. 成绩表 (Gradebook)
CREATE TABLE IF NOT EXISTS gradebook (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    assignment_id INTEGER,
    score REAL,
    grade TEXT,
    weight REAL DEFAULT 1.0, -- 权重
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (assignment_id) REFERENCES assignment(id),
    UNIQUE(student_id, assignment_id)
);

-- 15. 资源表 (Resource)
CREATE TABLE IF NOT EXISTS resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    file_type TEXT,
    file_size INTEGER,
    uploader_id INTEGER NOT NULL,
    course_id INTEGER,
    assignment_id INTEGER,
    tags TEXT,
    download_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploader_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (assignment_id) REFERENCES assignment(id)
);

-- 16. 消息表 (Message)
CREATE TABLE IF NOT EXISTS message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user(id),
    FOREIGN KEY (receiver_id) REFERENCES user(id)
);

-- 17. 系统设置表 (SystemSetting)
CREATE TABLE IF NOT EXISTS system_setting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 18. 活动日志表 (ActivityLog)
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    details TEXT,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- 插入默认管理员账号
INSERT OR IGNORE INTO user (username, password, role, nickname, email, status) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', '系统管理员', 'admin@example.com', 'active');

-- 插入测试教师账号
INSERT OR IGNORE INTO user (username, password, role, nickname, email, status) 
VALUES ('teacher1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'teacher', '张老师', 'teacher1@example.com', 'active');

INSERT OR IGNORE INTO user (username, password, role, nickname, email, status) 
VALUES ('teacher2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'teacher', '王老师', 'teacher2@example.com', 'active');

-- 插入测试学生账号
INSERT OR IGNORE INTO user (username, password, role, nickname, email, status) 
VALUES ('student1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'student', '李同学', 'student1@example.com', 'active');

INSERT OR IGNORE INTO user (username, password, role, nickname, email, status) 
VALUES ('student2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'student', '张同学', 'student2@example.com', 'active');

INSERT OR IGNORE INTO user (username, password, role, nickname, email, status) 
VALUES ('student3', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'student', '王同学', 'student3@example.com', 'active');

-- 插入系统设置
INSERT OR IGNORE INTO system_setting (key, value, description) VALUES
('site_name', '智能教学管理系统', '网站名称'),
('site_description', '一个功能强大的在线教学平台', '网站描述'),
('allow_registration', 'true', '是否允许注册'),
('default_user_role', 'student', '默认用户角色'),
('max_file_size', '10485760', '最大文件大小（字节）'),
('allowed_file_types', 'pdf,doc,docx,ppt,pptx,xls,xlsx,jpg,jpeg,png,gif,mp4,mp3,zip', '允许上传的文件类型'),
('grade_scale', 'A:90-100,B:80-89,C:70-79,D:60-69,F:0-59', '成绩等级标准'),
('late_submission_penalty', '0.1', '迟交扣分比例'),
('ai_grading_enabled', 'true', '是否启用AI评分'),
('notification_enabled', 'true', '是否启用通知');

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);
CREATE INDEX IF NOT EXISTS idx_user_role ON user(role);
CREATE INDEX IF NOT EXISTS idx_class_teacher ON class(teacher_id);
CREATE INDEX IF NOT EXISTS idx_class_member_class ON class_member(class_id);
CREATE INDEX IF NOT EXISTS idx_class_member_student ON class_member(student_id);
CREATE INDEX IF NOT EXISTS idx_assignment_course ON assignment(course_id);
CREATE INDEX IF NOT EXISTS idx_assignment_teacher ON assignment(teacher_id);
CREATE INDEX IF NOT EXISTS idx_submission_student ON submission(student_id);
CREATE INDEX IF NOT EXISTS idx_submission_assignment ON submission(assignment_id);
CREATE INDEX IF NOT EXISTS idx_discussion_course ON discussion(course_id);
CREATE INDEX IF NOT EXISTS idx_notification_user ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_progress_student ON learning_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_gradebook_student ON gradebook(student_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
