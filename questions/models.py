from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model

from accounts.models import User


class Question(models.Model):

    TEST_TYPE_CHOICES = [
        ("practice", "Practice Test"),
        ("exam", "Exam"),
        ("pre_exam", "Pre Exam"),
        ("main_exam", "Main Exam"),
    ]

    test_type = models.CharField(
        max_length=20,
        choices=TEST_TYPE_CHOICES,
        default="practice"
    )



    subject = models.CharField(max_length=100)




    question = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_answer = models.CharField(max_length=1)

    explanation = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.question




class TestAttempt(models.Model):

    attempt_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    test_type = models.CharField(
        max_length=20,
        default="test"
    )

    total_questions = models.IntegerField(
        default=10
    )

    score = models.IntegerField(
        default=0
    )

    completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.attempt_id)


class TestAnswer(models.Model):

    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(
        max_length=1
    )

    is_correct = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.attempt} - {self.question_id}"

class NoteSubject(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name


class Note(models.Model):

    subject = models.ForeignKey(
        NoteSubject,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    title = models.CharField(
        max_length=200
    )

    pdf = models.FileField(
        upload_to="notes/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class FavoriteQuestion(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_questions"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"],
                name="unique_user_favorite_question"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.question}"