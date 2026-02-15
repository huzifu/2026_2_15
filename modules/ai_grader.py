import jieba
import logging
from config import AI_SIMILARITY_THRESHOLD, AI_MIN_SCORE_RATIO

logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("sklearn not installed, using fallback grading method")

class AIGrader:
    @staticmethod
    def grade_objective(student_answer, standard_answer):
        """
        评分客观题 (忽略大小写和首尾空格)
        """
        if not student_answer or not standard_answer:
            return False
        
        # 标准化答案
        student = student_answer.strip().upper().replace(" ", "")
        standard = standard_answer.strip().upper().replace(" ", "")
        
        return student == standard

    @staticmethod
    def grade_subjective(student_answer, standard_answer, max_score):
        """
        评分主观题
        返回: (score, feedback)
        """
        if not student_answer or not student_answer.strip():
            return 0.0, "未作答"
        
        if not standard_answer or not standard_answer.strip():
            return max_score * 0.5, "标准答案为空，给予基础分"
            
        student_answer = student_answer.strip()
        standard_answer = standard_answer.strip()
        
        # 1. 如果没有安装 sklearn，使用简单的关键词覆盖率
        if not HAS_SKLEARN:
            return AIGrader._grade_feature_overlap(student_answer, standard_answer, max_score)
            
        # 2. 如果有 sklearn，使用 TF-IDF 余弦相似度
        try:
            # 分词
            s_cut = " ".join(jieba.cut(student_answer))
            t_cut = " ".join(jieba.cut(standard_answer))
            
            corpus = [s_cut, t_cut]
            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform(corpus)
            
            # 计算相似度
            similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            
            # 评分策略：相似度 * 满分，但设置最低分
            # 如果相似度过低，给予最低分
            if similarity < AI_MIN_SCORE_RATIO:
                score = max_score * AI_MIN_SCORE_RATIO
                feedback = f"AI评分: 相似度较低 ({similarity:.2%}), 给予基础分"
            else:
                score = similarity * max_score
                feedback = f"AI评分: 相似度 {similarity:.2%}"
            
            # 根据相似度给出建议
            if similarity >= 0.8:
                feedback += " - 优秀"
            elif similarity >= 0.6:
                feedback += " - 良好"
            elif similarity >= 0.4:
                feedback += " - 及格"
            else:
                feedback += " - 需改进"
            
            logger.info(f"Subjective grading: similarity={similarity:.2f}, score={score:.1f}/{max_score}")
            return round(score, 1), feedback
            
        except Exception as e:
            logger.error(f"AI Grading Error: {e}")
            return max_score * 0.3, "AI评分失败，给予基础分"

    @staticmethod
    def _grade_feature_overlap(student_answer, standard_answer, max_score):
        """
        基于 Jaccard 相似度的简单评分 (Fallback)
        """
        try:
            s_words = set(jieba.cut(student_answer))
            t_words = set(jieba.cut(standard_answer))
            
            # 移除停用词（简单版本）
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个'}
            s_words = s_words - stop_words
            t_words = t_words - stop_words
            
            if not t_words:
                return max_score * 0.5, "标准答案分词为空，给予基础分"
                
            intersection = s_words & t_words
            union = s_words | t_words
            
            jaccard = len(intersection) / len(union) if union else 0
            
            # 设置最低分
            if jaccard < AI_MIN_SCORE_RATIO:
                score = max_score * AI_MIN_SCORE_RATIO
                feedback = f"关键词覆盖率较低 ({jaccard:.2%}), 给予基础分"
            else:
                score = jaccard * max_score
                feedback = f"关键词覆盖率: {jaccard:.2%}"
            
            logger.info(f"Fallback grading: jaccard={jaccard:.2f}, score={score:.1f}/{max_score}")
            return round(score, 1), feedback
            
        except Exception as e:
            logger.error(f"Fallback grading error: {e}")
            return max_score * 0.3, "评分失败，给予基础分"

    @staticmethod
    def batch_grade(questions, answers):
        """
        批量评分
        questions: list of Question objects
        answers: dict {question_id: student_answer}
        返回: list of (score, is_correct, feedback)
        """
        results = []
        for question in questions:
            student_answer = answers.get(question.id, "")
            
            if question.type in ['single_choice', 'multi_choice', 'boolean', 'fill_in']:
                is_correct = AIGrader.grade_objective(student_answer, question.answer)
                score = question.score if is_correct else 0
                feedback = "正确" if is_correct else "错误"
            elif question.type == 'subjective':
                score, feedback = AIGrader.grade_subjective(
                    student_answer, question.answer, question.score
                )
                is_correct = None
            else:
                score, is_correct, feedback = 0, False, "未知题型"
            
            results.append((score, is_correct, feedback))
        
        return results
