from django.contrib import admin
from django.urls import path,include
from users import views


urlpatterns = [
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('resetpwd/',views.ResetPwdView.as_view(),name='resetpwd'),
    path('up/',views.up),


]