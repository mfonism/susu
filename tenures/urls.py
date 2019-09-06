from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('groups', views.EsusuGroupViewSet, basename='esusugroup')

urlpatterns = [
    path('', include(router.urls)),
]
