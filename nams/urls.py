"""nams URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
# media
from django.conf import settings
from django.views.static import serve
from django.views.generic import RedirectView
# django-rest-framework
from api.urls import router
# auth
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='nams/')),
    url(r'^admin/', admin.site.urls),
    url(r'^nams/', include('web.urls', namespace='web')),
    url(r'^api/', include(router.urls)),
    url(r'^document_nams/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # login/logout
    url(r'^login$', auth_views.LoginView.as_view(template_name="web/login.html"), name="login_nams"),
    url(r'^logout$', auth_views.LogoutView.as_view(), name='logout_nams'),
]
