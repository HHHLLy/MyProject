from django.urls import path
from . import  views
urlpatterns = [
    path('',views.doc_index,name='doc_index'),
    path('<int:doc_id>/', views.DocDownload.as_view(), name='doc_download'),


]
