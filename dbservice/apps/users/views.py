from rest_framework import viewsets

from dbservice.apps.utils.viewsets import JSONSchemaViewSet

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Data format described in `/schemas/users/users/list`,
    `/schemas/users/users/detail/` and `/schemas/users/users/update`.
    May be filtered on `email`.
    """
    model = User
    serializer_class = UserSerializer
    filter_fields = ('email',)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(id=user.id)


class UserSchema(JSONSchemaViewSet):
    schema_for = UserSerializer
    app_name = 'users-v1'
