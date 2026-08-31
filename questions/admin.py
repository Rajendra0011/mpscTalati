from django.contrib import admin

from .models import (
    Question,
    TestAttempt,
    TestAnswer,
    NoteSubject,
    Note,
    FavoriteQuestion,
)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "question",
        "subject",
        "test_type",
        "correct_answer",
    )

    list_filter = (
        "test_type",
        "subject",
    )

    search_fields = (
        "question",
    )

    list_per_page = 25


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):

    list_display = (
        "attempt_id",
        "user",
        "test_type",
        "total_questions",
        "score",
        "completed",
        "created_at",
    )

    list_filter = (
        "test_type",
        "completed",
    )


@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):

    list_display = (
        "attempt",
        "question",
        "selected_answer",
        "is_correct",
    )

    list_filter = (
        "is_correct",
    )


@admin.register(NoteSubject)
class NoteSubjectAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "subject",
        "created_at",
    )

    list_filter = (
        "subject",
    )

    search_fields = (
        "title",
    )

@admin.register(FavoriteQuestion)
class FavoriteQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "question",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__email",
        "question__question",
    )