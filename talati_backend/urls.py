from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def home(request):
    return JsonResponse({
        "message": "Talathi Backend is running"
    })


urlpatterns = [
    path("", home),

    path("admin/", admin.site.urls),

    path("api/", include("questions.urls")),

    path(
        "api/exam/",
        include("exam.urls")
    ),

    path(
        "api/auth/",
        include("accounts.urls")
    ),
]