from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class OmniAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # The Q object allows an "OR" search across multiple columns
            user = User.objects.get(
                Q(username__iexact=username) | 
                Q(email__iexact=username) | 
                Q(phone_number=username)
            )
        except User.DoesNotExist:
            # If no match is found across any of the 3 fields, reject login
            return None

        # If user exists, check if the password is correct
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None