from django.urls import path
from .views import CloudinarySignatureView, CompleteOnboardingView, UserList, UserDetail, UserLoginView, UserLogoutView, CurrentUserView, VisitorHistoryList

urlpatterns = [
    path('users/', UserList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('me/', CurrentUserView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('logout/', UserLogoutView.as_view()),
    path('visitors/', VisitorHistoryList.as_view()),
    path('get-signature/', CloudinarySignatureView.as_view()),
    path('complete-onboarding/', CompleteOnboardingView.as_view()),
]