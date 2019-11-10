# nams/tasks/__init__.py
from ..celery import app
from web.models import Stock, StockValueData
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
    # stocks = Stock.objects.filter(is_trust=False)
    # for s in stocks:
    try:
        data = asset_scraping.kabuoji3(code)
        if data['status']:
            stock = Stock.objects.get(code=code)
            for d in data['data']:
                if StockValueData.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                    StockValueData.objects.create(
                        stock=stock,
                        date=d[0],
                        val_open=d[1],
                        val_high=d[2],
                        val_low=d[3],
                        val_close=d[4],
                        turnover=d[5],
                    )
        logger.info('StockValueData of {} are updated'.format(stock))
        return True
    except Exception as e:
        logger.error(e)
        return False



