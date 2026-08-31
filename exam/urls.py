from django.urls import path

from .views import start_test,submit_test,user_record,leaderboard


urlpatterns = [
    path("start/", start_test),
    path("submit/", submit_test),
    path(
        "user/record/",
        user_record,
        name="user_record"
    ),

    path(
        "leaderboard/",
        leaderboard,
        name="leaderboard"
    ),
]