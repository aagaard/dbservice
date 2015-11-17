from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dbservice.apps.private.models import UserDetails


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        now = timezone.now()
        email = UserManager.normalize_email(email)
        user = self.model(email=email,
                          is_superuser=False,
                          last_login=now)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    The User class for all users of the system.

    is_staff == True => Sys. admin.
    is_superuser == True => DNO user
    not is_staff and not is_superuser => Residential home user
    """
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    email = models.EmailField(
        verbose_name='Email address',
        unique=True,
        max_length=255,
    )
    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    class Meta:
        ordering = ['email']


@receiver(post_save, sender=User)
def autocreate_userdetails(sender, instance, created, raw=False, **kwargs):
    if raw:
        return
    if created:
        UserDetails.objects.create(user=instance)
