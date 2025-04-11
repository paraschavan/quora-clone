from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from core.models import Question
from core.forms import QuestionForm, AnswerForm
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from functools import wraps
import time


# Leaky Bucket Throttling
def throttle(rate=1, per=1):
    def decorator(fn):
        @wraps(fn)
        def throttled(request, *args, **kwargs):
            session_id = request.session.session_key or request.META.get(
                "REMOTE_ADDR", ""
            )
            cache_key = f"throttle_{session_id}_{fn.__name__}"

            now = time.time()
            timestamps = cache.get(cache_key, [])
            timestamps = [t for t in timestamps if now - t < per]

            if len(timestamps) >= rate:
                return HttpResponse(
                    "Rate limit exceeded. Try again in a moment.", status=429
                )

            timestamps.append(now)
            cache.set(cache_key, timestamps, timeout=per * 2)

            return fn(request, *args, **kwargs)

        return throttled

    return decorator


class QuestionListView(ListView):
    model = Question
    template_name = "core/question_list.html"
    context_object_name = "questions"
    paginate_by = 10


class QuestionDetailView(LoginRequiredMixin, DetailView):
    model = Question
    template_name = "core/question_detail.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["answer_form"] = AnswerForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        question = self.get_object()
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

        return redirect("question_detail", pk=question.pk)


class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "core/question_form.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Generate search vector for fulltext search
        question = self.object  # type: ignore
        vector = SearchVector("title", weight="A") + SearchVector("content", weight="B")
        Question.objects.filter(pk=question.pk).update(search_vector=vector)

        return response


class QuestionSearchView(LoginRequiredMixin, ListView):
    model = Question
    template_name = "core/question_list.html"
    context_object_name = "questions"
    paginate_by = 10
    login_url = "login"

    @method_decorator(throttle(rate=1, per=1))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if not query:
            return Question.objects.none()

        if self.request.GET.get("format") == "json":
            return self._get_ajax_results(query)

        return self._get_full_results(query)

    def _get_ajax_results(self, query):
        # For dropdown search, limit to top 5 results
        search_query = SearchQuery(query)
        results = (
            Question.objects.select_related("author")
            .annotate(rank=SearchRank("search_vector", search_query))
            .filter(rank__gt=0.01)
            .order_by("-rank")[:5]
        )

        if not results:
            results = Question.objects.select_related("author").filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )[:5]

        return results

    def _get_full_results(self, query):
        # First try vector search for better relevance
        search_query = SearchQuery(query)
        vector_results = (
            Question.objects.select_related("author")
            .annotate(rank=SearchRank("search_vector", search_query))
            .filter(rank__gt=0.01)
            .order_by("-rank")
        )

        # If fewer than 3 results, fall back to simpler text search
        # This helps with single character queries or new content
        if vector_results.count() < 3:
            terms = query.split()
            text_query = Q()

            for term in terms:
                text_query |= Q(title__icontains=term) | Q(content__icontains=term)

            if text_query:
                text_results = (
                    Question.objects.select_related("author")
                    .filter(text_query)
                    .distinct()
                )

                # Combine vector and text results without duplicates
                combined_ids = list(vector_results.values_list("id", flat=True))
                combined_ids.extend(
                    [q.pk for q in text_results if q.pk not in combined_ids]
                )

                return (
                    Question.objects.select_related("author")
                    .filter(id__in=combined_ids)
                    .order_by("-created_at")
                )

        return vector_results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("format") == "json":
            data = []
            for question in context["questions"]:
                data.append(
                    {
                        "id": question.pk,
                        "title": question.title,
                        "content": (
                            question.content[:100] + "..."
                            if len(question.content) > 100
                            else question.content
                        ),
                        "author": question.author.username,
                        "created_at": question.created_at.strftime("%Y-%m-%d"),
                        "answers_count": question.answers.count(),
                    }
                )
            return JsonResponse(data, safe=False)
        return super().render_to_response(context, **response_kwargs)
