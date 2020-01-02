from django.core.management.base import BaseCommand
from web.models import Stock, StockValueData
from web.functions import asset_lib
from datetime import date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Record StockValueData by scraping kabuoji3'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        stocks = Stock.objects.all()
        today = date.today()
        for s in stocks:
            if not StockValueData.objects.filter(stock=s, date=today).exists():
                d = asset_lib.register_stock_value_data_alt(s.code)
                msg = "Result of record_stock_value_data for {}: {}".format(s, d)
                self.stdout.write(self.style.SUCCESS(msg))
