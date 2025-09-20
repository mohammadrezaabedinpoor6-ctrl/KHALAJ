from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list_view, name="blog_list"),
    path('<int:pk>/', views.blog_detail_view, name="blog_detail"),
    path('create/', views.blog_create_view, name="blog_create"),
    path('<int:pk>/update/', views.blog_update_view, name="blog_update"),
    path('<int:pk>/delete/', views.blog_delete_view, name="blog_delete"),
    path('comment/<int:pk>/edit/', views.comment_edit_view, name="comment_edit"),
    path('comment/<int:pk>/delete/', views.comment_delete_view, name="comment_delete"),
    path('<int:pk>/like/', views.like_blog_view, name='like_blog'),
    path('<int:pk>/like/', views.like_blog_view, name='like_blog'),
    path('comment/<int:pk>/like/', views.like_comment_view, name='like_comment'),
    path('reply/<int:comment_id>/create/', views.create_reply, name='reply_create'),
    path('reply/<int:reply_id>/edit/', views.edit_reply, name='reply_edit'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='reply_delete'),
    path('reply/<int:reply_id>/like/', views.like_reply, name='reply_like'),
]

