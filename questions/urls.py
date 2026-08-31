from django.urls import path

from .views import (
    ten_question_test,
    start_test,
    submit_test,
    start_pre_exam,
    submit_pre_exam,
    start_main_exam,
    submit_main_exam,
    subject_questions,
    note_subjects,
    subject_notes,
    note_detail,
    add_favorite,
    remove_favorite,
    favorite_questions,
    favorite_question_detail,


)

urlpatterns = [

    path(
        "test/10/",
        ten_question_test,
        name="ten_question_test"
    ),

    path(
        "test/start/",
        start_test,
        name="start_test"
    ),

    path(
        "test/submit/",
        submit_test,
        name="submit_test"
    ),

    path(
        "pre-exam/start/",
        start_pre_exam,
        name="start_pre_exam"
    ),

    path(
        "pre-exam/submit/",
        submit_pre_exam,
        name="submit_pre_exam"
    ),

    path(
        "main-exam/start/",
        start_main_exam,
        name="start_main_exam"
    ),

    path(
        "main-exam/submit/",
        submit_main_exam,
        name="submit_main_exam"
    ),

    path(
        "subject/questions/",
        subject_questions,
        name="subject_questions"
    ),

    path(
        "notes/subjects/",
        note_subjects,
        name="note_subjects"
    ),

    path(
        "notes/",
        subject_notes,
        name="subject_notes"
    ),

    path(
        "notes/<int:note_id>/",
        note_detail,
        name="note_detail"
    ),

    path(
        "favorites/add/",
        add_favorite,
        name="add_favorite"
    ),

    path(
        "favorites/remove/",
        remove_favorite,
        name="remove_favorite"
    ),

    path(
        "favorites/",
        favorite_questions,
        name="favorite_questions"
    ),

    path(
        "favorites/question/<int:question_id>/",
        favorite_question_detail,
        name="favorite_question_detail"
    ),





]