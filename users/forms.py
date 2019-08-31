from django.contrib.auth.forms import (
    UsernameField,
    UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
)

from .models import User


class UserCreationForm(BaseUserCreationForm):
    '''
    A form that creates a user, with no privileges, from the given email and password.
    '''
    class Meta:
        model = User
        fields = ('email',)


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = ('__all__')
