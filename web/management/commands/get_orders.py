from django.core.management.base import BaseCommand
from web.models import Stock, StockValueData
from web.functions import asset_scraping
import logging
logger = logging.getLogger('django')
from nams import tasks


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Record StockValueData by scraping kabuoji3'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        res = tasks.get_orders.delay()
        msg = "Task ID: {}".format(res.id)
        self.stdout.write(self.style.SUCCESS(msg))
        # return d
        # stocks = Stock.objects.filter(is_trust=False)
        # for s in stocks:
        #     try:
        #         data = asset_scraping.kabuoji3(s.code)
        #         StockValueData.objects.create(
        #             stock=s,
        #             date=data[0],
        #             val_open=data[1],
        #             val_high=data[2],
        #             val_low=data[3],
        #             val_close=data[4],
        #             turnover=data[5],
        #         )
        #     except Exception as e:
        #         self.stderr.write("{}".format(e))
        #         logger.error("{}".format(e))
        # if smsg != "":
        #     self.stdout.write(self.style.SUCCESS(smsg))
        #     logger.info(smsg)
        # else:
        #     self.stderr.write(emsg)
        #     logger.error(emsg)