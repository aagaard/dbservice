from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from dbservice.apps.users.models import User

from . import views


class AccessControlFilteringTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'super@test.com', 'qwe')
        self.user = User.objects.create_user(
            'normal@test.com', 'qwe')
        self.user_details_list_view = \
            views.UserDetailsViewSet.as_view({'get': 'list'})
        factory = APIRequestFactory()
        self.request = factory.get('/v1/userdetails/')

    def test_superuser_filtering(self):
        force_authenticate(self.request, user=self.superuser)
        response = self.user_details_list_view(self.request)
        self.assertEqual(2, response.data['count'])

    def test_user_filtering(self):
        force_authenticate(self.request, user=self.user)
        response = self.user_details_list_view(self.request)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(self.user.id, response.data['results'][0]['id'])
