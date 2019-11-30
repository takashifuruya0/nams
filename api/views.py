# coding:utf-8

import logging
logger = logging.getLogger("django")
from web.models import Order, Stock, StockFinancialData, StockValueData
from web.models import Entry, ReasonWinLoss, AssetStatus
from django.contrib.auth.models import User
# django-rest-framework
from django_filters import rest_framework as dfilters
from rest_framework import viewsets
from api.serializer import OrderSerializer, StockSerializer, ReasonWinLossSerializer
from api.serializer import StockValueDataSerializer, StockFinancialDataSerializer
from api.serializer import EntrySerializer, AssetStatusSerializer, UserSerializer


# filter
class StockFilter(dfilters.FilterSet):
    class Meta:
        fields = ("name", "code", "industry", "market", "is_trust")
        model = Stock


class OrderFilter(dfilters.FilterSet):
    stock = dfilters.ModelChoiceFilter(queryset=Stock.objects.all())

    class Meta:
        fields = ("stock", "stock__code",)
        model = Order


class StockValueDataFilter(dfilters.FilterSet):
    stock = dfilters.ModelChoiceFilter(queryset=Stock.objects.all())

    class Meta:
        fields = ("stock", "stock__code",)
        model = StockValueData


class StockFinancialDataFilter(dfilters.FilterSet):
    stock = dfilters.ModelChoiceFilter(queryset=Stock.objects.all())

    class Meta:
        fields = ("stock", "stock__code",)
        model = StockFinancialData


class EntryFilter(dfilters.FilterSet):
    stock = dfilters.ModelChoiceFilter(queryset=Stock.objects.all())

    class Meta:
        fields = ("stock", "stock__code",)
        model = Entry


class UserFilter(dfilters.FilterSet):
    class Meta:
        fields = ('username', )
        model = User


# viewset
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('datetime')
    serializer_class = OrderSerializer
    filter_class = OrderFilter


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    filter_class = StockFilter


class StockValueDataViewSet(viewsets.ModelViewSet):
    queryset = StockValueData.objects.all().order_by('date', 'stock')
    serializer_class = StockValueDataSerializer
    filter_class = StockValueDataFilter


class StockFinancialDataViewSet(viewsets.ModelViewSet):
    queryset = StockFinancialData.objects.all().order_by('date', 'stock')
    serializer_class = StockFinancialDataSerializer
    filter_class = StockFinancialDataFilter


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    filter_class = EntryFilter


class ReasonWinLossViewSet(viewsets.ModelViewSet):
    queryset = ReasonWinLoss.objects.all()
    serializer_class = ReasonWinLossSerializer


class AssetStatusViewSet(viewsets.ModelViewSet):
    queryset = AssetStatus.objects.all()
    serializer_class = AssetStatusSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # filter_class = UserFilter


