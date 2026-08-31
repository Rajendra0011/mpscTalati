import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import razorpay
from django.conf import settings

from .models import Question, TestAttempt, TestAnswer,NoteSubject, Note, FavoriteQuestion

User = get_user_model()

def ten_question_test(request):

    questions = Question.objects.filter(
        test_type="practice"
    ).order_by("?")[:1]

    data = []

    for question in questions:
        data.append({
            "id": question.id,
            "question": question.question,
            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d,
            }
        })

    return JsonResponse({
        "test_type": "10_questions",
        "total_questions": len(data),
        "questions": data
    })


@csrf_exempt
@require_POST
def start_test(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:
        data = {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

    if not email:
        return JsonResponse(
            {
                "error": "Email is required"
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
                "error": "User not found"
            },
            status=404
        )

    # PRACTICE TEST → 5 QUESTIONS
    questions = list(
        Question.objects
        .filter(
            test_type="practice"
        )
        .order_by("?")[:5]
    )

    if not questions:
        return JsonResponse(
            {
                "error": "No practice questions available"
            },
            status=404
        )

    attempt = TestAttempt.objects.create(
        user=user,
        test_type="practice",
        total_questions=len(questions)
    )

    result = []

    for question in questions:

        result.append({
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
            len(result),

        "questions":
            result,

        "message":
            "Practice test started successfully"
    })

@csrf_exempt
@require_POST
def submit_test(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400
        )

    attempt_id = data.get(
        "attempt_id"
    )

    answers = data.get(
        "answers",
        []
    )

    if not attempt_id:
        return JsonResponse(
            {
                "error": "attempt_id is required"
            },
            status=400
        )

    try:
        attempt = TestAttempt.objects.get(
            attempt_id=attempt_id
        )
    except TestAttempt.DoesNotExist:
        return JsonResponse(
            {
                "error": "Attempt not found"
            },
            status=404
        )

    if attempt.completed:
        return JsonResponse(
            {
                "error": "Test already submitted"
            },
            status=400
        )

    correct = 0
    attempted = 0

    for answer in answers:

        question_id = answer.get(
            "question_id"
        )

        selected_answer = answer.get(
            "answer",
            ""
        ).lower()

        try:
            question = Question.objects.get(
                id=question_id
            )
        except Question.DoesNotExist:
            continue

        if selected_answer:
            attempted += 1

        is_correct = (
                selected_answer
                == question.correct_answer
        )

        if is_correct:
            correct += 1

        TestAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct
        )

    wrong = attempted - correct

    attempt.score = correct
    attempt.completed = True
    attempt.save(
        update_fields=[
            "score",
            "completed"
        ]
    )

    return JsonResponse({

        "attempt_id":
            str(attempt.attempt_id),

        "total_questions":
            attempt.total_questions,

        "attempted":
            attempted,

        "correct":
            correct,

        "wrong":
            wrong,

        "score":
            correct,

        "message":
            "Test submitted successfully"
    })


@csrf_exempt
@require_POST
def start_pre_exam(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:
        data = {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

    if not email:
        return JsonResponse(
            {
                "error": "Email is required"
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
                "error": "User not found"
            },
            status=404
        )

    questions = list(
        Question.objects
        .filter(
            test_type="pre_exam"
        )
        .order_by("?")[:100]
    )

    if not questions:
        return JsonResponse(
            {
                "error": "No questions available"
            },
            status=404
        )

    attempt = TestAttempt.objects.create(
        user=user,
        test_type="pre_exam",
        total_questions=len(questions)
    )

    result = []

    for question in questions:

        result.append({
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
            len(result),

        "questions":
            result,

        "message":
            "Pre Exam started successfully"
    })

@csrf_exempt
@require_POST
def submit_pre_exam(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400
        )
    print("SUBMIT DATA =", data)

    attempt_id = data.get(
        "attempt_id"
    )

    answers = data.get(
        "answers",
        []
    )

    print("ANSWERS =", answers)

    if not attempt_id:
        return JsonResponse(
            {
                "error": "attempt_id is required"
            },
            status=400
        )

    try:
        attempt = TestAttempt.objects.get(
            attempt_id=attempt_id,
            test_type="pre_exam"
        )
    except TestAttempt.DoesNotExist:
        return JsonResponse(
            {
                "error": "Pre Exam attempt not found"
            },
            status=404
        )

    if attempt.completed:

        return JsonResponse(
            {
                "error": "Test already submitted"
            },
            status=400
        )

    correct = 0
    attempted = 0

    for answer in answers:

        question_id = answer.get(
            "question_id"
        )

        selected_answer = answer.get(
            "answer",
            ""
        ).upper()

        print(
            "QUESTION ID =",
            question_id,
            "ANSWER =",
            selected_answer
        )

        try:
            question = Question.objects.get(
                id=question_id,
                test_type="pre_exam"
            )

        except Question.DoesNotExist:
            continue

        if selected_answer:
            attempted += 1

        is_correct = (
                selected_answer
                == question.correct_answer.upper()
        )

        if is_correct:
            correct += 1

        TestAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct
        )

    wrong = attempted - correct

    attempt.score = correct
    attempt.completed = True

    attempt.save(
        update_fields=[
            "score",
            "completed"
        ]
    )

    return JsonResponse({

        "attempt_id":
            str(attempt.attempt_id),

        "total_questions":
            attempt.total_questions,

        "attempted":
            attempted,

        "correct":
            correct,

        "wrong":
            wrong,

        "score":
            correct,

        "message":
            "Pre Exam submitted successfully"
    })

@csrf_exempt
@require_POST
def start_main_exam(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:
        data = {}

    email = data.get(
        "email",
        ""
    ).strip().lower()

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
        Question.objects
        .filter(
            test_type="main_exam"
        )
        .order_by("?")[:100]
    )

    if not questions:
        return JsonResponse(
            {
                "error":
                    "No Main Exam questions available"
            },
            status=404
        )

    attempt = TestAttempt.objects.create(
        user=user,
        test_type="main_exam",
        total_questions=len(questions)
    )

    result = []

    for question in questions:

        result.append({
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
            len(result),

        "questions":
            result,

        "message":
            "Main Exam started successfully"
    })

@csrf_exempt
@require_POST
def submit_main_exam(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400
        )

    attempt_id = data.get(
        "attempt_id"
    )

    answers = data.get(
        "answers",
        []
    )

    if not attempt_id:
        return JsonResponse(
            {
                "error": "attempt_id is required"
            },
            status=400
        )

    try:
        attempt = TestAttempt.objects.get(
            attempt_id=attempt_id,
            test_type="main_exam"
        )
    except TestAttempt.DoesNotExist:
        return JsonResponse(
            {
                "error": "Main Exam attempt not found"
            },
            status=404
        )

    if attempt.completed:
        return JsonResponse(
            {
                "error": "Test already submitted"
            },
            status=400
        )

    correct = 0
    attempted = 0

    for answer in answers:

        question_id = answer.get(
            "question_id"
        )

        selected_answer = answer.get(
            "answer",
            ""
        ).upper()

        try:
            question = Question.objects.get(
                id=question_id,
                test_type="main_exam"
            )
        except Question.DoesNotExist:
            continue

        if selected_answer:
            attempted += 1

        is_correct = (
                selected_answer
                == question.correct_answer.upper()
        )

        if is_correct:
            correct += 1

        TestAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct
        )

    wrong = attempted - correct

    attempt.score = correct
    attempt.completed = True

    attempt.save(
        update_fields=[
            "score",
            "completed"
        ]
    )

    return JsonResponse({

        "attempt_id":
            str(attempt.attempt_id),

        "total_questions":
            attempt.total_questions,

        "attempted":
            attempted,

        "correct":
            correct,

        "wrong":
            wrong,

        "score":
            correct,

        "message":
            "Main Exam submitted successfully"
    })

def subject_questions(request):

    if request.method != "GET":
        return JsonResponse(
            {
                "error": "GET method required"
            },
            status=405
        )

    subject = request.GET.get(
        "subject",
        ""
    ).strip()

    if not subject:
        return JsonResponse(
            {
                "error": "Subject is required"
            },
            status=400
        )

    questions = Question.objects.filter(
        subject=subject,
        test_type="practice"
    ).order_by("id")

    data = []

    for question in questions:

        data.append({
            "id": question.id,

            "question":
                question.question,

            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d
            },

            "correct_answer":
                question.correct_answer.upper()
        })

    return JsonResponse({
        "subject": subject,
        "total_questions": len(data),
        "questions": data
    })

def note_subjects(request):

    subjects = NoteSubject.objects.all().order_by("name")

    data = []

    for subject in subjects:
        data.append({
            "id": subject.id,
            "name": subject.name
        })

    return JsonResponse({
        "subjects": data
    })


def subject_notes(request):

    subject_id = request.GET.get("subject_id")

    if not subject_id:
        return JsonResponse(
            {
                "error": "subject_id is required"
            },
            status=400
        )

    notes = Note.objects.filter(
        subject_id=subject_id
    ).order_by("-created_at")

    data = []

    for note in notes:

        data.append({
            "id": note.id,
            "title": note.title,
            "pdf_url": request.build_absolute_uri(
                note.pdf.url
            )
        })

    return JsonResponse({
        "subject_id": subject_id,
        "notes": data
    })

def note_detail(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id
    )

    return JsonResponse({
        "id": note.id,
        "title": note.title,
        "pdf_url": request.build_absolute_uri(
            note.pdf.url
        )
    })

@csrf_exempt
@require_POST
def add_favorite(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400
        )

    email = data.get(
        "email",
        ""
    ).strip().lower()

    question_id = data.get(
        "question_id"
    )

    if not email or not question_id:

        return JsonResponse(
            {
                "error":
                    "email and question_id are required"
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
                "error": "User not found"
            },
            status=404
        )

    try:

        question = Question.objects.get(
            id=question_id
        )

    except Question.DoesNotExist:

        return JsonResponse(
            {
                "error": "Question not found"
            },
            status=404
        )

    favorite, created = FavoriteQuestion.objects.get_or_create(
        user=user,
        question=question
    )

    return JsonResponse({

        "success": True,

        "is_favorite": True,

        "created": created,

        "question_id":
            question.id,

        "message":
            "Question added to favorites"
    })


@csrf_exempt
@require_POST
def remove_favorite(request):

    try:
        data = json.loads(
            request.body or "{}"
        )
    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400
        )

    email = data.get(
        "email",
        ""
    ).strip().lower()

    question_id = data.get(
        "question_id"
    )

    if not email or not question_id:

        return JsonResponse(
            {
                "error":
                    "email and question_id are required"
            },
            status=400
        )

    deleted, _ = FavoriteQuestion.objects.filter(
        user__email=email,
        question_id=question_id
    ).delete()

    return JsonResponse({

        "success": True,

        "is_favorite": False,

        "deleted": deleted > 0,

        "question_id":
            question_id,

        "message":
            "Question removed from favorites"
    })

def favorite_questions(request):

    email = request.GET.get(
        "email",
        ""
    ).strip().lower()

    if not email:

        return JsonResponse(
            {
                "error": "Email is required"
            },
            status=400
        )

    favorites = FavoriteQuestion.objects.filter(
        user__email=email
    ).select_related(
        "question"
    ).order_by(
        "-created_at"
    )

    data = []

    for favorite in favorites:

        question = favorite.question

        data.append({

            "id":
                question.id,

            "question":
                question.question,

            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d
            },

            "correct_answer":
                question.correct_answer.upper()
        })

    return JsonResponse({

        "total":
            len(data),

        "questions":
            data
    })

def favorite_question_detail(request, question_id):

    email = request.GET.get(
        "email",
        ""
    ).strip().lower()

    if not email:
        return JsonResponse(
            {
                "error": "Email is required"
            },
            status=400
        )

    try:
        favorite = FavoriteQuestion.objects.select_related(
            "question"
        ).get(
            user__email=email,
            question_id=question_id
        )

    except FavoriteQuestion.DoesNotExist:

        return JsonResponse(
            {
                "error": "Favorite question not found"
            },
            status=404
        )

    question = favorite.question

    return JsonResponse({

        "id": question.id,

        "question": question.question,

        "options": {
            "A": question.option_a,
            "B": question.option_b,
            "C": question.option_c,
            "D": question.option_d
        },

        "correct_answer":
            question.correct_answer.upper(),

        "is_favorite": True
    })

