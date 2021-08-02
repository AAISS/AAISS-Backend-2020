import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from backend_api import validators

SMALL_MAX_LENGTH = 255
BIG_MAX_LENGTH = 65535


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
    email = models.EmailField(max_length=SMALL_MAX_LENGTH, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"User with id {self.id}: {self.email}"


class FieldOfInterest(models.Model):
    """Field of interest which user can add to their profile"""
    name = models.CharField(max_length=SMALL_MAX_LENGTH)

    def __str__(self):
        return f"FOI with name: {self.name}"


class Teacher(models.Model):
    """Workshop teacher database model"""
    name = models.CharField(max_length=SMALL_MAX_LENGTH)
    pic = models.ImageField(blank=True)
    cv_path = models.CharField(max_length=511, blank=True, default="")
    bio = models.CharField(max_length=BIG_MAX_LENGTH)
    order = models.SmallIntegerField(default=0)
    year = models.IntegerField(blank=False, default=2020)

    def __str__(self):
        return f"Teacher with id {self.id}: {self.name}"


class Presenter(models.Model):
    """Presentation presenter database model"""
    name = models.CharField(max_length=SMALL_MAX_LENGTH)
    pic = models.ImageField(blank=True)
    workplace = models.CharField(max_length=SMALL_MAX_LENGTH, blank=True)
    paper = models.CharField(max_length=SMALL_MAX_LENGTH, blank=True)
    cv_path = models.CharField(max_length=511, blank=True, default="")
    bio = models.CharField(max_length=BIG_MAX_LENGTH)
    order = models.SmallIntegerField(default=0)
    year = models.IntegerField(blank=False, default=2020)

    def __str__(self):
        return f"Presenter with id {self.id}: {self.name}==> {self.year}"


class Workshop(models.Model):
    name = models.CharField(max_length=SMALL_MAX_LENGTH)
    teachers = models.ManyToManyField(Teacher)
    cost = models.PositiveIntegerField()
    desc = models.CharField(max_length=BIG_MAX_LENGTH)
    has_project = models.BooleanField(default=False, blank=False)
    prerequisites = models.CharField(max_length=BIG_MAX_LENGTH, default='', blank=True)
    capacity = models.PositiveSmallIntegerField(default=50)
    add_to_calendar_link = models.CharField(max_length=SMALL_MAX_LENGTH, default='', blank=True)
    year = models.IntegerField(blank=False, default=2020)

    NOT_ASSIGNED = 'NOT_ASSIGNED'
    ELEMENTARY = 'Elementary'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    options = [
        (NOT_ASSIGNED, _('NOT_ASSIGNED')),
        (ELEMENTARY, _('Elementary')),
        (INTERMEDIATE, _('Intermediate')),
        (ADVANCED, _('Advanced')),
    ]
    level = models.CharField(
        choices=options,
        default=NOT_ASSIGNED,
        blank=True,
        max_length=15
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def no_of_participants(self):
        return len(User.objects.filter(registered_workshops=self).all())

    @property
    def participants(self):
        users = []
        for user in User.objects.filter(registered_workshops=self).all():
            users.append(user)
        return users

    def __str__(self):
        name = ""
        for teacher in self.teachers.all():
            name += teacher.name + " "
        return f"{name}: {self.name}"


class Presentation(models.Model):
    name = models.CharField(max_length=SMALL_MAX_LENGTH)
    presenters = models.ManyToManyField(Presenter)
    desc = models.CharField(max_length=BIG_MAX_LENGTH)
    year = models.IntegerField(blank=False, default=2020)

    NOT_ASSIGNED = 'NOT_ASSIGNED'
    ELEMENTARY = 'Elementary'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    options = [
        (NOT_ASSIGNED, _('NOT_ASSIGNED')),
        (ELEMENTARY, _('Elementary')),
        (INTERMEDIATE, _('Intermediate')),
        (ADVANCED, _('Advanced')),
    ]
    level = models.CharField(
        choices=options,
        default=NOT_ASSIGNED,
        blank=True,
        max_length=15
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def no_of_participants(self):
        return len(User.objects.filter(registered_for_presentations=True).all())

    @property
    def participants(self):
        users = []
        for user in User.objects.filter(registered_for_presentations=True).all():
            users.append(user)
        return users

    def __str__(self):
        name = ""
        for presenter in self.presenters.all():
            name += presenter.name + " "
        print(name)
        return f"{name}: {self.name}"


class User(models.Model):
    """Generic non-admin user profile data"""
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=SMALL_MAX_LENGTH)
    fields_of_interest = models.ManyToManyField(FieldOfInterest, blank=True)
    registered_workshops = models.ManyToManyField(Workshop, blank=True)
    registered_for_presentations = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=12, validators=[validators.validate_all_number])

    def __str__(self):
        return f"{self.account}"


class Misc(models.Model):
    name = models.CharField(max_length=SMALL_MAX_LENGTH, primary_key=True)
    desc = models.CharField(max_length=BIG_MAX_LENGTH, blank=True)
    pic = models.ImageField(blank=True)
    year = models.IntegerField(blank=False, default=2020)

    def __str__(self):
        return f"Misc with name {self.name}"


class Mailer(models.Model):
    ALL = 1
    WORKSHOP = 2
    PRESENTATIONS = 3
    CUSTOM = 4
    options = [
        (WORKSHOP, _('Send email to selected workshop(s) registered users')),
        (PRESENTATIONS, _('Send email to presentations users')),
        (ALL, _('Send email to all users')),
        (CUSTOM, _('Send email to custom selection of users')),
    ]

    subject = models.CharField(max_length=SMALL_MAX_LENGTH)
    target_mode = models.PositiveSmallIntegerField(
        choices=options,
        default=ALL,
    )
    workshop_selection = models.ManyToManyField(Workshop, blank=True)
    user_selection = models.ManyToManyField(User, blank=True)
    HTML_body = models.CharField(max_length=BIG_MAX_LENGTH)

    def __str__(self):
        return f"Mailer with id {self.id}: subject= {self.subject}"


class Payment(models.Model):
    authority = models.CharField(max_length=SMALL_MAX_LENGTH, primary_key=True)
    total_price = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workshops = models.ManyToManyField(Workshop, blank=True)
    presentation = models.BooleanField(default=False, blank=True)
    is_done = models.BooleanField(default=False)
    ref_id = models.CharField(default='', max_length=SMALL_MAX_LENGTH)
    year = models.IntegerField(blank=False, default=2020)
    date = models.DateField(blank=False,
                            default=datetime.datetime(year=2020, month=7, day=1, hour=0, minute=0, second=0,
                                                      microsecond=0))

    def __str__(self):
        return f"Payment for {self.user.account} ({self.total_price})  in {str(self.date)}"
