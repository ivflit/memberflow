from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', views.TenantTokenRefreshView.as_view(), name='auth-token-refresh'),
    path('invite/', views.SendInviteView.as_view(), name='auth-invite'),
    path('invite/accept/', views.InviteAcceptView.as_view(), name='auth-invite-accept'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
]
