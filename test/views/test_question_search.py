from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.question import Question
from django.contrib.postgres.search import SearchVector
from test import log

class QuestionSearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.test_user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create some questions with different content
        cls.question1 = Question.objects.create(
            title='Python Programming',
            content='Python is a versatile programming language',
            author=cls.test_user
        )
        cls.question2 = Question.objects.create(
            title='Django Framework',
            content='Django is a high-level Python web framework',
            author=cls.test_user
        )
        cls.question3 = Question.objects.create(
            title='JavaScript Basics',
            content='JavaScript is a scripting language',
            author=cls.test_user
        )
        
        # Update search vectors
        for question in Question.objects.all():
            vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
            Question.objects.filter(pk=question.pk).update(search_vector=vector)
    
    def setUp(self):
        self.client = Client()
        # Login for all tests since search requires authentication
        self.client.login(username='testuser', password='testpass123')
    
    @log
    def test_view_url_exists(self):
        """Test that the URL exists"""
        response = self.client.get('/search/?q=python')
        self.assertEqual(response.status_code, 200)
    
    @log
    def test_view_url_accessible_by_name(self):
        """Test that the URL is accessible by name"""
        response = self.client.get(reverse('question_search') + '?q=python')
        self.assertEqual(response.status_code, 200)
    
    @log
    def test_login_required(self):
        """Test that login is required for search"""
        self.client.logout()
        response = self.client.get(reverse('question_search') + '?q=python')
        self.assertEqual(response.status_code, 302)  # Redirects to login
    
    @log
    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        response = self.client.get(reverse('question_search') + '?q=python')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/question_list.html')
    
    @log
    def test_search_results(self):
        """Test that search returns correct results"""
        response = self.client.get(reverse('question_search') + '?q=python')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['questions']), 2)  # Should find 2 questions with "python"
        
        # Test that the right questions are found
        question_ids = [q.id for q in response.context['questions']]
        self.assertIn(self.question1.pk, question_ids)
        self.assertIn(self.question2.pk, question_ids)
        self.assertNotIn(self.question3.pk, question_ids)
    
    @log
    def test_ajax_search(self):
        """Test that AJAX search returns JSON data"""
        response = self.client.get(
            reverse('question_search') + '?q=python&format=json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse JSON and check content
        data = response.json()
        self.assertEqual(len(data), 2)  # Should find 2 questions
        
        # Check data structure
        self.assertTrue('id' in data[0])
        self.assertTrue('title' in data[0])
        self.assertTrue('content' in data[0])
    
    @log
    def test_empty_query(self):
        """Test behavior with empty search query"""
        response = self.client.get(reverse('question_search') + '?q=')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['questions']), 0)  # Should return no results 