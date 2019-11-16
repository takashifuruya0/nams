# django-rest-framework
from rest_framework import routers
from api.views import OrderViewSet, StockViewSet, EntryViewSet

router = routers.DefaultRouter()
router.register(r'order', OrderViewSet)
router.register(r'stock', StockViewSet)
router.register(r'entry', EntryViewSet)
