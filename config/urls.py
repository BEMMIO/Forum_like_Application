"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings

from django.contrib import admin
from django.conf.urls import url
from django.urls import path,include
from django.views import defaults as default_views


urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path('admin/', admin.site.urls),
    path('',include('dev.pages.urls',namespace='pages')),
    path('a/',include('dev.accounts.urls',namespace='accounts')),
    path('u/',include('dev.users.urls',namespace='users')),
    path('blog/',include('dev.blog.urls',namespace='blog')),
    path('search/',include('dev.search.urls',namespace='search')),


]


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns

    # Allows debug of error pages in dev.
    urlpatterns += [
        path('400/', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        path('403/', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        path('404/', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        path('500/', default_views.server_error),
    ]
