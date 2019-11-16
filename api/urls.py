# django-rest-framework
from rest_framework import routers
from api.views import OrderViewSet, StockViewSet, EntryViewSet
from api.views import ReasonWinLossViewSet, StockFinancialDataViewSet
from api.views import AssetStatusViewSet, StockValueDataViewSet
from api.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'order', OrderViewSet)
router.register(r'stock', StockViewSet)
router.register(r'entry', EntryViewSet)
router.register(r'stock_value_data', StockValueDataViewSet)
router.register(r'stock_financial_data', StockFinancialDataViewSet)
router.register(r'reason_win_loss', ReasonWinLossViewSet)
router.register(r'asset_status', AssetStatusViewSet)
router.register(r'user', UserViewSet)
