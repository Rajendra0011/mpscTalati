import json

from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg, Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import TestAttempt, TestAnswer, ExamQuestion
from datetime import timedelta

from django.db.models import Sum, Count, Q
from django.utils import timezone


User = get_user_model()


# =========================================================
# START EXAM
# =========================================================

@csrf_exempt
@require_POST
def start_test(request):

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    email = data.get("email", "").strip().lower()

    if not email:
        return JsonResponse(
            {"error": "Email is required"},
            status=400
        )

    try:
        user = User.objects.get(
            email=email
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"},
            status=404
        )

    questions = list(
        ExamQuestion.objects
        .filter(is_active=True)
        .order_by("?")[:10]
    )

    if not questions:
        return JsonResponse(
            {
                "error": "No exam questions available"
            },
            status=404
        )

    attempt = TestAttempt.objects.create(
        user=user,
        total_questions=len(questions)
    )

    data = []

    for question in questions:

        data.append({

            "id": question.id,

            "question": question.question,

            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d
            }
        })

    return JsonResponse({

        "attempt_id":
            str(attempt.attempt_id),

        "total_questions":
            len(data),

        "questions":
            data,

        "message":
            "Exam started successfully"
    })


# =========================================================
# SUBMIT EXAM
# =========================================================

@csrf_exempt
@require_POST
def submit_test(request):

    try:

        data = json.loads(
            request.body or "{}"
        )

        attempt_id = data.get(
            "attempt_id"
        )

        answers = data.get(
            "answers",
            []
        )

        attempt = TestAttempt.objects.get(
            attempt_id=attempt_id
        )

    except TestAttempt.DoesNotExist:

        return JsonResponse(
            {
                "error":
                    "Invalid attempt_id"
            },
            status=404
        )

    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=400
        )

    correct = 0
    attempted = 0

    for item in answers:

        question_id = item.get(
            "question_id"
        )

        selected_answer = item.get(
            "answer"
        )

        try:

            question = ExamQuestion.objects.get(
                id=question_id
            )

        except ExamQuestion.DoesNotExist:

            continue

        if selected_answer:
            attempted += 1

        is_correct = (
                selected_answer ==
                question.correct_answer
        )

        if is_correct:
            correct += 1

        TestAnswer.objects.update_or_create(

            attempt=attempt,

            question=question,

            defaults={
                "selected_answer":
                    selected_answer or "",

                "is_correct":
                    is_correct
            }
        )

    total_questions = (
        attempt.total_questions
    )

    wrong = attempted - correct

    attempt.score = correct

    attempt.completed = True

    attempt.save()

    return JsonResponse({

        "attempt_id":
            str(attempt.attempt_id),

        "total_questions":
            total_questions,

        "attempted":
            attempted,

        "correct":
            correct,

        "wrong":
            wrong,

        "score":
            correct
    })


# =========================================================
# USER RECORD / USER PERFORMANCE
# =========================================================

@csrf_exempt
@require_GET
def user_record(request):

    email = request.GET.get(
        "email",
        ""
    ).strip().lower()

    if not email:

        return JsonResponse(
            {
                "error":
                    "Email is required"
            },
            status=400
        )

    try:

        user = User.objects.get(
            email=email
        )

    except User.DoesNotExist:

        return JsonResponse(
            {
                "error":
                    "User not found"
            },
            status=404
        )

    attempts = TestAttempt.objects.filter(

        user=user,

        completed=True

    ).order_by(
        "-created_at"
    )

    # -----------------------------------------
    # BASIC STATS
    # -----------------------------------------

    tests_given = attempts.count()

    total_questions = attempts.aggregate(
        total=Sum("total_questions")
    )["total"] or 0

    total_correct = attempts.aggregate(
        total=Sum("score")
    )["total"] or 0

    total_wrong = (
            total_questions -
            total_correct
    )

    # -----------------------------------------
    # AVERAGE SCORE
    # -----------------------------------------

    average_score = attempts.aggregate(
        average=Avg("score")
    )["average"] or 0

    # -----------------------------------------
    # BEST SCORE
    # -----------------------------------------

    best_score = attempts.aggregate(
        best=Max("score")
    )["best"] or 0

    # -----------------------------------------
    # ACCURACY
    # -----------------------------------------

    if total_questions > 0:

        accuracy = round(
            (
                    total_correct * 100
            )
            / total_questions
        )

    else:

        accuracy = 0

    # -----------------------------------------
    # TEST HISTORY
    # -----------------------------------------

    history = []

    for attempt in attempts[:20]:

        percentage = 0

        if attempt.total_questions > 0:

            percentage = round(
                (
                        attempt.score * 100
                )
                / attempt.total_questions
            )

        history.append({

            "attempt_id":
                str(attempt.attempt_id),

            "total_questions":
                attempt.total_questions,

            "score":
                attempt.score,

            "percentage":
                percentage,

            "date":
                attempt.created_at.strftime(
                    "%d-%m-%Y"
                )
        })

    # -----------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------

    return JsonResponse({

        "name":
            user.first_name,

        "email":
            user.email,

        "tests_given":
            tests_given,

        "total_questions":
            total_questions,

        "total_correct":
            total_correct,

        "total_wrong":
            total_wrong,

        "accuracy":
            accuracy,

        "average_score":
            round(
                float(average_score),
                1
            ),

        "best_score":
            best_score,

        "history":
            history
    })

@csrf_exempt
@require_GET
def leaderboard(request):

    period = request.GET.get(
        "period",
        "all"
    ).lower()

    now = timezone.now()

    # -----------------------------------------
    # DATE FILTER
    # -----------------------------------------

    if period == "weekly":

        start_date = now - timedelta(days=7)

    elif period == "monthly":

        start_date = now - timedelta(days=30)

    else:

        start_date = None

    # -----------------------------------------
    # BASE QUERY
    # -----------------------------------------

    attempts = TestAttempt.objects.filter(
        completed=True,
        user__isnull=False
    )

    if start_date:

        attempts = attempts.filter(
            created_at__gte=start_date
        )

    # -----------------------------------------
    # USER RANKING
    # -----------------------------------------

    leaderboard_data = (
        attempts
        .values(
            "user_id",
            "user__first_name",
            "user__email"
        )
        .annotate(
            total_score=Sum("score"),
            tests_given=Count("id"),
            total_questions=Sum(
                "total_questions"
            )
        )
        .order_by(
            "-total_score",
            "-tests_given"
        )
    )

    result = []

    for rank, item in enumerate(
            leaderboard_data,
            start=1
    ):

        name = (
                item["user__first_name"]
                or item["user__email"]
                or "User"
        )

        total_score = (
                item["total_score"] or 0
        )

        tests_given = (
                item["tests_given"] or 0
        )

        total_questions = (
                item["total_questions"] or 0
        )

        result.append({

            "rank": rank,

            "name": name,

            "email":
                item["user__email"] or "",

            "score":
                total_score,

            "tests_given":
                tests_given,

            "total_questions":
                total_questions
        })

    logged_in_email = request.GET.get(
        "email",
        ""
    ).strip().lower()

    my_rank = None
    my_score = 0
    my_tests_given = 0

    if logged_in_email:

        for item in result:

            if item["email"].lower() == logged_in_email:

                my_rank = item["rank"]
                my_score = item["score"]
                my_tests_given = item["tests_given"]

                break

    return JsonResponse({

        "period": period,

        "total_users":
            len(result),

        "my_rank": my_rank,

        "my_score": my_score,

        "my_tests_given": my_tests_given,

        "leaderboard":
            result
    })