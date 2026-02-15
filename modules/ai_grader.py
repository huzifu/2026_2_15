import jieba
import numpy as np
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

class AIGrader:
    @staticmethod
    def grade_objective(student_answer, standard_answer):
        """
        评分客观题 (忽略大小写和首尾空格)
        """
        if not student_answer or not standard_answer:
            return False
        return student_answer.strip().upper() == standard_answer.strip().upper()

    @staticmethod
    def grade_subjective(student_answer, standard_answer, max_score):
        """
        评分主观题
        返回: (score, feedback)
        """
        if not student_answer:
            return 0.0, "未作答"
            
        student_answer = student_answer.strip()
        standard_answer = standard_answer.strip()
        
        # 1. 如果没有安装 sklearn，使用简单的关键词覆盖率
        if not HAS_SKLEARN:
            return AIGrader._grade_feature_overlap(student_answer, standard_answer, max_score)
            
        # 2.如果有 sklearn，使用 TF-IDF 余弦相似度
        try:
            # 分词
            s_cut = " ".join(jieba.cut(student_answer))
            t_cut = " ".join(jieba.cut(standard_answer))
            
            corpus = [s_cut, t_cut]
            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform(corpus)
            
            # 计算相似度
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            
            # 评分策略：相似度 * 满分
            # 简单的线性映射，设定一个阈值
            score = similarity * max_score
            
            feedback = f"AI 相似度评分: {similarity:.2f}"
            return round(score, 1), feedback
            
        except Exception as e:
            print(f"AI Grading Error: {e}")
            return 0.0, "AI 评分失败"

    @staticmethod
    def _grade_feature_overlap(student_answer, standard_answer, max_score):
        """
        基于 Jaccard 相似度的简单评分 (Fallback)
        """
        s_words = set(jieba.cut(student_answer))
        t_words = set(jieba.cut(standard_answer))
        
        if not t_words:
            return 0.0, "标准答案为空"
            
        intersection = s_words & t_words
        union = s_words | t_words
        
        jaccard = len(intersection) / len(union) if union else 0
        
        score = jaccard * max_score
        return round(score, 1), f"关键词覆盖评分: {jaccard:.2f}"
