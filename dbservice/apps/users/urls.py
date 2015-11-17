from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register(r'', views.UserViewSet, base_name='users-v1-user')

urlpatterns = router.urls
