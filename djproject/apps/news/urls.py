from django.urls import path
from . import views
urlpatterns = [
    path('index/',views.IndexView.as_view(),name='index'),
    path('news/',views.NewsListView.as_view(),name='news'),
    path('news/banners/',views.NewsBannerView.as_view(),name='banner'),
    path('<int:news_id>/',views.NewsDetailView.as_view(),name='news_detail'),
    path('<int:news_id>/comments/',views.NewsCommentsView.as_view(),name='news_comment'),
    path('search/',views.SearchView(),name='search'),
    path('basehtmlcourse/',views.BaseHtmlView.as_view(),name='basehtml'),
    path('comments/<int:news_id>/<int:comment_id>/del/',views.NewsCommentsDelView.as_view(),name='comment_del'),
    path('weather/',views.BaseHtmlWeather.as_view(),name='get_default_weather'),
    path('city/weather/',views.BaseHtmlWeather.as_view(),name='get_city_weather')




]