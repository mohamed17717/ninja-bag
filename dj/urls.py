from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from django.conf import settings
from django.conf.urls.static import static

import debug_toolbar

urlpatterns = [
  path('', include('social_django.urls', namespace='social')),
  path('logout/', LogoutView.as_view(template_name=settings.LOGOUT_REDIRECT_URL), name='logout'),

  path('', include('toolsframe.urls', namespace='toolsframe')),
  path('', include('tools.urls', namespace='tools')),
  path('account/', include('accounts.urls', namespace='accounts')),

  path('admin/', admin.site.urls),
  path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:
  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
