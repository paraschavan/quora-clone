from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.question import Question
from core.models.answer import Answer
from test import log

class AnswerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.test_user = User.objects.create_user(username='testuser', password='testpass123')
        cls.test_user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        # Create a question
        cls.test_question = Question.objects.create(
            title='Test Question',
            content='Content for testing answers',
            author=cls.test_user
        )
    
    def setUp(self):
        self.client = Client()
    
    @log
    def test_post_answer(self):
        """Test that a user can post an answer"""
        self.client.login(username='testuser', password='testpass123')
        answer_data = {
            'content': 'This is a test answer'
        }
        response = self.client.post(
            reverse('question_detail', args=[self.test_question.pk]),
            answer_data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to question detail
        self.assertEqual(Answer.objects.count(), 1)
        self.assertEqual(Answer.objects.first().content, 'This is a test answer') # type: ignore
    
    @log
    def test_like_answer(self):
        """Test that a user can like an answer"""
        # Create an answer
        answer = Answer.objects.create(
            content='Test answer',
            question=self.test_question,
            author=self.test_user
        )
        
        # Login as second user and like the answer
        self.client.login(username='testuser2', password='testpass123')
        response = self.client.post(
            reverse('like_answer', args=[answer.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Add this to simulate AJAX request
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(answer.likes.count(), 1)
        self.assertTrue(answer.likes.filter(pk=self.test_user2.pk).exists()) 