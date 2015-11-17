from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from rest_framework.routers import Route
from rest_framework.routers import DynamicListRoute


class AppRouter(DefaultRouter):
    def __init__(self, app_name):
        super().__init__()
        self.app_name = app_name
        self.root_view_name = '{}-root'.format(app_name)
        self.routes = [
            route._replace(name='{}-{}'.format(app_name, route.name))
            for route in self.routes
        ]
        self.routes.insert(1, Route(
            url=r'^{prefix}/bulk{trailing_slash}$',
            mapping={
                'post': 'bulk_create',
                'get': 'bulk_list'
            },
            name='{}-{{basename}}-bulk_create'.format(app_name),
            initkwargs={}
        ))

    def get_urls(self):
        urls = super().get_urls()

        if self.include_root_view:
            root_url = url(r'^$', self.get_api_root_view(),
                           name='{}-root'.format(self.app_name))
            urls[0] = root_url
        return urls


class JSONSchemaRouter(SimpleRouter):
    routes = [
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='schema-{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def get_default_base_name(self, viewset):
        model_cls = viewset.schema_for.Meta.model
        return '{}-{}'.format(
            viewset.app_name,
            model_cls._meta.object_name.lower()
        )
