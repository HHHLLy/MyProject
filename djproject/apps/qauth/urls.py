from django.urls import path
from . import  views
urlpatterns = [
    path('login/',views.QQAuthView.as_view(),name='qauth'),
    path('auth_callback',views.demo),

    ]