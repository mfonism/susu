from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone

from shrewd_models.models import ShrewdModelManagerMixin, AbstractShrewdModelMixin


class UserManager(BaseUserManager, ShrewdModelManagerMixin):
    '''
    A shrewd manager for our shrewd user.
    '''
    def _create_user(self, email, password, **extra_fields):
        '''
        Create and save a user with the given email and password.
        '''
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        '''
        Create and save a user with the given email and password.
        '''
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_admin', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        '''
        Create and save a superuser with given email and password.
        '''
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, AbstractShrewdModelMixin, PermissionsMixin):
    '''
    A fully featured shrewd User model with admin-compliant permissions.

    Email is required. Other fields are optional.
    '''
    email = models.EmailField('email address', max_length=255, unique=True)
    first_name = models.CharField('first name', max_length=30)
    last_name = models.CharField('last name', max_length=150)
    is_admin = models.BooleanField('admin status', default=False)
    is_staff = models.BooleanField('staff status', default=False)

    objects = UserManager() # shrewd_mode=True
    all_objects = UserManager(shrewd_mode=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Send an email to this user.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs) 
