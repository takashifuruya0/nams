from web.models import *
import requests
from django.contrib.auth.models import User
import logging
logger = logging.getLogger('django')


def stock():
    try:
        url = "https://www.fk-management.com/drm/asset/stock/?limit=200&offset=0"
        r = requests.get(url)
        data = r.json()
        for d in data['results']:
            d.pop("pk")
            d['is_trust'] = False if len(d['code']) == 4 else True
            Stock.objects.create(**d)
        result = True
    except Exception as e:
        logger.error(e)
        result = False
    finally:
        return result


def order():
    try:
        user = User.objects.first()
        url = "https://www.fk-management.com/drm/asset/order/?limit=200&offset=0"
        r = requests.get(url)
        data = r.json()
        logger.info("========data========")
        logger.info(data)
        for d in data['results']:
            stock = Stock.objects.get(code=d['stock']['code'])
            d['stock'] = stock
            d['val'] = d['price']
            d['is_simulated'] = False
            d['is_buy'] = True if d['order_type'] == "現物買" else False
            d['user'] = user
            d.pop("pk")
            d.pop('price')
            d.pop('order_type')
            d.pop('chart')
            logger.info("========d========")
            logger.info(d)
            o = Order.objects.create(**d)
            # entry
            if not o.stock.is_trust and o.is_buy:
                ed = {
                    "user": user,
                    "stock": stock,
                    "is_simulated": False,
                    "is_nisa": d['is_nisa'],
                }
                entry = Entry.objects.create(**ed)
                o.entry = entry
                o.save()
        result = True
    except Exception as e:
        logger.error(e)
        result = False
    finally:
        return result

    # d = {
    #     "datetime": None,
    #     "order_type": "",
    #     "stock": {
    #         "code": "",
    #         "name": "",
    #         "industry": "",
    #         "market": ""
    #     },
    #     "num": None,
    #     "price": None,
    #     "commission": None,
    #     "is_nisa": False,
    #     "chart": None
    # }


def init():
    # delete
    Order.objects.all().delete()
    Entry.objects.all().delete()
    Stock.objects.all().delete()
    # stock
    s = stock()
    if s:
        logger.info("Stocks were migrated")
        # order and entry
        o = order()
        if o:
            logger.info("Orders were migrated")
            w = ReasonWinLoss.objects.create(is_win=True, reason="W_0_default")
            l = ReasonWinLoss.objects.create(is_win=False, reason="L_0_default")
            if w and l:
                logger.info("ReasonWinLoss were created")
