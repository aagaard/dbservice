from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        RedirectView.as_view(url=reverse_lazy('api-v1-root')),
        name='api-current-version'),

    url(r'^api/v1/', include('dbservice.api_v1')),

    # login/logout for browsable API
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),

    # POST email, password; receive token for use in
    # "Authorization: JWT $token" header
    url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api-token-verify/', 'rest_framework_jwt.views.verify_jwt_token'),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '', url(r'^__debug__/', include(debug_toolbar.urls)),
    )
