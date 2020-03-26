from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.course_list,name='course_index'),
    path('<int:course_id>',views.Course_detail.as_view(),name='course_detail')
]