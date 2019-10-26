from web.models import *
import requests
from django.contrib.auth.models import User


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
        print("{}".format(e))
        result = False
    finally:
        return result


def order():
    try:
        user = User.objects.first()
        url = "https://www.fk-management.com/drm/asset/order/?limit=200&offset=0"
        r = requests.get(url)
        data = r.json()
        for d in data['results']:
            d['stock'] = Stock.objects.get(code=d['stock']['code'])
            d['val'] = d['price']
            d['is_simulated'] = False
            d['is_buy'] = True if d['order_type'] == "現物買" else False
            d['user'] = user
            d.pop("pk")
            d.pop('price')
            d.pop('order_type')
            d.pop('chart')
            o = Order.objects.create(**d)
            # entry
            if not o.stock.is_trust and o.is_buy:
                ed = {
                    "user": user,
                    "stock": o.stock,
                    "is_simulated": False,
                    "is_nisa": o.is_nisa,
                }
                entry = Entry.objects.create(**ed)
                o.entry = entry
                o.save()
        result = True
    except Exception as e:
        print("{}".format(e))
        result = False
    finally:
        return result

    d = {
        "datetime": None,
        "order_type": "",
        "stock": {
            "code": "",
            "name": "",
            "industry": "",
            "market": ""
        },
        "num": None,
        "price": None,
        "commission": None,
        "is_nisa": False,
        "chart": None
    }


def init():
    # stock
    s = stock()
    if s:
        print("Stocks were migrated")
        # order and entry
        o = order()
        if o:
            print("Orders were migrated")
            w = ReasonWinLoss.objects.create(is_win=True, reason="W_0_default")
            l = ReasonWinLoss.objects.create(is_win=False, reason="L_0_default")
            if w and l:
                print("ReasonWinLoss were created")
