from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ExamQuestion


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "question",
        "subject",
        "correct_answer",
        "is_active",
    )

    list_filter = (
        "subject",
        "is_active",
    )

    search_fields = (
        "question",
    )