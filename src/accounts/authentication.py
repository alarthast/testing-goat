from accounts.models import Token, User


class PasswordlessAuthenticationBackend:
    def authenticate(self, request, uid):
        try:
            token = Token.objects.get(uid=uid)
        except Token.DoesNotExist:
            return None
        return self.get_user(email=token.email) or User.objects.create(
            email=token.email
        )

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
