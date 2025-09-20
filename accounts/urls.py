from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.sign_up_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # مسیر خروج از سیستم
    path('verify_email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('password_reset/', views.request_password_reset, name='password_reset'),
    path('password_reset_code/', views.reset_password, name='password_reset_code'),
    path('verify_code/<int:user_id>/', views.verify_code, name='verify_code'),
    path('login/', auth_views.LoginView.as_view(), name='login'),  # استفاده از ویو پیش‌فرض جنگو برای لاگین

]
