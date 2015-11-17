from rest_framework import serializers

from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    _default_view_name = 'users-v1-%(model_name)s-detail'

    userdetails = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='private-v1-userdetails-detail')

    class Meta:
        model = User
        fields = ('id', 'url', 'email', 'is_staff', 'is_superuser',
                  'userdetails', 'is_active', 'password')
        read_only_fields = ('is_staff', 'is_superuser', 'is_active')
        write_only_fields = ('password',)

    def restore_object(self, attrs, instance=None):
        user = super().restore_object(attrs, instance)
        user.set_password(attrs['password'])
        return user
