from django.urls import path,include
from . import views
urlpatterns = [
    path('index/',views.IndexView.as_view(),name='admin_index'),
    path('tag/',views.TagManagerView.as_view(),name='admin_tags_manage'),
    path('tags/<int:tag_id>/',views.TagEditView.as_view(),name='admin_tags_edit'),
    path('tags/',views.TagManagerView.as_view(),name='admin_tags_add'),
    path('hotnews/',views.HotNewsManagerView.as_view(),name='admin_hotnews'),
    path('hotnews/<int:hn_id>/',views.HotNewsEditView.as_view(),name='admin_hotnews_del'),
    path('hotnews/add/',views.HotNewsAddView.as_view(),name='admin_hotnews_add'),
    path('tags/<int:tag_id>/news/',views.HotNewsGetView.as_view(),name='admin_hotnews_get'),

    path('news/',views.NewsManageView.as_view(),name='admin_news_manage'),
    path('news/pub/',views.NewsPubView.as_view(),name='admin_news_pub'),
    path('news/edit/<int:news_id>/',views.NewsEditView.as_view(),name='admin_news_edit'),
    path('news/images/',views.NewsUploadImage.as_view(),name='admin_news_upload_image'),
    path('token/',views.UpToken.as_view(),name='admin_token'),
    path('markdown/images/', views.MarkDownUpImageView.as_view(), name='markdown_image_upload'),

    path('banners/',views.BannerEditView.as_view(),name='admin_banner_edit'),
    path('banners/<int:banner_id>/',views.BannerEditView.as_view(),name='admin_banner_del'),
    path('banners/add/',views.BannerAddView.as_view(),name='admin_banner_add'),
    path('banners/tags/<int:tag_id>/news/',views.BannerOfNewsByTagView.as_view(),name='admin_banner_tag_news'),

    path('docs/',views.DocsManageView.as_view(),name='admin_docs_manage'),
    path('docs/pub/',views.DocsPubView.as_view(),name='admin_docs_pub'),
    path('docs/edit/<int:doc_id>',views.DocsEditView.as_view(),name='admin_docs_edit'),
    path('docs/<int:doc_id>/',views.DocsEditView.as_view(),name='admin_docs_del'),
    path('docs/files/',views.DocsUploadFileView.as_view(),name='admin_docs_upload'),

    path('courses/',views.CoursesManageView.as_view(),name='admin_course_manage'),
    path('courses/pub/',views.CoursesPubView.as_view(),name='admin_course_pub'),
    path('courses/<int:course_id>/',views.CoursesEditView.as_view(),name='admin_course_edit'),

    path('groups/',views.GroupManageView.as_view(),name='admin_group_manage'),
    path('groups/<int:group_id>/',views.GroupEditView.as_view(),name='admin_group_del'),
    path('groups/<int:group_id>/',views.GroupEditView.as_view(),name='admin_group_edit'),
    path('groups/add/',views.GroupsAddView.as_view(),name='admin_group_add'),
    path('users/',views.UsersManageView.as_view(),name='admin_user_manage'),
    path('users/<int:user_id>/',views.UsersEditView.as_view(),name='admin_user_edit'),
    # path('users/<int:user_id>/',views.UsersEditView.as_view(),name='admin_user_del'),

    path('test/',views.test,{'name':'aaa'}),
]