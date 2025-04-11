from django import forms
from core.models import Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'content': 'Your Answer',
        } 