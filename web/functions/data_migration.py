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
            d['is_trust'] = False if len(d['code']) == 4 else True
            d['fkmanage_id'] = d['pk']
            d.pop('pk')
            s = Stock.objects.filter(code=d['code'])
            if s.count() == 1:
                s.update(**d)
            else:
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
            d['fkmanage_id'] = d['pk']
            d.pop('pk')
            d.pop('price')
            d.pop('order_type')
            d.pop('chart')
            os = Order.objects.filter(
                datetime=d['datetime'], stock=d['stock'],
                val=d['val'], is_buy=d['is_buy'], user=d['user']
            )
            logger.info("========d========")
            logger.info(d)
            if os.exists():
                o = os.filter(fkmanage_id=None).first()
                if o:
                    Order.objects.filter(pk=o.pk).update(**d)
                    o = Order.objects.get(pk=o.pk)
                else:
                    continue
            else:
                o = Order.objects.create(**d)
            # entry
            if not o.stock.is_trust and o.is_buy and not o.entry:
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


def reason():
    if ReasonWinLoss.objects.filter(is_win=True, reason="0_default").exists():
        ReasonWinLoss.objects.create(is_win=True, reason="0_default")
    if ReasonWinLoss.objects.filter(is_win=False, reason="0_default").exists():
        ReasonWinLoss.objects.create(is_win=False, reason="0_default")
    if ReasonWinLoss.objects.filter(is_win=True, reason="1_底値掴み"):
        ReasonWinLoss.objects.create(is_win=True, reason="1_底値掴み")
    if ReasonWinLoss.objects.filter(is_win=True, reason="2_売り逃げ"):
        ReasonWinLoss.objects.create(is_win=True, reason="2_売り逃げ")
    if ReasonWinLoss.objects.filter(is_win=True, reason="3_急騰"):
        ReasonWinLoss.objects.create(is_win=True, reason="3_急騰")
    if ReasonWinLoss.objects.filter(is_win=False, reason="1_高値掴み"):
        ReasonWinLoss.objects.create(is_win=False, reason="1_高値掴み")
    if ReasonWinLoss.objects.filter(is_win=False, reason="2_売り逃し"):
        ReasonWinLoss.objects.create(is_win=False, reason="2_売り逃し")
    if ReasonWinLoss.objects.filter(is_win=False, reason="3_急落"):
        ReasonWinLoss.objects.create(is_win=False, reason="3_急落")
    w = True
    l = True
    return w,l


def init(delete=False):
    # delete
    if delete:
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
            w, l = reason()
            if w and l:
                logger.info("ReasonWinLoss were created")
