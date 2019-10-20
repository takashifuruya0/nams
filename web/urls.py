# coding:utf-8
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from web.views import views_main

app_name = 'web'
urlpatterns = [
    # dashboard
    url(r'^$', views_main.main, name='main'),
    # test
    url(r'^test$', views_main.test, name='test'),

]

