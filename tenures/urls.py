from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('groups', views.EsusuGroupViewSet, basename='esusugroup')
router.register('future-tenures', views.FutureTenureViewSet, basename='futuretenure')
router.register('live-tenures', views.LiveTenureViewSet, basename='livetenure')
router.register('historical-tenures', views.HistoricalTenureViewSet, basename='historicaltenure')
router.register('watches', views.WatchViewSet, basename='watch')

urlpatterns = [
    path('', include(router.urls)),
]
