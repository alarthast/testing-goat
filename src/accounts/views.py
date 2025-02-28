from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse

from accounts.models import Token


def send_login_email(request):
    email = request.POST["email"]
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse("login") + "?token=" + str(token.uid),
    )
    send_mail(
        "Your login link for Superlists",
        f"Use this link to log in: {url}",
        "noreply@superlists",
        [email],
    )

    messages.success(
        request,
        "Check your email, we've sent you a link you can use to log in.",
    )
    return redirect("/")


def login(request):
    return redirect("/")
