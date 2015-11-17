from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class Root(APIView):
    def get(self, request, format=None):
        return Response({
            reverse('homes-v1-root', request=request, format=format),
            reverse('users-v1-user-list', request=request, format=format),
        })


urlpatterns = patterns(
    '',
    url(r'^$', Root.as_view(), name='api-v1-root'),

    url(r'^homes/',
        include('dbservice.apps.homes.urls')),

    url(r'^users',
        include('dbservice.apps.users.urls')),

    url(r'^private/',
        include('dbservice.apps.private.urls')),

    url(r'^schemas/', include('dbservice.schemas')),
)
