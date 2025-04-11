from django.test import TestCase
from django.contrib.auth.models import User
from core.models.question import Question
from django.db.utils import IntegrityError
from test import log

class QuestionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.test_user = User.objects.create_user(username='testuser', password='testpass123')
        
    @log
    def test_question_creation(self):
        """Test that a question can be created"""
        question = Question.objects.create(
            title="Test Question Title",
            content="This is a test question content",
            author=self.test_user
        )
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(question.title, "Test Question Title")
        self.assertEqual(question.author, self.test_user)
        
    @log
    def test_question_string_representation(self):
        """Test the string representation of a question"""
        question = Question.objects.create(
            title="Test Question",
            content="Content",
            author=self.test_user
        )
        self.assertEqual(str(question), "Test Question")
        
    @log
    def test_question_ordering(self):
        """Test that questions are ordered by created_at in descending order"""
        question1 = Question.objects.create(title="First Question", content="Content", author=self.test_user)
        question2 = Question.objects.create(title="Second Question", content="Content", author=self.test_user)
        
        # Get all questions and check the order
        questions = Question.objects.all()
        self.assertEqual(questions[0], question2)  # Newest should be first
        self.assertEqual(questions[1], question1)
        
    @log
    def test_get_absolute_url(self):
        """Test the get_absolute_url method"""
        question = Question.objects.create(
            title="URL Test",
            content="Testing URL",
            author=self.test_user
        )
        self.assertEqual(question.get_absolute_url(), f'/question/{question.pk}/') 