from rest_framework import viewsets

from dbservice.apps.utils.viewsets import JSONSchemaViewSet

from . import serializers
from . import models


class UserDetailsViewSet(viewsets.ModelViewSet):
    """
    `/schemas/homes/userdetails/list/`
    `/schemas/homes/userdetails/detail/` and
    `/schemas/homes/userdetails/update/`
    """
    model = models.UserDetails
    serializer_class = serializers.UserDetailsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        else:
            return qs.filter(user=user)


class UserDetailsSchema(JSONSchemaViewSet):
    schema_for = serializers.UserDetailsSerializer
    app_name = 'private-v1'
