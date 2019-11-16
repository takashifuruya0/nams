from web.functions import asset_scraping
from web.models import StockFinancialData, Stock
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


