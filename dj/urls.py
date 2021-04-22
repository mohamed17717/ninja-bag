from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

# from app.views import home
# from toolsframe.views import home

urlpatterns = [
  # path('', home, name='homepage'),
  path('', include('toolsframe.urls', namespace='toolsframe')),
  path('t/', include('tools.urls', namespace='tools')),
  path('account/', include('accounts.urls', namespace='accounts')),

  path('app/', include('app.urls', namespace='app')),
  path('admin/', admin.site.urls),
]

if settings.DEBUG:
  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
