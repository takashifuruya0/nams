# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.conf import settings
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from web.forms import OrderForm
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, Stock, StockValueData, StockFinancialData
# list view, pagination
from django.views.generic import ListView
from pure_pagination.mixins import PaginationMixin
from django.utils.decorators import method_decorator
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@login_required
@transaction.atomic
def stock_list(request):
    if request.method == "POST":
        return redirect('web:stock_list')
    elif request.method == "GET":
        msg = request.GET
        if not settings.ENVIRONMENT == "production":
            messages.info(request, msg)
        logger.info(msg)
        stocks = Stock.objects.all()
        output = {
            "msg": msg,
            "user": request.user,
            "stocks": stocks
        }
        return TemplateResponse(request, "web/stock_list.html", output)


@login_required
def stock_detail(request, stock_code):
    msg = "Hello Stock Detail"
    logger.info(msg)
    if not settings.ENVIRONMENT == "production":
        messages.info(request, msg)

    try:
        stock = Stock.objects.prefetch_related('entry_set', "order_set").get(code=stock_code)
        svds = StockValueData.objects.filter(stock=stock, date__gte=(date.today()-relativedelta(months=6))).order_by('date')
        sfds = StockFinancialData.objects.filter(stock=stock).order_by('date')
    except Exception as e:
        logger.error(e)
        messages.error(request, "Not found or not authorized to access it")
        return redirect('web:main')
    output = {
        "msg": msg,
        "stock": stock,
        "svds": svds,
        "sfds": sfds,
    }
    return TemplateResponse(request, "web/stock_detail.html", output)


@login_required
def stock_edit(request, stock_code):
    try:
        stock = Stock.objects.prefetch_related('entry_set', "order_set").get(code=stock_code)
    except Exception as e:
        logger.error(e.args)
        messages.error(request, "Not found or not authorized to access it")
        return redirect('web:main')
    if request.method == "POST":
        return redirect('web:stock_detail', stock_code=stock_code)
    elif request.method == "GET":
        output = {
            "stock": stock,
        }
        return TemplateResponse(request, "web/stock_edit.html", output)


@method_decorator(login_required, name='dispatch')
class StockList(PaginationMixin, ListView):
    model = Stock
    ordering = ['code']
    paginate_by = 20
    template_name = 'web/stock_list.html'

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res

    def get_queryset(self):
        queryset = Stock.objects.all().order_by('code')
        return queryset

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                pass
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return self.get(request, *args, **kwargs)
