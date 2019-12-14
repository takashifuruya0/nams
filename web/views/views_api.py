# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse, HttpResponse
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
import json
from django.contrib import messages
from django.db import transaction
from web.functions import asset_scraping, asset_lib
from web.models import Entry, Order, Stock, StockValueData

# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@transaction.atomic
def order(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                val = json.loads(request.body.decode())
                logger.info("request_json: {}".format(val))
                o = Order()
                o.datetime = val["datetime"]
                o.order_type = val["kind"]
                o.is_buy = True if o.order_type == "現物買" else False
                # Stocksにデータがない→登録
                if Stock.objects.filter(code=val["code"]).__len__() == 0:
                    stockinfo = asset_scraping.yf_detail(val["code"])
                    if stockinfo['status']:
                        stock = Stock()
                        stock.code = val["code"]
                        stock.name = stockinfo['data']['name']
                        stock.industry = stockinfo['data']['industry']
                        stock.market = stockinfo['data']['market']
                        stock.is_trust = False if len(str(stock.code)) == 4 else True
                        stock.save()
                    # kabuoji3よりデータ取得
                    if stock.is_trust:
                        # 投資信託→スキップ
                        pass
                    else:
                        # 株→登録
                        data = asset_scraping.kabuoji3(stock.code)
                        if data['status']:
                            # 取得成功時
                            for d in data['data']:
                                # (date, stock)の組み合わせでデータがなければ追加
                                if StockValueData.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                                    svd = StockValueData()
                                    svd.stock = stock
                                    svd.date = d[0]
                                    svd.val_open = d[1]
                                    svd.val_high = d[2]
                                    svd.val_low = d[3]
                                    svd.val_close = d[4]
                                    svd.turnover = d[5]
                                    svd.save()
                            logger.info('StockValueData of "%s" are updated' % stock.code)
                        else:
                            # 取得失敗時
                            logger.error(data['msg'])
                        # StockFinancialInfoを登録
                        check = asset_scraping.yf_profile(stock.code)
                        if check:
                            logger.info("StockFinancialData of {} was saved.".format(stock.code))

                    smsg = "New stock was registered:{}".format(stock.code)
                else:
                    stock = Stock.objects.get(code=val["code"])
                    smsg = "This stock has been already registered:{}".format(stock.code)
                logger.info(smsg)
                o.stock = stock
                o.num = val["num"]
                o.value = val["price"]
                o.is_nisa = False
                o.commission = asset_lib.get_commission(o.num * o.value)
                o.save()
                logger.info("New Order is created: {}".format(o))
                # order時のholding stocks, asset status の変更
                res = asset_lib.order_process(o, request.user)
                # message
                d = {
                    "is_nisa": o.is_nisa,
                    "commission": o.commission,
                    "val": o.val,
                    "num": o.num,
                    "datetime": str(o.datetime),
                    "is_buy": o.is_buy,
                    "stock": {
                        "code": o.stock.code,
                        "name": o.stock.name,
                    }
                }
                data = {
                    "status": True,
                    "data": d,
                }
                messages.success(request, "Done")
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
            return response
    elif request.method == "GET":
        data = {
            "status": False,
            "message": "Please use POST method"
        }
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
        return response
