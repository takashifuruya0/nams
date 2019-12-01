from django.core.management.base import BaseCommand
from web.models import Stock, StockValueData
from web.functions import asset_scraping
import logging
logger = logging.getLogger('django')
from nams import tasks


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Record AssetStatus by coping the latest data'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        d = tasks.record_asset_status()
        msg = "Task ID: {} nams.tasks.record_asset_status".format(d.id)
        self.stdout.write(self.style.SUCCESS(msg))
