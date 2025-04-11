from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from core.models import Answer


@login_required
@require_POST
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    
    if answer.likes.filter(id=request.user.id).exists():
        answer.likes.remove(request.user)
        liked = False
    else:
        answer.likes.add(request.user)
        liked = True
    
    # Return JSON response if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': answer.likes.count()
        })
    
    return HttpResponseRedirect(reverse('question_detail', args=[answer.question.pk])) 