from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('groups', views.EsusuGroupViewSet, basename='esusugroup')
router.register('future-tenures', views.FutureTenureViewSet, basename='futuretenure')

urlpatterns = [
    path('', include(router.urls)),
]
