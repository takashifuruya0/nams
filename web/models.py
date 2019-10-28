from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import User
# from django.utils import timezone
# Create your models here.


class Stock(models.Model):
    objects = None
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=40)
    is_trust = models.BooleanField()
    market = models.CharField(max_length=30, blank=True, null=True)
    industry = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return "({}) {}".format(self.code, self.name)


class StockValueData(models.Model):
    objects = None
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    val_high = models.FloatField()
    val_low = models.FloatField()
    val_open = models.FloatField()
    val_close = models.FloatField()
    turnover = models.FloatField()

    def __str__(self):
        return "{}_{}".format(self.date, self.stock)


class ReasonWinLoss(models.Model):
    objects = None
    reason = models.CharField(max_length=40)
    is_win = models.BooleanField()

    def __str__(self):
        return "{}".format(self.reason)


class Entry(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    border_loss_cut = models.FloatField(blank=True, null=True)
    border_profit_determination = models.FloatField(blank=True, null=True)
    reason_win_loss = models.ForeignKey(ReasonWinLoss, on_delete=models.CASCADE, blank=True, null=True)
    memo = models.TextField(max_length=400, blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    is_simulated = models.BooleanField()
    is_nisa = models.BooleanField()

    def __str__(self):
        return "E{:0>3}_{}".format(self.pk, self.stock)

    def num_orders(self):
        return self.order_set.count()

    def remaining(self):
        orders = self.order_set.all()
        remaining = 0
        for o in orders:
            if o.is_buy:
                remaining += o.num
            else:
                remaining -= o.num
        return remaining

    def profit(self):
        profit = 0
        if self.is_closed:
            orders = self.order_set.all()
            for o in orders:
                if o.is_buy:
                    profit -= (o.num * o.val + o.commission)
                else:
                    profit += (o.num * o.val - o.commission)
        return profit


class Order(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.now)
    is_nisa = models.BooleanField(default=False)
    is_buy = models.BooleanField()
    is_simulated = models.BooleanField()
    num = models.IntegerField()
    val = models.FloatField()
    commission = models.IntegerField()
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=True, blank=True)
    chart = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        bs = "B" if self.is_buy else "S"
        return "{}_{}_{}".format(bs, self.datetime, self.stock)


class AssetStatus(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    buying_power = models.IntegerField()
    investment = models.IntegerField()
    nisa_power = models.IntegerField()
    sum_stock = models.IntegerField()
    sum_trust = models.IntegerField()
    sum_other = models.IntegerField()

    def __str__(self):
        return "{}_{}".format(self.date, self.user)

    def get_total(self):
        return self.sum_other + self.sum_stock + self.sum_trust


class StockFinancialData(models.Model):
    objects = None
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    """ stock_settlement_info """
    interest_bearing_debt = models.FloatField(blank=True, null=True, verbose_name="有利子負債")
    roa = models.FloatField(blank=True, null=True, verbose_name="ROA")
    roe = models.FloatField(blank=True, null=True, verbose_name="ROE")
    sales = models.FloatField(blank=True, null=True, verbose_name="売上高")
    assets = models.FloatField(blank=True, null=True, verbose_name="総資産")
    eps = models.FloatField(blank=True, null=True, verbose_name="EPS")
    net_income = models.FloatField(blank=True, null=True, verbose_name="当期利益")
    bps = models.FloatField(blank=True, null=True, verbose_name="BPS")
    roa_2 = models.FloatField(blank=True, null=True, verbose_name="総資産経常利益率")
    operating_income = models.FloatField(blank=True, null=True, verbose_name="営業利益")
    equity_ratio = models.FloatField(blank=True, null=True, verbose_name="自己資本比率")
    capital = models.FloatField(blank=True, null=True, verbose_name="資本金")
    recurring_profit = models.FloatField(blank=True, null=True, verbose_name="経常利益")
    equity = models.FloatField(blank=True, null=True, verbose_name="自己資本")
    """ stock_finance_info() """
    pbr_f = models.FloatField(blank=True, null=True, verbose_name="PBR（実績）")
    eps_f = models.FloatField(blank=True, null=True, verbose_name="EPS（会社予想）")
    market_value = models.FloatField(blank=True, null=True, verbose_name="時価総額")
    per_f = models.FloatField(blank=True, null=True, verbose_name="PER（会社予想）")
    dividend_yield = models.FloatField(blank=True, null=True, verbose_name="配当利回り（会社予想）")
    bps_f = models.FloatField(blank=True, null=True, verbose_name="BPS実績")

    def __str__(self):
        return "{}_{}".format(self.date, self.stock)