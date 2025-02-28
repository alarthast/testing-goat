from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect

from accounts.models import Token


def send_login_email(request):
    email = request.POST["email"]
    Token.objects.create(email=email)
    send_mail(
        "Your login link for Superlists",
        "body",
        "noreply@superlists",
        [email],
    )

    messages.success(
        request,
        "Check your email, we've sent you a link you can use to log in.",
    )
    return redirect("/")
