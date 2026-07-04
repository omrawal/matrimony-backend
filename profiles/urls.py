from django.urls import path
from .views import (
    AdminManageUserPhotosView,
    AdminUserManagementView,
    AdminVerifyUserView,
    CloudinarySignatureView,
    CompleteOnboardingView,
    ManagePhotosView,
    PendingVerificationListView,
    ShortlistedUsersAPIView,
    ToggleShortlistAPIView,
    UserList,
    UserDetail,
    UserLoginView,
    UserLogoutView,
    CurrentUserView,
    ViewContactDetailsAPI,
    VisitorHistoryList,
)

urlpatterns = [
    path("users/", UserList.as_view()),
    path("users/<int:pk>/", UserDetail.as_view()),
    path("me/", CurrentUserView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("logout/", UserLogoutView.as_view()),
    path("visitors/", VisitorHistoryList.as_view()),
    path("get-signature/", CloudinarySignatureView.as_view()),
    path("complete-onboarding/", CompleteOnboardingView.as_view()),

    path("me/photos/<str:action>/", ManagePhotosView.as_view(), name="manage_photos"),
    path("me/shortlists/", ShortlistedUsersAPIView.as_view()),

    path("users/<int:user_id>/contact/", ViewContactDetailsAPI.as_view()),
    path("users/<int:user_id>/shortlist/", ToggleShortlistAPIView.as_view()),
    
    path("admin/pending-verifications/", PendingVerificationListView.as_view()),
    path("admin/verify-user/<int:user_id>/", AdminVerifyUserView.as_view()),
    path("admin/manage-users/", AdminUserManagementView.as_view()),
    path("admin/manage-users/<int:user_id>/", AdminUserManagementView.as_view()),
    path(
        "admin/manage-users/<int:user_id>/photos/<str:action>/",
        AdminManageUserPhotosView.as_view(),
    ),
]
