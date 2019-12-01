# nams/tasks/__init__.py
from datetime import date
from django.contrib.auth.models import User
from ..celery import app
from web.models import Stock, StockValueData, AssetStatus, StockFinancialData
from web.functions import asset_scraping
import logging
logger = logging.getLogger('django')
# celery -A nams worker -c 2 -l info


@app.task()
def minus_numbers(a, b):
    print('Request: {}-{}={}'.format(a, b, a - b))
    return a - b


@app.task()
def add_numbers(a, b):
    print('Request: {}+{}={}'.format(a, b, a + b))
    return a + b


@app.task()
def record_stock_value_data(code):
    '''
    record_stock_value_data
    :desc: kabuoji3からHLOCTを取得し、StockValueDataに格納
    :param code: 銘柄コード
    :return: StockValueDataの追加数等
    '''
    # for result
    counter = 0
    list_added = list()
    # main process
    data = asset_scraping.kabuoji3(code)
    stock = Stock.objects.get(code=code)
    if data['status']:
        for d in data['data']:
            if StockValueData.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                counter += 1
                s = StockValueData.objects.create(
                    stock=stock,
                    date=d[0],
                    val_open=d[1],
                    val_high=d[2],
                    val_low=d[3],
                    val_close=d[4],
                    turnover=d[5],
                )
                list_added.append(s.date.__str__())
        logger.info('StockValueData of {} are updated'.format(stock))
    result = {
        "counter": counter,
        "stock": {
            "name": stock.name,
            "code": stock.code,
        },
        "list": list_added,
    }
    return result


@app.task()
def record_asset_status():
    '''
    record_asset_status
    :desc: 最終日のレコードを取得して、日付を今日に変更して作成
    :param: Null
    :return: True
    '''
    users = User.objects.all()
    for u in users:
        asset_status = AssetStatus.objects.filter(user=u)
        if asset_status.exists():
            logger.info("Started for {}".format(u.username))
            asset_status = asset_status.latest('date')
            asset_status.pk = None
            asset_status.date = date.today()
            asset_status.save()
            logger.info("Done for {}".format(u.username))
        else:
            logger.info("Not found for {}".format(u.username))
    return True


@app.task()
def record_stock_financial_data(code):
    '''
    record_stock_financial_data
    :desc: yahoo finance からデータ取得し、StockFinancialDataに格納
    :param code: 銘柄コード
    :return: 追加結果等
    '''
    data = asset_scraping.yf_profile(code, is_consolidated=True)
    if data['status']:
        stock = Stock.objects.get(code=code)
        for d in data['data']:
            if StockFinancialData.objects.filter(stock=stock, date=d['決算発表日']).__len__() == 0:
                sfd = StockFinancialData()
    result = {}
    return result
