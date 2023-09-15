from rest_framework import routers

from borrowings.views import BorrowingViewSet


app_name = "borrowings"

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet, basename="borrowings")

urlpatterns = router.urls
