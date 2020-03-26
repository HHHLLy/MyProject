from django.urls import path
from news import views
urlpatterns = [
    path('index/',views.IndexView.as_view(),name='index'),
    path('news/',views.NewsListView.as_view(),name='news'),
    path('news/banners/',views.NewsBannerView.as_view(),name='banner'),
    path('<int:news_id>/',views.NewsDetailView.as_view(),name='news_detail'),
    path('<int:news_id>/comments/',views.NewsCommentsView.as_view(),name='news_comment'),
    path('search/',views.SearchView(),name='search')



]