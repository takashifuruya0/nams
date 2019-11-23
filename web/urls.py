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
    # entry
    url(r'^entry/$', views_main.entry_list, name='entry_list'),
    url(r'^entry/(?P<entry_id>\d+)/$', views_main.entry_detail, name='entry_detail'),
    url(r'^entry/(?P<entry_id>\d+)/edit$', views_main.entry_detail, name='entry_edit'),
    # order
    url(r'^order/(?P<order_id>\d+)/$', views_main.order_detail, name='order_detail'),
    url(r'^order/(?P<order_id>\d+)/edit$', views_main.order_detail, name='order_edit'),

]

