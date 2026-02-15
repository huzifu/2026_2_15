-- AI 智能教学助手系统 数据库初始化脚本
-- 数据库类型: SQLite

-- 1. 用户表 (User)
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- 用户ID
    username TEXT NOT NULL UNIQUE,        -- 用户名 (唯一)
    password TEXT NOT NULL,               -- 密码 (加密存储)
    role TEXT NOT NULL CHECK(role IN ('teacher', 'student', 'admin')), -- 角色
    nickname TEXT,                        -- 昵称
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- 创建时间
);

-- 2. 作业表 (Assignment)
CREATE TABLE IF NOT EXISTS assignment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                  -- 作业标题
    description TEXT,                     -- 作业描述
    teacher_id INTEGER NOT NULL,          -- 发布教师ID
    deadline DATETIME,                    -- 截止时间
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES user(id)
);

-- 3. 题目表 (Question)
CREATE TABLE IF NOT EXISTS question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,       -- 所属作业ID
    type TEXT NOT NULL CHECK(type IN ('single_choice', 'multi_choice', 'boolean', 'fill_in', 'subjective')), -- 题目类型
    content TEXT NOT NULL,                -- 题目内容 (支持JSON格式存储选项)
    answer TEXT,                          -- 标准答案
    score REAL DEFAULT 0,                 -- 分值
    analysis TEXT,                        -- 题目解析
    FOREIGN KEY (assignment_id) REFERENCES assignment(id) ON DELETE CASCADE
);

-- 4. 提交记录表 (Submission)
CREATE TABLE IF NOT EXISTS submission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,          -- 学生ID
    assignment_id INTEGER NOT NULL,       -- 作业ID
    total_score REAL,                     -- 总得分
    feedback TEXT,                        -- 总体评语
    submit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (assignment_id) REFERENCES assignment(id)
);

-- 5. 提交详情表 (SubmissionDetail) - 用于存储每道题的作答情况
CREATE TABLE IF NOT EXISTS submission_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,       -- 提交记录ID
    question_id INTEGER NOT NULL,         -- 题目ID
    student_answer TEXT,                  -- 学生作答
    is_correct BOOLEAN,                   -- 是否正确 (客观题)
    score REAL,                           -- 该题得分
    ai_feedback TEXT,                     -- AI 评分建议/评语
    FOREIGN KEY (submission_id) REFERENCES submission(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES question(id)
);

-- 插入默认管理员账号 (密码: admin123, 实际使用时请加密)
INSERT OR IGNORE INTO user (username, password, role, nickname) 
VALUES ('admin', 'admin123', 'admin', '系统管理员');

-- 插入测试教师账号
INSERT OR IGNORE INTO user (username, password, role, nickname) 
VALUES ('teacher1', '123456', 'teacher', '张老师');

-- 插入测试学生账号
INSERT OR IGNORE INTO user (username, password, role, nickname) 
VALUES ('student1', '123456', 'student', '李同学');
