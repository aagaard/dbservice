from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include

from dbservice.apps.utils.routers import AppRouter
import dbservice.apps.private.views


router = AppRouter('private-v1')


router.register(r'userdetails',
                dbservice.apps.private.views.UserDetailsViewSet)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
