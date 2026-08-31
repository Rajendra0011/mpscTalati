from django.conf import settings
from django.db import models
import uuid


class TestAttempt(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_attempts",
        null=True,
        blank=True
    )

    attempt_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
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


class ExamQuestion(models.Model):

    SUBJECT_CHOICES = [
        ("marathi", "मराठी"),
        ("english", "English"),
        ("maths", "गणित"),
        ("gk", "सामान्य ज्ञान"),
        ("reasoning", "बुद्धिमत्ता"),
    ]

    question = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_answer = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ]
    )

    subject = models.CharField(
        max_length=20,
        choices=SUBJECT_CHOICES,
        default="gk"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.question[:60]


class TestAnswer(models.Model):

    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(
        max_length=1,
        blank=True
    )

    is_correct = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.attempt} - Q{self.question.id}"