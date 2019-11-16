# coding:utf-8

import logging
logger = logging.getLogger("django")
from web.models import Order, Stock, StockFinancialData, StockValueData
from web.models import Entry, ReasonWinLoss, AssetStatus
# django-rest-framework
from django_filters import rest_framework as dfilters
from rest_framework import viewsets
from api.serializer import OrderSerializer, StockSerializer, ReasonWinLossSerializer
from api.serializer import StockValueDataSerializer, StockFinancialDataSerializer
from api.serializer import EntrySerializer


# filter
class OrderFilter(dfilters.FilterSet):
    stock = dfilters.ModelChoiceFilter(queryset=Stock.objects.all())

    class Meta:
        fields = ("stock",)
        model = Order


class StockValueDataFilter(dfilters.FilterSet):
    stock = dfilters.ModelChoiceFilter(queryset=StockValueData.objects.all())

    class Meta:
        fields = ('stock',)
        model = StockValueData


# viewset
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('date')
    serializer_class = OrderSerializer
    filter_class = OrderFilter


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class StockValueDataViewSet(viewsets.ModelViewSet):
    queryset = StockValueData.objects.all().order_by('date', 'stock')
    serializer_class = StockValueDataSerializer


class StockFinancialDataViewSet(viewsets.ModelViewSet):
    queryset = StockFinancialData.objects.all().order_by('date', 'stock')
    serializer_class = StockFinancialData


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
