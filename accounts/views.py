from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import json
import razorpay
from django.conf import settings


User = get_user_model()


@csrf_exempt
@require_POST
def google_login(request):

    try:
        data = json.loads(request.body)

        email = data.get("email", "").strip().lower()
        name = data.get("name", "").strip()

        if not email:
            return JsonResponse(
                {"error": "Email is required"},
                status=400
            )

        # Existing user शोधा
        user = User.objects.filter(
            email=email
        ).first()

        # User नसेल तर नवीन तयार करा
        if not user:

            username = email.split("@")[0]

            # username duplicate असेल तर unique करा
            base_username = username
            counter = 1

            while User.objects.filter(
                    username=username
            ).exists():

                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name
            )

        return JsonResponse({
            "message": "Login successful",
            "email": user.email,
            "name": user.first_name,
            "is_logged_in": True,
            "is_premium": user.is_premium
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    except Exception as e:

        return JsonResponse(
            {"error": str(e)},
            status=500
        )

@csrf_exempt
def activate_premium(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST method required"
            },
            status=405
        )

    email = request.POST.get("email", "").strip().lower()

    if not email:
        return JsonResponse(
            {
                "success": False,
                "message": "Email is required"
            },
            status=400
        )

    try:

        user = User.objects.get(
            email__iexact=email
        )

    except User.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "User not found"
            },
            status=404
        )

    user.is_premium = True
    user.save(
        update_fields=["is_premium"]
    )

    return JsonResponse({
        "success": True,
        "email": user.email,
        "is_premium": user.is_premium,
        "message": "Premium activated successfully"
    })



@csrf_exempt
@require_POST
def create_razorpay_order(request):

    try:
        data = json.loads(request.body)

        email = data.get("email", "").strip().lower()
        plan = data.get("plan", "").strip().lower()

        if not email:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Email is required"
                },
                status=400
            )

        if plan not in ["monthly", "yearly"]:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid plan"
                },
                status=400
            )

        # Monthly ₹50 = 5000 paise
        # Yearly ₹299 = 29900 paise

        amount = 5000 if plan == "monthly" else 29900

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": f"talati_{email}_{plan}"
        })

        return JsonResponse({
            "success": True,
            "order_id": order["id"],
            "amount": amount,
            "currency": "INR",
            "plan": plan,
            "key_id": settings.RAZORPAY_KEY_ID
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON"
            },
            status=400
        )

    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "message": str(e)
            },
            status=500
        )

@csrf_exempt
@require_POST
def verify_razorpay_payment(request):

    try:
        data = json.loads(request.body)

        email = data.get("email", "").strip().lower()
        payment_id = data.get("razorpay_payment_id", "").strip()
        order_id = data.get("razorpay_order_id", "").strip()
        signature = data.get("razorpay_signature", "").strip()
        plan = data.get("plan", "").strip().lower()

        if not email:
            return JsonResponse({
                "success": False,
                "message": "Email is required"
            }, status=400)

        if not payment_id or not order_id or not signature:
            return JsonResponse({
                "success": False,
                "message": "Payment details are required"
            }, status=400)

        if plan not in ["monthly", "yearly"]:
            return JsonResponse({
                "success": False,
                "message": "Invalid plan"
            }, status=400)

        # Razorpay client
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        # Signature verification
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

        # User शोधा
        user = User.objects.get(
            email__iexact=email
        )

        # Premium activate
        user.is_premium = True

        user.save(
            update_fields=["is_premium"]
        )

        return JsonResponse({
            "success": True,
            "email": user.email,
            "is_premium": user.is_premium,
            "plan": plan,
            "message": "Payment verified and Premium activated"
        })

    except razorpay.errors.SignatureVerificationError:

        return JsonResponse({
            "success": False,
            "message": "Payment signature verification failed"
        }, status=400)

    except User.DoesNotExist:

        return JsonResponse({
            "success": False,
            "message": "User not found"
        }, status=404)

    except json.JSONDecodeError:

        return JsonResponse({
            "success": False,
            "message": "Invalid JSON"
        }, status=400)

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)