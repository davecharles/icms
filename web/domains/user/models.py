import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models

from guardian.mixins import GuardianUserMixin
from guardian.shortcuts import get_objects_for_user

from .managers import UserManager


class User(AbstractUser, GuardianUserMixin):
    # Statuses
    NEW = "NEW"
    BLOCKED = "BLOCKED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    ACTIVE = "ACTIVE"
    STATUSES = (
        (NEW, "New"),
        (BLOCKED, "Blocked"),
        (SUSPENDED, "Suspended"),
        (CANCELLED, "Cancelled"),
        (ACTIVE, "Active"),
    )

    # Password disposition
    TEMPORARY = "TEMPORARY"
    FULL = "FULL"
    PASSWORD_DISPOSITION = ((TEMPORARY, "Temporary"), (FULL, "Full"))

    REQUIRED_FIELDS = [
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "security_question",
        "security_answer",
    ]

    objects = UserManager()

    title = models.CharField(max_length=20, blank=False, null=True)
    preferred_first_name = models.CharField(max_length=4000, blank=True, null=True)
    middle_initials = models.CharField(max_length=40, blank=True, null=True)
    organisation = models.CharField(max_length=4000, blank=False, null=True)
    department = models.CharField(max_length=4000, blank=False, null=True)
    job_title = models.CharField(max_length=320, blank=False, null=True)
    location_at_address = models.CharField(max_length=4000, blank=True, null=True)
    work_address = models.CharField(max_length=300, blank=False, null=True)
    date_of_birth = models.DateField(blank=False, null=True)
    security_question = models.CharField(max_length=4000, blank=False, null=True)
    security_answer = models.CharField(max_length=4000, blank=False, null=True)
    share_contact_details = models.BooleanField(blank=False, null=False, default=False)
    account_status = models.CharField(
        max_length=20, choices=STATUSES, blank=False, null=False, default=ACTIVE
    )
    account_status_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True, related_name="users_changed"
    )
    account_status_date = models.DateField(blank=True, null=True)
    password_disposition = models.CharField(
        max_length=20, choices=PASSWORD_DISPOSITION, blank=True, null=True
    )
    unsuccessful_login_attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        if self.title:
            return " ".join(filter(None, (self.title, self.first_name, self.last_name)))
        else:
            return " ".join(filter(None, (self.first_name, self.last_name)))

    @property
    def account_status_by_full_name(self):
        return None if self.account_status_by is None else self.account_status_by.full_name

    @property
    def account_last_login_date(self):
        return None if self.last_login is None else self.last_login.date()

    def is_importer(self):
        """Checks if user is a member of any import organisation or is an individual importer"""

        # Check if user has any invidual importer company
        own_importers = self.own_importers.filter(is_active=True).count()
        if own_importers > 0:
            return True

        # Check if user is a member of any import/agent organisation
        from web.domains.importer.models import Importer

        return (
            get_objects_for_user(
                self,
                "web.is_contact_of_importer",
                Importer.objects.filter(is_active=True),
                with_superuser=False,
            ).count()
            > 0
        )

    def is_exporter(self):
        """Checks if user is a member of any export organisation."""
        from web.domains.exporter.models import Exporter

        return (
            get_objects_for_user(
                self,
                "web.is_contact_of_exporter",
                Exporter.objects.filter(is_active=True),
                with_superuser=False,
            ).count()
            > 0
        )

    def is_export_case_officer(self):
        return self.has_perm("web.export_case_officer")

    def set_temp_password(self, length=8):
        """
        Generates a random alphanumerical password of given length.
        Default length is 8
        """
        temp_password = "".join(
            random.SystemRandom().choices(string.ascii_letters + string.digits, k=length)
        )
        self.set_password(temp_password)
        self.password_disposition = self.TEMPORARY
        return temp_password

    class Meta:
        ordering = ("-is_active", "first_name")


class PhoneNumber(models.Model):
    WORK = "WORK"
    FAX = "FAX"
    MOBILE = "MOBILE"
    HOME = "HOME"
    MINICOM = "MINICOM"
    TYPES = ((WORK, "Work"), (FAX, "Fax"), (MOBILE, "Mobile"), (HOME, "Home"), (MINICOM, "Minicom"))
    phone = models.CharField(max_length=60, blank=False, null=False)
    type = models.CharField(max_length=30, choices=TYPES, blank=False, null=False, default=WORK)
    comment = models.CharField(max_length=4000, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="phone_numbers")

    @property
    def entity_type(self):
        return dict(PhoneNumber.TYPES)[self.type]


class Email(models.Model):
    WORK = "WORK"
    HOME = "HOME"
    TYPES = ((WORK, "Work"), (HOME, "Home"))
    email = models.EmailField(max_length=254, blank=False, null=False)
    type = models.CharField(max_length=30, choices=TYPES, blank=False, null=False, default=WORK)
    portal_notifications = models.BooleanField(blank=False, null=False, default=False)
    comment = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        abstract = True


class AlternativeEmail(Email):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alternative_emails")

    def __str__(self):
        return self.email


class PersonalEmail(Email):
    is_primary = models.BooleanField(blank=False, null=False, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_emails")

    def __str__(self):
        return self.email
