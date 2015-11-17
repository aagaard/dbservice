from rest_framework import serializers

from . import models


class UserDetailsSerializer(serializers.HyperlinkedModelSerializer):
    _default_view_name = 'private-v1-%(model_name)s-detail'

    user = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='users-v1-user-detail')

    class Meta:
        model = models.UserDetails
        fields = ('id', 'user', 'address', 'postal_code', 'city')
