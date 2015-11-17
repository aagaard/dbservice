from django.db import models


class UserDetails(models.Model):
    # TODO: Add name
    user = models.OneToOneField('users.User')
    address = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=120, blank=True)
