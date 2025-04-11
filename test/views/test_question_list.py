from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.question import Question
from test import log

class QuestionListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.test_user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create 15 questions for pagination tests
        for i in range(15):
            Question.objects.create(
                title=f'Test Question {i}',
                content=f'Content for question {i}',
                author=cls.test_user
            )
    
    def setUp(self):
        self.client = Client()
    
    @log
    def test_view_url_exists(self):
        """Test that the URL exists"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    @log
    def test_view_url_accessible_by_name(self):
        """Test that the URL is accessible by name"""
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
    
    @log
    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/question_list.html')
    
    @log
    def test_pagination_is_ten(self):
        """Test that pagination is set to 10 items per page"""
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['questions']), 10)
    
    @log
    def test_second_page(self):
        """Test that the second page shows remaining questions"""
        response = self.client.get(reverse('question_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['questions']), 5)  # Only 5 left on second page 