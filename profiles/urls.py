from django.urls import path
from .views import UserList, UserDetail, UserLoginView, UserLogoutView, CurrentUserView

urlpatterns = [
    path('users/', UserList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('me/', CurrentUserView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('logout/', UserLogoutView.as_view()),
]