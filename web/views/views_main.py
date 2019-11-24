# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.template.response import TemplateResponse
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from web.forms import EntryForm
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, StockValueData
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@login_required
def main(request):
    msg = "Hello Django Test"
    entrys = Entry.objects.filter(user=request.user).order_by('-pk')[:10]
    logger.info(msg)
    messages.info(request, msg)
    output = {
        "msg": msg,
        "user": request.user,
        "entrys": entrys,
    }
    return TemplateResponse(request, "web/main.html", output)


@login_required
def test(request):
    msg = "Hello Django Test"
    logger.info(msg)
    messages.info(request, msg)
    output = {
        "msg": msg,
        "user": request.user,
    }
    return TemplateResponse(request, "web/main.html", output)


@login_required
@transaction.atomic
def entry_list(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                # entryの統合
                pks = request.POST.getlist('pk')
                entrys = Entry.objects.filter(pk__in=pks)
                if request.POST['post_type'] == "merge_entrys":
                    # 最初のEntry
                    first_entry = entrys.first()
                    for entry in entrys:
                        if not entry == first_entry:
                            entry.order_set.all().update(entry=first_entry)
                        if entry.remaining() == 0:
                            entry.delete()
                        else:
                            entry.save()
                    msg = "Entrys {} are merged to Entry {}".format(pks, first_entry.pk)
                    messages.success(request, msg)
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return redirect('web:entry_list')
    elif request.method == "GET":
        msg = request.GET
        logger.info(msg)
        messages.info(request, msg)
        entrys = Entry.objects.filter(user=request.user).order_by('-pk')
        if request.GET.get("is_closed", False):
            entrys = entrys.filter(is_closed=True)
        elif request.GET.get("is_open", False):
            entrys = entrys.filter(is_closed=False)
        output = {
            "msg": msg,
            "user": request.user,
            "entrys": entrys,
            # "sum_profit": sum([e.profit() for e in entrys]),
            # "count_won": sum([(1 if e.profit() > 0 else 0) for e in entrys]),
        }
        return TemplateResponse(request, "web/entry_list.html", output)


@transaction.atomic
@login_required
def entry_detail(request, entry_id):
    msg = "Hello Entry Detail"
    if request.method == "POST":
        try:
            with transaction.atomic():
                pks = request.POST.getlist('pk')
                orders = Order.objects.filter(pk__in=pks)
                entry = Entry.objects.get(pk=entry_id)
                # link_orders
                if request.POST['post_type'] == "link_orders":
                    orders.update(entry=entry)
                    msg = "Orders {} are linked to Entry {}".format(pks, entry_id)
                    entry.save()
                    messages.success(request, msg)
                # unlink_orders
                elif request.POST['post_type'] == "unlink_orders":
                    orders.update(entry=None)
                    msg = "Orders {} are unlinked from Entry {}".format(pks, entry_id)
                    entry.save()
                    messages.success(request, msg)
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return redirect('web:entry_detail', entry_id=entry_id)
    elif request.method == "GET":
        logger.info(msg)
        messages.info(request, msg)
        try:
            entry = Entry.objects.get(pk=entry_id, user=request.user)
            orders_unlinked = Order.objects.filter(entry=None, stock=entry.stock)
            edo = entry.date_open().date()
            od = edo - relativedelta(days=7)
            edc = entry.date_close().date() if entry.is_closed else date.today()
            cd = edc + relativedelta(days=7) if entry.is_closed else date.today()
            svds = StockValueData.objects.filter(stock=entry.stock, date__gt=od, date__lt=cd).order_by('date')
            svds_count = svds.count()
            date_list = dict()
            for i, svd in enumerate(svds):
                date_list[svd.date.__str__] = i
            bos_detail = [None for i in range(svds_count)]
            sos_detail = [None for i in range(svds_count)]
            for o in entry.order_set.all():
                order_date = o.datetime.date().__str__
                if o.is_buy:
                    bos_detail[date_list[order_date]] = o.val
                else:
                    sos_detail[date_list[order_date]] = o.val
        except Exception as e:
            logger.error(e)
            messages.error(request, "Not found or not authorized to access it")
            messages.add_message(request, messages.ERROR, e)
            return redirect('web:main')
        output = {
            "msg": msg,
            "user": request.user,
            "entry": entry,
            "orders_unlinked": orders_unlinked,
            "orders_linked": entry.order_set.all().order_by('datetime'),
            "svds": svds,
            "bos_detail": bos_detail,
            "sos_detail": sos_detail,
        }
        logger.info(output)
        return TemplateResponse(request, "web/entry_detail.html", output)


@login_required
def entry_edit(request, entry_id):
    if request.method == "POST":
        entry = Entry.objects.get(id=entry_id)
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.info(request, "Entry {} was updated".format(entry_id))
        return redirect('web:entry_detail', entry_id=entry_id)
    elif request.method == "GET":
        entry = Entry.objects.get(id=entry_id)
        initial = {
            "memo": entry.memo,
            "reason_win_loss": entry.reason_win_loss,
            "border_loss_cut": entry.border_loss_cut,
            "border_profit_determination": entry.border_profit_determination,
        }
        form = EntryForm(initial=initial)
        output = {
            "entry": entry,
            "form": form
        }
        return TemplateResponse(request, "web/entry_edit.html", output)


@login_required
def order_detail(request, order_id):
    msg = "Hello Order Detail"
    logger.info(msg)
    messages.info(request, msg)
    try:
        order = Order.objects.get(pk=order_id, user=request.user)
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