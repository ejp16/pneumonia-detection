from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):
    def authenticate(self, **kwargs):
        email=kwargs['email']
        password=kwargs['password']
        try:
            user=User.objects.get(email=email)
            if user.check_password(password) is True:
                return user
        except User.DoesNotExist:
                return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None