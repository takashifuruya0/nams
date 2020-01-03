# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from web.forms import EntryForm
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, StockValueData
from web.functions import asset_scraping, asset_analysis
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
def entry_list(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                # entryの統合
                pks = request.POST.getlist('pk')
                entrys = Entry.objects.prefetch_related('order_set').filter(pk__in=pks, user=request.user)
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
        if not settings.ENVIRONMENT == "production":
            messages.info(request, msg)
        logger.info(msg)
        entrys = Entry.objects.prefetch_related('order_set').select_related().filter(user=request.user).order_by('-pk')
        if request.GET.get("is_closed", False):
            entrys = entrys.filter(is_closed=True)
        elif request.GET.get("is_open", False):
            entrys = entrys.filter(is_closed=False)
        output = {
            "msg": msg,
            "user": request.user,
            "entrys": entrys,
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
                entry = Entry.objects.get(pk=entry_id,  user=request.user)
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
        # production以外ではmsg表示
        if not settings.ENVIRONMENT == "production":
            messages.info(request, msg)
        logger.info(msg)
        try:
            # 各種情報取得
            entry = Entry.objects.prefetch_related('order_set')\
                .select_related().get(pk=entry_id, user=request.user)
            orders_unlinked = Order.objects.filter(entry=None, stock=entry.stock).order_by('datetime')
            orders_linked = entry.order_set.all().order_by('datetime')
            edo = entry.date_open().date()
            edc = entry.date_close().date() if entry.is_closed else date.today()
            # days日のマージンでグラフ化範囲を指定
            days = 60
            od = edo - relativedelta(days=days)
            cd = edc + relativedelta(days=days) if entry.is_closed else date.today()
            svds = StockValueData.objects.filter(stock=entry.stock, date__gt=od, date__lt=cd).order_by('date')
            df = asset_analysis.prepare(svds)
            df_check = asset_analysis.check(df)
            df_trend = asset_analysis.get_trend(df)
            # グラフ化範囲のデータ数
            svds_count = svds.count()
            # 日付とindex番号の紐付け
            date_list = dict()
            for i, svd in enumerate(svds):
                date_list[svd.date.__str__()] = i
            # 売買注文のグラフ化
            bos_detail = [None for i in range(svds_count)]
            sos_detail = [None for i in range(svds_count)]
            for o in entry.order_set.all():
                order_date = str(o.datetime.date())
                if order_date in list(date_list.keys()):
                    if o.is_buy:
                        bos_detail[date_list[order_date]] = o.val*10000 if entry.stock.is_trust else o.val
                    else:
                        sos_detail[date_list[order_date]] = o.val*10000 if entry.stock.is_trust else o.val
        except Exception as e:
            logger.error(e)
            messages.error(request, "Not found or not authorized to access it")
            if not settings.ENVIRONMENT == "production":
                messages.add_message(request, messages.ERROR, e.args)
                messages.add_message(request, messages.ERROR, type(e))
                # messages.info(list(date_list[order_date].keys()))
            return redirect('web:main')
        output = {
            "msg": msg,
            "user": request.user,
            "entry": entry,
            "orders_unlinked": orders_unlinked,
            "orders_linked": orders_linked,
            "svds": svds,
            "bos_detail": bos_detail,
            "sos_detail": sos_detail,
            "od": od,
            "cd": cd,
            "df": df,
            "df_check": df_check,
            "df_trend": df_trend,
        }
        # openの場合、現在情報を取得
        if not entry.is_closed:
            overview = asset_scraping.yf_detail(entry.stock.code)
            if overview['status']:
                output['overview'] = overview['data']
        logger.info(output)
        return TemplateResponse(request, "web/entry_detail.html", output)


@login_required
def entry_edit(request, entry_id):
    try:
        entry = Entry.objects.get(id=entry_id, user=request.user)
    except Exception as e:
        logger.error(e.args)
        messages.error(request, "Not found for entry_id = {}".format(entry_id))
        return redirect("web:main")
    if request.method == "POST":
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.info(request, "Entry {} was updated".format(entry_id))
        return redirect('web:entry_detail', entry_id=entry_id)
    elif request.method == "GET":
        form = EntryForm(instance=entry)
        output = {
            "entry": entry,
            "form": form
        }
        return TemplateResponse(request, "web/entry_edit.html", output)


# Create your views here.
@method_decorator(login_required, name='dispatch')
class EntryList(PaginationMixin, ListView):
    model = Entry
    ordering = ['pk']
    paginate_by = 20
    template_name = 'web/entry_list.html'

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        msg = self.request.GET
        if not settings.ENVIRONMENT == "production":
            messages.info(self.request, msg)
        logger.info(msg)
        res["msg"] = msg
        res["user"] = self.request.user
        return res

    def get_queryset(self):
        queryset = Entry.objects.prefetch_related('order_set').select_related().filter(user=self.request.user).order_by('-pk')
        if self.request.GET.get("is_closed", False):
            queryset = queryset.filter(is_closed=True)
        elif self.request.GET.get("is_open", False):
            queryset = queryset.filter(is_closed=False)
        return queryset

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # entryの統合
                pks = request.POST.getlist('pk')
                entrys = Entry.objects.prefetch_related('order_set').filter(pk__in=pks, user=request.user)
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
            return self.get(request, *args, **kwargs)
