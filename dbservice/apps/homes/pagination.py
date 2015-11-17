from rest_framework import pagination
from rest_framework import serializers


class PageNumberPaginationWithoutCount(pagination.BasePaginationSerializer):
    count = serializers.Field(source='paginator.count')
    next = pagination.NextPageField(source='*')
    previous = pagination.PreviousPageField(source='*')
