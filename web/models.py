from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from web.functions import asset_scraping
# from django.utils import timezone
# Create your models here.


class Stock(models.Model):
    objects = None
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=40)
    is_trust = models.BooleanField()
    market = models.CharField(max_length=30, blank=True, null=True)
    industry = models.CharField(max_length=30, blank=True, null=True)
    fkmanage_id = models.IntegerField(null=True, blank=True, default=None)

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
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        header = "W" if self.is_win else "L"
        return "{}{}".format(header, self.reason)


class Entry(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザ")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
    border_loss_cut = models.FloatField(blank=True, null=True, verbose_name="損切価格")
    border_profit_determination = models.FloatField(blank=True, null=True, verbose_name="利確価格")
    reason_win_loss = models.ForeignKey(ReasonWinLoss, on_delete=models.CASCADE, blank=True, null=True, verbose_name="理由")
    memo = models.TextField(max_length=400, blank=True, null=True, verbose_name="メモ")
    is_closed = models.BooleanField(default=False)
    is_simulated = models.BooleanField()
    is_nisa = models.BooleanField()

    def __str__(self):
        return "E{:0>3}_{}".format(self.pk, self.stock)

    def val_order(self, is_buy):
        orders = self.order_set.filter(is_buy=is_buy)
        val = 0
        if orders.exists():
            for o in orders:
                val += (o.val * o.num)
            val = val/self.num_order(is_buy)
        return val

    def num_order(self, is_buy):
        orders = self.order_set.filter(is_buy=is_buy)
        num = 0
        if orders.exists():
            num = orders.aggregate(num=Sum('num'))['num']
        return num

    def num_buy(self):
        return self.num_order(is_buy=True)

    def num_sell(self):
        return self.num_order(is_buy=False)

    def val_buy(self):
        return self.val_order(is_buy=True)

    def val_sell(self):
        return self.val_order(is_buy=False)

    def num_linked_orders(self):
        return self.order_set.count()

    def remaining(self):
        remaining = self.num_buy() - self.num_sell()
        return remaining

    def profit(self):
        profit = 0
        orders = self.order_set.all()
        for o in orders:
            if o.is_buy:
                profit -= (o.num * o.val + o.commission)
            else:
                profit += (o.num * o.val - o.commission)
        if not self.is_closed:
            data = asset_scraping.yf_detail(self.stock.code)
            if data['status']:
                profit += data['data']['val'] * self.remaining()
        if profit > 0 and not self.is_nisa:
            profit = round(profit * 0.8)
        return profit

    def profit_pct(self):
        return round(100 + self.profit() * 100 / self.val_buy() / self.num_buy(), 1)

    def date_open(self):
        os = self.order_set.filter(is_buy=True)
        if os.exists():
            return min([o.datetime for o in os])
        else:
            return

    def date_close(self):
        os = self.order_set.filter(is_buy=False)
        if os.exists():
            return max([o.datetime for o in os])
        else:
            return

    def border_loss_cut_percent(self):
        if self.border_loss_cut:
            return round(self.border_loss_cut/self.val_buy()*100, 2)

    def border_profit_determination_percent(self):
        if self.border_profit_determination:
            return round(self.border_profit_determination/self.val_buy()*100, 2)

    def save(self, *args, **kwargs):
        self.is_closed = True if self.remaining() == 0 else False
        if self.order_set.exists():
            # same stocks should be linked
            if not self.order_set.count() == self.order_set.filter(stock=self.order_set.first().stock).count():
                raise Exception('Different stocks are linked')
            # remaining should be over 0
            if self.remaining() < 0:
                raise Exception('remaining should be over 0')
            # date_open should be earlier than date_close
            if self.is_closed and self.date_open() > self.date_close():
                raise Exception('date_open should be earlier than date_close')
        super().save(*args, **kwargs)


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
    fkmanage_id = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        bs = "B" if self.is_buy else "S"
        return "{}_{}_{}".format(bs, self.datetime, self.stock)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.entry:
            self.entry.save()


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
        return self.sum_other + self.sum_stock + self.sum_trust + self.buying_power

    def get_gp(self):
        return self.get_total() - self.investment

    def get_gpr(self):
        return round((self.get_total() - self.investment)/self.investment * 100, 2)


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


class V_Entry(models.Model):
    name = models.CharField(max_length=100)
    is_closed = models.BooleanField()
    date_open = models.DateTimeField()
    date_close = models.DateTimeField()
    period = models.IntegerField()
    buy_total = models.FloatField()
    sell_total = models.FloatField()
    commission = models.IntegerField()
    profit = models.FloatField()
    buy_num = models.IntegerField()
    buy_price = models.FloatField()
    sell_num = models.IntegerField()
    sell_price = models.FloatField()

    class Meta:
        managed = False
        db_table = "v_entry"
