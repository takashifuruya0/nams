from web.functions import asset_scraping
from web.models import StockFinancialData, Stock, Entry, AssetStatus
from django.contrib.auth.models import User
import requests
from io import BytesIO
from django.core import files
from datetime import date
import logging
logger = logging.getLogger('django')


def register_stock_financial_data(code):
    result = {
        'code': code,
        'StockFinancialData': [],
        'status': None,
    }
    try:
        # 情報取得
        detail = asset_scraping.yf_detail(code)
        profiles = asset_scraping.yf_profile(code, is_consolidated=True)
        if profiles['status'] and profiles[0]['決算期'] is None:
            # 単体の情報を取得
            profiles = asset_scraping.yf_profile(code, is_consolidated=False)
        # stock情報
        stock = Stock.objects.get(code=code)
        # 今年度を含めて３年分
        for i in range(3):
            profile = profiles[i]
            if not StockFinancialData.objects.filter(date=profile["決算発表日"], stock__code=code).exists():
                data = {
                    "stock": stock,
                    # profile
                    "date": profile["決算発表日"],
                    'equity': profile['自己資本'],
                    'equity_ratio': profile["自己資本比率"],
                    'capital': profile["資本金"],
                    'operating_income': profile["営業利益"],
                    'assets': profile["総資産"],
                    'recurring_profit': profile["経常利益"],
                    'net_income': profile["当期利益"],
                    'interest_bearing_debt': profile["有利子負債"],
                    'eps': profile["EPS（一株当たり利益）"],
                    'bps': profile["BPS（一株当たり純資産）"],
                    'sales': profile["売上高"],
                    'roa': profile["ROA（総資産利益率）"],
                    'roa_2': profile["総資産経常利益率"],
                    'roe': profile["ROE（自己資本利益率）"],
                }
                # 今年度分はdetail情報を利用
                if i == 0 and detail['status']:
                    data['market_value'] = detail['data']["時価総額"]
                    data['dividend_yield'] = detail['data']["配当利回り（会社予想）"]
                    data['bps_f'] = detail['data']["BPS（実績）"]
                    data['eps_f'] = detail['data']["EPS（会社予想）"]
                    data['pbr_f'] = detail['data']["PBR（実績）"]
                    data['per_f'] = detail['data']["PER（会社予想）"]
                # 保存
                logger.debug(data)
                sfd = StockFinancialData.objects.create(**data)
                result['StockFinancialData'].append(sfd)
        # status=Trueに設定
        result['status'] = True
    except Exception as e:
        logger.error(e)
        # status=Falseに設定
        result['status'] = False
    finally:
        return result


def get_commission(fee):
    if fee < 50000:
        return 54
    elif fee < 100000:
        return 97
    elif fee < 200000:
        return 113
    elif fee < 500000:
        return 270
    elif fee < 1000000:
        return 525
    elif fee < 1500000:
        return 628
    elif fee < 30000000:
        return 994
    else:
        return 1050


def order_process(order, user=None):
    res = {
        "status": False,
        "msg": None,
    }
    try:
        '''chart保存'''
        url_chart = "https://chart.yahoo.co.jp/?code={}.T&tm=6m&type=c&log=off&size=m&over=m25,m75&add=m,r,vm&comp=".format(order.stock.code)
        r = requests.get(url_chart)
        if r.status_code == 200:
            # file
            filename = "{}_{}.png".format(date.today(), order.stock.code)
            fp = BytesIO()
            fp.write(r.content)
            order.chart.save(filename, files.File(fp))
            logger.info("A current chart is added to {}".format(order))
        '''Status更新'''
        astatus_today = AssetStatus.objects.filter(date=date.today())
        if astatus_today:
            astatus = astatus_today[0]
        else:
            astatus = AssetStatus.objects.latest('date')
            astatus.pk = None
            astatus.date = date.today()
        '''買い注文処理'''
        if order.is_buy:
            # status更新
            astatus.buying_power = astatus.buying_power - order.num * order.val - order.commission
            # 買付余力以上は買えません
            if astatus.buying_power < 0:
                logger.error("buying_power " + str(astatus.buying_power))
                logger.error("order.num " + str(order.num))
                logger.error("order.price " + str(order.val))
                logger.error("order.commision " + str(order.commission))
                raise ValueError("buying_power < 0 !")
            if len(str(order.stock.code)) == 4:
                astatus.sum_stock += order.num * order.val
            else:
                astatus.sum_trust += order.num * order.val
            # astatus.total = astatus.buying_power + astatus.stocks_value + astatus.other_value
            astatus.save()
            logger.info("AssetStatus is updated")
            logger.info(astatus)

            #Entry作成
            entry = Entry()
            entry.user = User.objects.first() if user is None else user
            entry.stock = order.stock
            entry.border_profit_determination = int(order.val * 1.05)
            entry.border_loss_cut = int(order.val * 0.95)
            entry.save()
            order.entry = entry
            order.save()
            res['status'] = True
            res['msg'] = "Buy Order Process was done"
        # 売り
        elif order.order_type == "現物売":
            entry = Entry.objects.prefetch_related('order_set').filter(is_closed=False, stock=order.stock).last()
            # status更新
            if order.is_nisa:
                # NISA: TAX=0%
                astatus.buying_power = astatus.buying_power + order.num * order.val
                logger.info("TAX 0%:NISA")
            elif order.price - entry.val_buy() > 0:
                # 利益あり＋NISA以外: TAX=20%
                tax = (order.val - entry.val_buy()) * order.num * 0.2
                astatus.buying_power = astatus.buying_power + order.num * order.val - order.commission - tax
                logger.info("TAX 20%:Has benefit and not NISA")
            else:
                # 利益なし＋NISA以外: TAX=0%
                astatus.buying_power = astatus.buying_power + order.num * order.val - order.commission
                logger.info("TAX 0%: Has not benefit and not NISA")
            if not order.stock.is_trust:
                astatus.sum_stock -= order.num * order.val
            else:
                astatus.sum_trust -= order.num * order.val
            astatus.save()
            logger.info("AssetStatus is updated")
            logger.info(astatus)
            # entry紐付け
            if entry.remaining() >= order.num:
                order.entry = entry
                order.save()
            else:
                logger.error("entry.remaining " + str(entry.remaining()))
                logger.error("order.num " + str(order.num))
                raise ValueError("entry.remaining - order.num < 0!")
            res['status'] = True
            res['msg'] = "Sell Order Process was done"
    except Exception as e:
        logger.error(e)
        logger.error(order.__dict__)
        res['status'] = False
        res['msg'] = "Process was failed"
    finally:
        return res
