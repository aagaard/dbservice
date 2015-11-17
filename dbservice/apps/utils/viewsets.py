from django.utils.decorators import classonlymethod
from rest_framework.decorators import list_route
from rest_framework.fields import ChoiceField
from rest_framework.fields import DateTimeField
from rest_framework.fields import EmailField
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.utils.formatting import dedent
from rest_framework.viewsets import ViewSet
from rest_framework import status


class JSONSchemaViewSet(ViewSet):
    schema_for = None
    app_name = None

    @classonlymethod
    def as_view(cls, actions={}, **initkwargs):
        return super().as_view(
            actions=actions, **initkwargs)

    @list_route()
    def list(self, request):
        return Response(self._list_schema(request))

    @list_route()
    def detail(self, request):
        return Response(self._detail_schema(request))

    @list_route()
    def update(self, request):
        return Response(self._update_schema(request))

    def _schema_type_for(self, field):
        type_label = field.type_label
        if type_label in ('boolean', 'integer', 'string'):
            return type_label
        elif type_label == 'float':
            return 'number'
        elif isinstance(field, ChoiceField):
            choice_stored, choice_presentation = field.choices[-1]
            if isinstance(choice_stored, str):
                return 'string'
            if isinstance(choice_stored, int):
                return 'integer'
        elif isinstance(field, (DateTimeField, EmailField)):
            return 'string'
        elif isinstance(field, PrimaryKeyRelatedField):
            return 'integer'
        elif isinstance(field, HyperlinkedRelatedField):
            return 'string'
        elif isinstance(field, HyperlinkedIdentityField):
            return 'string'
        raise Exception(u'schema_type_for not handling %r' % field)

    def _extract_schema_data(self, request):
        serializer = self.schema_for()
        model = serializer.opts.model
        # basename = model._meta.object_name.lower()
        modelname = model.__name__
        description = dedent(model.__doc__)
        rw_properties = {}
        ro_properties = {}
        required = []
        for name, field in serializer.get_fields().items():
            # FIXME: need to decide format for specifying JSON Schema for
            # method fields...
            if isinstance(field, SerializerMethodField):
                continue
            if getattr(field, 'required', False):
                required.append(name)
            data = {}
            data['description'] = getattr(field, 'help_text', '')
            data['type'] = self._schema_type_for(field)
            if isinstance(field, ChoiceField):
                # RelatedField also provides choices; don't enumerate those...
                data['enum'] = [
                    stored for stored, presentation
                    in field.choices
                ]
            if getattr(field, 'max_length', None) is not None:
                data['maxLength'] = field.max_length
            if getattr(field, 'min_length', None) is not None:
                data['minLength'] = field.min_length
            if isinstance(field, DateTimeField):
                data['format'] = 'date-time'
            if isinstance(field, EmailField):
                data['format'] = 'email'
            if isinstance(field, PrimaryKeyRelatedField):
                opts = field.queryset.model._meta
                rel_basename = '{}-{}'.format(
                    opts.app_label, opts.object_name.lower())
                rel_href = reverse(
                    '{}-list'.format(rel_basename), request=request) + '{$}/'
                rel_targetschema = reverse(
                    'schema-{}-detail'.format(rel_basename), request=request)
                data['links'] = [
                    {
                        'rel': 'full',
                        'href': rel_href,
                        'targetSchema': {
                            '$ref': rel_targetschema,
                        }
                    }
                ]
            if field.read_only:
                data['readOnly'] = True
                ro_properties[name] = data
            else:
                rw_properties[name] = data
        return {
            'modelname': modelname,
            'description': description,
            'rw_properties': rw_properties,
            'ro_properties': ro_properties,
            'required': required,
        }

    def _get_absolute_urls(self, request):
        serializer = self.schema_for()
        model = serializer.opts.model
        basename = '{}-{}'.format(
            self.app_name,
            model._meta.object_name.lower()
        )
        list_url = reverse(
            '{}-list'.format(basename), request=request)
        instance_url = list_url + '{id}/'
        list_schema_url = reverse(
            'schema-{}-list'.format(basename), request=request) + '#'
        detail_schema_url = reverse(
            'schema-{}-detail'.format(basename), request=request) + '#'
        update_schema_url = reverse(
            'schema-{}-update'.format(basename), request=request) + '#'
        return {
            'list': list_url,
            'instance': instance_url,
            'list_schema': list_schema_url,
            'detail_schema': detail_schema_url,
            'update_schema': update_schema_url,
        }

    def _update_schema(self, request):
        # urls = self._get_absolute_urls(request)
        data = self._extract_schema_data(request)
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': '{} updatable fields'.format(data['modelname']),
            'description': data['description'],
            'type': 'object',
            'properties': data['rw_properties'],
            'required': [e for e in data['required']
                         if e in data['rw_properties']],
        }

    def _detail_schema(self, request):
        urls = self._get_absolute_urls(request)
        data = self._extract_schema_data(request)
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': '{}'.format(data['modelname']),
            'description': data['description'],
            'type': 'object',
            'allOf': [
                {
                    '$ref': urls['update_schema'],
                }
            ],
            'properties': data['ro_properties'],
            'required': [e for e in data['required']
                         if e in data['ro_properties']],
            'links': [
                {
                    'rel': 'self',
                    'href': urls['instance'],
                    'method': 'GET',
                    'targetSchema': {
                        '$ref': '#',
                    },
                },
                {
                    'rel': 'update',
                    'href': urls['instance'],
                    'method': 'PUT',
                    'schema': {
                        '$ref': urls['update_schema'],
                    },
                    'targetSchema': {
                        '$ref': '#',
                    },
                },
                {
                    'rel': 'delete',
                    'href': urls['instance'],
                    'method': 'DELETE',
                }
            ]
        }

    def _list_schema(self, request):
        urls = self._get_absolute_urls(request)
        data = self._extract_schema_data(request)
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': '{} list'.format(data['modelname']),
            'description': data['description'],
            'type': 'object',
            'allOf': [
                {
                    "$ref": "/static/pagination.json#",  # TODO: global URI
                },
            ],
            'properties': {
                'results': {
                    'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        '$ref': urls['instance'],
                    }
                }
            },
            'required': ['results'],
            'links': [
                {
                    'rel': 'full',
                    'href': urls['list'],
                    'method': 'GET',
                    'targetSchema': {
                        '$ref': '#',
                    },
                },
                {
                    'rel': 'create',
                    'href': urls['list'],
                    'method': 'POST',
                    'schema': {
                        '$ref': urls['update_schema'],
                    },
                    'targetSchema': {
                        '$ref': urls['detail_schema'],
                    },
                },
            ],
        }


class BulkCreateModelMixin(object):
    """
    CustomModelMixin class for bulk creation of objects
    """
    # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
    def bulk_create(self, request):
        serializer = self.get_serializer(
            data=request.DATA, files=request.FILES, many=True)
        if serializer.is_valid():
            for obj in serializer.object:
                self.pre_save(obj)
            objects = serializer.save(force_insert=True)
            for obj in objects:
                self.post_save(obj, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def bulk_list(self, request):
        return self.list(request)
