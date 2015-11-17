"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from . import models
from . import views


class AccessControlFilteringTestCase(TestCase):
    # superusers has access to everything
    # (normal) users only have access to themselves and their own data
    def setUp(self):
        self.superuser = models.User.objects.create_superuser(
            'super@test.com', 'qwe')
        self.user = models.User.objects.create_user(
            'normal@test.com', 'qwe')
        self.list_view = views.UserViewSet.as_view({'get': 'list'})
        factory = APIRequestFactory()
        self.request = factory.get('/v1/users/')

    def test_superuser_filtering(self):
        force_authenticate(self.request, user=self.superuser)
        response = self.list_view(self.request)
        self.assertEqual(2, response.data['count'])

    def test_user_filtering(self):
        force_authenticate(self.request, user=self.user)
        response = self.list_view(self.request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(self.user.id, response.data['results'][0]['id'])
