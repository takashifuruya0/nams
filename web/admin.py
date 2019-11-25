from django.contrib import admin
from .models import Stock, StockFinancialData, AssetStatus
from .models import StockValueData, Order, Entry, ReasonWinLoss


# Register your models here.
class StockAdmin(admin.ModelAdmin):
    list_display = ['pk', 'is_trust', 'code', 'name', 'market', 'industry', "fkmanage_id"]
    list_filter = ['market', 'industry', ]
    search_fields = ['is_trust', 'code', 'name', ]


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = [
        'pk', "user", "date",
        "buying_power", "sum_stock", "sum_other", "sum_trust",
        "investment", "get_total",
    ]
    list_filter = ["user", "date", ]


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "is_simulated", "is_buy", "is_nisa",
        "user", "datetime", "entry", "stock",
        "num", "val", "commission",
        "chart", "chart_image", "fkmanage_id",
    ]
    list_filter = [
        "user", "datetime", "is_simulated", "is_buy", "stock__is_trust",
        "stock__name", "stock__code", "stock__industry", "stock__market",
    ]
    search_fields = ['stock__name']

    def chart_image(self, row):
        if row.chart:
            return '<img src="/document/{}" style="width:100px;height:auto;">'.format(row.chart)
        else:
            return None

    chart_image.allow_tags = True


class StockValueDataAdmin(admin.ModelAdmin):
    list_display = ['pk', "stock", "date", "val_open", "val_high", "val_low", "val_close", "turnover"]
    list_filter = ["stock__code", "stock__name", "stock__industry", "stock__market", "date", ]
    search_fields = ['stock__name']


class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'stock',
        # 'border_loss_cut', 'border_profit_determination',
        'is_closed', 'is_simulated',
        "remaining", "profit",
        'reason_win_loss', 'memo', "num_linked_orders",
    ]
    list_filter = [
        "is_closed", "is_simulated",
        "stock__name",
        "stock__code",
        "stock__industry", "stock__market",
    ]
    search_fields = ['stock__name']


class StockFinancialDataAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'stock', 'date',
        'assets',
        'eps', 'roe', 'roa', 'roa_2', 'bps',
        'pbr_f', 'per_f', 'eps_f', 'bps_f',
        'capital', 'sales',
        'equity', 'equity_ratio',
        'net_income',
        'recurring_profit',
        'operating_income',
        'dividend_yield', 'market_value',
        'interest_bearing_debt',
    ]
    list_filter = ['date', "stock__name", "stock__code", "stock__industry", "stock__market", ]
    search_fields = ['stock__name']


class ReasonWinLossAdmin(admin.ModelAdmin):
    list_display = ["pk", "reason", "is_win", ]


admin.site.register(Stock, StockAdmin)
admin.site.register(AssetStatus, AssetStatusAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(StockValueData, StockValueDataAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(StockFinancialData, StockFinancialDataAdmin)
admin.site.register(ReasonWinLoss, ReasonWinLossAdmin)