from django.urls import path,include
from django.urls import re_path
from verifications import views
urlpatterns = [
    path('image_codes/<uuid:image_code_id>/',views.ImageView.as_view(),name="image_codes"),#将image_code_id规定为js里uuid的格式
    re_path('usernames/(?P<username>\w{5,20})/',views.CheckUsernameView.as_view(),name="check_username"),
    re_path('mobile/(?P<mobile>1[3-9]\d{9})/',views.CheckMobileView.as_view(),name="check_mobile"),
    # re_path('reset_mobile/(?P<mobile>(\w[5,20]))/',views.CheckUserView.as_view(),name="check_reset_username"),
    # re_path('reset_mobile/(?P<mobile>(1[3-9]\d{9}))/',views.CheckUserView.as_view(),name="check_reset_mobile"),
    path('reset_m/<reset_mobile>/',views.CheckResetUserView.as_view()),
    path('reset_p/',views.CheckResetPwdView.as_view()),
    path("sms_codes/",views.SmsCodesView.as_view(),name="smscode"),
    path("reset_sms_codes/",views.ResetSmsCodesView.as_view()),



    ]
