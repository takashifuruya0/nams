from django.core.management.base import BaseCommand
from web.models import Stock
from web.functions import asset_lib
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Record StockFinancialData by scraping kabuoji3'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        stocks = Stock.objects.filter(is_trust=False)
        for s in stocks:
            d = asset_lib.register_stock_financial_data(s.code)
            msg = "Result of record_stock_financial_data for {}: {}".format(s, d)
            self.stdout.write(self.style.SUCCESS(msg))
