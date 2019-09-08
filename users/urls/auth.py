'''
djoser.urls.base registers the user view set in this manner:

    router = DefaultRouter()
    router.register("users", views.UserViewSet)
    User = get_user_model()

The default basename is deduced from the model, and is therefore 'user'.
In this app, we need to change that to 'auth-user'
So that for view names we can have 
'auth-user-list' and 'auth-user-detail' for the djoser part...
Which then frees up 'user-list' and 'user-detail' for our user app
'''
from rest_framework.routers import DefaultRouter

from djoser import views as djoser_views


authuser_router = DefaultRouter()
authuser_router.register('users', djoser_views.UserViewSet, 'auth-user')

urlpatterns = authuser_router.urls
