from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.question import Question
from test import log

class QuestionCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.test_user = User.objects.create_user(username='testuser', password='testpass123')
    
    def setUp(self):
        self.client = Client()
    
    @log
    def test_view_url_exists(self):
        """Test that the URL exists"""
        response = self.client.get('/ask/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login for unauthenticated users
    
    @log
    def test_view_url_accessible_by_name(self):
        """Test that the URL is accessible by name for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ask_question'))
        self.assertEqual(response.status_code, 200)
    
    @log
    def test_login_required(self):
        """Test that login is required to access the create view"""
        response = self.client.get(reverse('ask_question'))
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertTrue(response.url.startswith('/accounts/login/'))  # type: ignore
    
    @log
    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ask_question'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/question_form.html')
    
    @log
    def test_create_question(self):
        """Test that a user can create a question"""
        self.client.login(username='testuser', password='testpass123')
        question_data = {
            'title': 'New Test Question',
            'content': 'Content for the new test question'
        }
        response = self.client.post(reverse('ask_question'), question_data)
        
        # Should redirect to question detail after creation
        self.assertEqual(response.status_code, 302)
        
        # Check that the question was created
        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.first()
        self.assertEqual(new_question.title, 'New Test Question') # type: ignore
        self.assertEqual(new_question.author, self.test_user) # type: ignore
        
        # Check that the search vector was updated
        self.assertIsNotNone(new_question.search_vector) # type: ignore 