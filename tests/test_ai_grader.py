"""
AI评分模块测试
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.ai_grader import AIGrader

class TestAIGrader(unittest.TestCase):
    def test_grade_objective_correct(self):
        """测试客观题评分 - 正确答案"""
        result = AIGrader.grade_objective("A", "A")
        self.assertTrue(result)
        
        # 忽略大小写
        result = AIGrader.grade_objective("a", "A")
        self.assertTrue(result)
        
        # 忽略空格
        result = AIGrader.grade_objective(" A ", "A")
        self.assertTrue(result)

    def test_grade_objective_incorrect(self):
        """测试客观题评分 - 错误答案"""
        result = AIGrader.grade_objective("A", "B")
        self.assertFalse(result)

    def test_grade_subjective(self):
        """测试主观题评分"""
        student_answer = "Python是一种高级编程语言"
        standard_answer = "Python是一种解释型的高级编程语言"
        max_score = 10
        
        score, feedback = AIGrader.grade_subjective(student_answer, standard_answer, max_score)
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, max_score)
        self.assertIsNotNone(feedback)

    def test_grade_subjective_empty(self):
        """测试主观题评分 - 空答案"""
        score, feedback = AIGrader.grade_subjective("", "标准答案", 10)
        self.assertEqual(score, 0)
        self.assertEqual(feedback, "未作答")

if __name__ == '__main__':
    unittest.main()
