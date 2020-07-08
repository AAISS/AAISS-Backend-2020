from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator

from backend_api import validators


class AccountManager(BaseUserManager):
    def create_user(self, email, password):
        """Creates User Accounts to use in user model"""
        if not email:
            raise ValueError("Users must have an email address")

        email = email.lower()
        user = self.model(email=email, account_type=1)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates default superusers"""
        if not email:
            raise ValueError("Admins must have an email address")

        email = email.lower()
        admin = self.model(email=email, account_type=0)
        admin.set_password(password)
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        return admin


class Account(AbstractBaseUser, PermissionsMixin):
    """Default user model for database"""
    ACCOUNT_TYPE_CHOICES = (
        (0, 'admin'),
        (1, 'User')
    )
    account_type = models.PositiveSmallIntegerField(choices=ACCOUNT_TYPE_CHOICES)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"User with id {self.id}: {self.email}"


class FieldOfInterest(models.Model):
    """Field of interest which user can add to their profile"""
    name = models.CharField(max_length=255)


class Teacher(models.Model):
    """Workshop teacher database model"""
    name = models.CharField(max_length=255)
    pic_path = models.CharField(max_length=511)
    cv_path = models.CharField(max_length=511, blank=True, default="")
    desc = models.CharField(max_length=65535)


class Presenter(models.Model):
    """Presentation presenter database model"""
    name = models.CharField(max_length=255)
    pic_path = models.CharField(max_length=511)
    workplace = models.CharField(max_length=255)
    paper = models.CharField(max_length=255)
    cv_path = models.CharField(max_length=511, blank=True, default="")
    desc = models.CharField(max_length=65535)


class Workshop(models.Model):
    name = models.CharField(max_length=255)
    teachers = models.ManyToManyField(Teacher)
    cost = models.PositiveIntegerField()
    desc = models.CharField(max_length=65535)


class Presentation(models.Model):
    name = models.CharField(max_length=255)
    presenters = models.ManyToManyField(Presenter)
    desc = models.CharField(max_length=65535)


class User(models.Model):
    """Generic non-admin user profile data"""
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    fields_of_interest = models.ManyToManyField(FieldOfInterest, blank=True)
    registered_workshops = models.ManyToManyField(Workshop, blank=True)
    registered_for_presentations = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=12, validators=[validators.validate_all_number])
    national_code = models.CharField(max_length=10,
                                     validators=[RegexValidator(regex='^.{10}$', message='Length has to be 10')])
