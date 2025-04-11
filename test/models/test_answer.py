from django.test import TestCase
from django.contrib.auth.models import User
from core.models.question import Question
from core.models.answer import Answer
from test import log

class AnswerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.test_user = User.objects.create_user(username='testuser', password='testpass123')
        # Create a second user for testing likes
        cls.test_user2 = User.objects.create_user(username='testuser2', password='testpass123')
        # Create a question
        cls.test_question = Question.objects.create(
            title="Test Question", 
            content="Content",
            author=cls.test_user
        )
        
    @log
    def test_answer_creation(self):
        """Test that an answer can be created"""
        answer = Answer.objects.create(
            content="This is a test answer",
            question=self.test_question,
            author=self.test_user
        )
        self.assertEqual(Answer.objects.count(), 1)
        self.assertEqual(answer.content, "This is a test answer")
        self.assertEqual(answer.question, self.test_question)
        self.assertEqual(answer.author, self.test_user)
        
    @log
    def test_answer_string_representation(self):
        """Test the string representation of an answer"""
        answer = Answer.objects.create(
            content="Test Answer",
            question=self.test_question,
            author=self.test_user
        )
        expected_str = f"Answer by {self.test_user.username} on {self.test_question.title}"
        self.assertEqual(str(answer), expected_str)
        
    @log
    def test_answer_ordering(self):
        """Test that answers are ordered by created_at in descending order"""
        answer1 = Answer.objects.create(content="First Answer", question=self.test_question, author=self.test_user)
        answer2 = Answer.objects.create(content="Second Answer", question=self.test_question, author=self.test_user)
        
        # Get all answers and check the order
        answers = Answer.objects.all()
        self.assertEqual(answers[0], answer2)  # Newest should be first
        self.assertEqual(answers[1], answer1)
    
    @log
    def test_answer_likes(self):
        """Test that users can like answers"""
        answer = Answer.objects.create(
            content="Likeable Answer",
            question=self.test_question,
            author=self.test_user
        )
        
        # Test like functionality
        answer.likes.add(self.test_user2)
        self.assertEqual(answer.likes.count(), 1)
        self.assertTrue(answer.likes.filter(pk=self.test_user2.pk).exists())
        
        # Test total_likes method
        self.assertEqual(answer.total_likes(), 1)
        
        # Test removing a like
        answer.likes.remove(self.test_user2)
        self.assertEqual(answer.likes.count(), 0) 