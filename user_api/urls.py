"""
URLs mapping for users.
"""
from django.urls import path
from .views import (
    MeView,
    RegisterAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    VerifyEmailRequestAPIView,
    VerifyEmailConfirmAPIView,

    GoogleAuth,
    GoogleAuthCallback,

    # ProfileDetailAPIView,
    UserAPIView,
    # UserUpdateAPIView
    MyProfileUpdate,
)

app_name = 'user_api'
urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('me/profile_update/', MyProfileUpdate.as_view(), name='me_profile_update'),
    # path('me/update/', UserUpdateAPIView.as_view(), name='update'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('reset-password/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('verify-email/', VerifyEmailRequestAPIView.as_view(), name='email_verify_request'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailConfirmAPIView.as_view(), name='email_verify_confirm'),

    path('google_auth/', GoogleAuth.as_view(), name='google_auth'),
    path('google_auth_callback/', GoogleAuthCallback.as_view(), name='google_auth_callback'),  # add path for google authentication
    
    path('user/<slug>/', UserAPIView.as_view(), name='user'),
    # path('user/<slug>/profile/', ProfileDetailAPIView.as_view(), name='profile'),
    
    # path('<pk>/profile', ProfileDetailAPIView.as_view(), name='profile'),
]