from django.urls import include, path
from rest_framework import routers

from payments.views.payments import PaymentViewSet


router = routers.SimpleRouter()
router.register(r"", PaymentViewSet, basename="payments")

urlpatterns = [path("", include(router.urls))]
