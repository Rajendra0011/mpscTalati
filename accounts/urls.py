from django.urls import path
from .views import (
    google_login,
    activate_premium,
    create_razorpay_order,
    verify_razorpay_payment,
)


urlpatterns = [
    path(
        "google-login/",
        google_login,
        name="google_login"
    ),

    path(
        "activate-premium/",
        activate_premium,
        name="activate_premium"
    ),

    path(
        "razorpay/create-order/",
        create_razorpay_order,
        name="create_razorpay_order"
    ),

    path(
        "razorpay/verify-payment/",
        verify_razorpay_payment,
        name="verify_razorpay_payment"
    ),
]