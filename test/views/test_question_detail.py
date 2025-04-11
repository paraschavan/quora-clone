from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.question import Question
from core.models.answer import Answer
from test import log

class QuestionDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.test_user = User.objects.create_user(username='testuser', password='testpass123')
        cls.test_user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        # Create a question
        cls.test_question = Question.objects.create(
            title='Detail Test Question',
            content='Content for testing question detail view',
            author=cls.test_user
        )
        
        # Create an answer for this question
        cls.test_answer = Answer.objects.create(
            content='Test answer content',
            question=cls.test_question,
            author=cls.test_user2
        )
    
    def setUp(self):
        self.client = Client()
    
    @log
    def test_view_url_exists(self):
        """Test that the URL exists"""
        response = self.client.get(f'/question/{self.test_question.pk}/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login for unauthenticated users
    
    @log
    def test_view_url_accessible_by_name(self):
        """Test that the URL is accessible by name for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('question_detail', args=[self.test_question.pk]))
        self.assertEqual(response.status_code, 200)
    
    @log
    def test_login_required(self):
        """Test that login is required to access the detail view"""
        response = self.client.get(reverse('question_detail', args=[self.test_question.pk]))
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertTrue(response.url.startswith('/accounts/login/')) # type: ignore
    
    @log
    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('question_detail', args=[self.test_question.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/question_detail.html')
    
    @log
    def test_context_data(self):
        """Test that context contains the question and answer form"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('question_detail', args=[self.test_question.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['question'], self.test_question)
        self.assertTrue('answer_form' in response.context)
    
    @log
    def test_post_answer(self):
        """Test that a user can post an answer"""
        self.client.login(username='testuser', password='testpass123')
        answer_data = {
            'content': 'New test answer from post'
        }
        response = self.client.post(
            reverse('question_detail', args=[self.test_question.pk]),
            answer_data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to question detail
        
        # Check that the answer was created
        self.assertEqual(Answer.objects.filter(question=self.test_question).count(), 2)
        self.assertTrue(Answer.objects.filter(content='New test answer from post').exists()) 