# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from web.forms import OrderForm
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@login_required
@transaction.atomic
def order_list(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                True
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return redirect('web:order_list')
    elif request.method == "GET":
        msg = request.GET
        if not settings.ENVIRONMENT == "production":
            messages.info(request, msg)
        logger.info(msg)
        orders = Order.objects.select_related().filter(user=request.user).order_by('-datetime')
        output = {
            "msg": msg,
            "user": request.user,
            "orders": orders,
        }
        return TemplateResponse(request, "web/order_list.html", output)


@login_required
def order_detail(request, order_id):
    msg = "Hello Order Detail"
    logger.info(msg)
    if not settings.ENVIRONMENT == "production":
        messages.info(request, msg)

    try:
        order = Order.objects.select_related().get(pk=order_id, user=request.user)
    except Exception as e:
        logger.error(e)
        messages.error(request, "Not found or not authorized to access it")
        return redirect('web:main')
    output = {
        "msg": msg,
        "user": request.user,
        "order": order,
    }
    return TemplateResponse(request, "web/order_detail.html", output)


@login_required
def order_edit(request, order_id):
    try:
        order = Order.objects.select_related().get(id=order_id, user=request.user)
    except Exception as e:
        logger.error(e.args)
        messages.error(request, "Not found for order_id = {}".format(order_id))
        return redirect('web:main')
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.info(request, "Order {} was updated".format(order_id))
        return redirect('web:order_detail', order_id=order_id)
    elif request.method == "GET":
        form = OrderForm(instance=order)
        output = {
            "order": order,
            "form": form,
        }
        return TemplateResponse(request, "web/order_edit.html", output)
