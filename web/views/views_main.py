# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.template.response import TemplateResponse
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from web.forms import InvestmentForm
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, StockValueData, Stock, AssetStatus
from web.functions import asset_scraping
from django_celery_results.models import TaskResult
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@login_required
def main(request):
    if request.method == "GET":
        msg = "Hello Django Test"
        entrys = Entry.objects.filter(user=request.user).order_by('-pk')[:5]
        astatus_list = AssetStatus.objects.filter(user=request.user)
        astatus = astatus_list.latest('date') if astatus_list.exists() else None
        logger.info(msg)
        if not settings.ENVIRONMENT == "production":
            messages.info(request, msg)
        if request.user.is_superuser:
            tasks = TaskResult.objects.all()[:5]
        output = {
            "msg": msg,
            "user": request.user,
            "entrys": entrys,
            "tasks": tasks,
            "astatus": astatus,
            "investment_form": InvestmentForm(),
        }
        return TemplateResponse(request, "web/main.html", output)

    elif request.method == "POST":
        if request.POST['post_type'] == "investment":
            form = InvestmentForm(request.POST)
            if form.is_valid():
                astatus = AssetStatus.objects.latest('date')
                astatus.buying_power += form.cleaned_data['value']
                if form.cleaned_data['is_investment']:
                    investment_type = "Investment"
                    astatus.investment += form.cleaned_data['value']
                else:
                    investment_type = "Modification"
                astatus.save()
        messages.info(request, "Add ¥{:,} as {}".format(form.cleaned_data['value'], investment_type))
        return redirect("web:main")


@login_required
def test(request):
    msg = "Hello Django Test"
    logger.info(msg)
    messages.info(request, msg)
    code = request.GET.get("code", 1357)
    stock = Stock.objects.get(code=code)
    svds = StockValueData.objects.filter(stock__code=code).order_by('date')
    date_start = svds.first().date
    date_end = svds.last().date
    orders = Order.objects.filter(stock__code=code, datetime__lte=date_end, datetime__gte=date_start).order_by('datetime')
    output = {
        "msg": msg,
        "user": request.user,
        "stock": stock,
        "orders": orders,
        "svds": svds,
    }
    return TemplateResponse(request, "web/d3.html", output)

