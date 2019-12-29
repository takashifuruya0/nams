# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from web.views import views_main, views_entry, views_order, views_stock


app_name = 'web'
urlpatterns = [
    # dashboard
    path('', views_main.main, name='main'),
    # test
    path('test', views_main.test, name='test'),
    # entry
    # path('entry/', views_entry.entry_list, name='entry_list'),
    path('entry/', views_entry.EntryList.as_view(), name='entry_list'),
    path('entry/<int:entry_id>/', views_entry.entry_detail, name='entry_detail'),
    path('entry/<int:entry_id>/edit', views_entry.entry_edit, name='entry_edit'),
    # order
    # path('order/', views_order.order_list, name="order_list"),
    path('order/', views_order.OrderList.as_view(), name="order_list"),
    path('order/<int:order_id>/', views_order.order_detail, name='order_detail'),
    path('order/<int:order_id>/edit', views_order.order_edit, name='order_edit'),
    # stock
    # path('stock/$', views_stock.stock_list, name="stock_list"),
    path('stock/$', views_stock.StockList.as_view(), name="stock_list"),
    path('stock/<stock_code>/', views_stock.stock_detail, name='stock_detail'),
    path('stock/<stock_code>/edit', views_stock.stock_edit, name='stock_edit'),
]

