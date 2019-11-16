# coding: utf-8
from rest_framework import serializers
from web.models import Stock, Order, Entry, StockValueData, StockFinancialData
from web.models import ReasonWinLoss, AssetStatus


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class EntrySerializer(serializers.ModelSerializer):
    stock = StockSerializer()

    class Meta:
        model = Entry
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    stock = StockSerializer()
    entry = EntrySerializer()

    class Meta:
        model = Order
        fields = '__all__'


class StockValueDataSerializer(serializers.ModelSerializer):
    stock = StockSerializer

    class Meta:
        model = StockValueData
        fields = '__all__'


class StockFinancialDataSerializer(serializers.ModelSerializer):
    stock = StockSerializer

    class Meta:
        model = StockFinancialData
        fields = '__all__'


class AssetStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetStatus
        fields = '__all__'


class ReasonWinLossSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasonWinLoss
        fields = '__all__'

