from django.urls import path
from .views import admin_login, admin_logout, admin_change_password, admin_dashboard, profile_settings, profile_list, profile_datatable_view, ProfileView, ProfileEditView, ProfileDeleteView, blog_list, blog_detail, blog_edit, blog_delete, comic_list, comic_detail, comic_edit, comic_delete, like_list, edit_like, delete_like, comment_list, comment_view, comment_edit, comment_delete, add_blog, add_comic, character_card_list


urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    path('admin_login/', admin_login, name='admin_login'),
    path('admin_logout/', admin_logout, name='admin_logout'),
    path('admin_change_password/', admin_change_password, name='admin_change_password'),
    path('profile_settings/', profile_settings, name='profile_settings'),
    path('profile_list/', profile_list,  name='profile_list'),
    path('ajax_datatable/profiles/', profile_datatable_view, name='profile_datatable'),
    path('profile/<int:pk>/view/', ProfileView.as_view(), name='profile_view'),
    path('profile/<int:pk>/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('profile/<int:pk>/delete/', ProfileDeleteView.as_view(), name='profile_delete' ),
    path('admin_blog_list/', blog_list, name='admin_blog_list'),
    path('admin_blog/<int:pk>/', blog_detail, name = 'admin_blog_detail'),
    path('admin_blog/<int:pk>/edit/', blog_edit, name='admin_blog_edit'),
    path('admin_blog/<int:pk>/delete/', blog_delete, name='admin_blog_delete'),
    path('admin_blog_add/', add_blog, name='admin_blog_add'),
    path('comic_list/', comic_list, name='comic_list',),
    path('admin_comic/<int:pk>/', comic_detail, name='admin_comic_detail'),
    path('admin_comic/<int:pk>/edit/', comic_edit, name='admin_comic_edit'),
    path('admin_comic/<int:pk>/delete/', comic_delete, name='admin_comic_delete'),
    path('admin_comic_add/', add_comic, name='admin_comic_add'),
    path('like_list/', like_list, name = 'like_list'),
    path('likes/edit/<int:like_id>/', edit_like, name='edit_like'),
    path('likes/delete/<int:like_id>/', delete_like, name='delete_like'),

    path('comment_list/', comment_list, name='comment_list'),
    path('comments/<int:comment_id>/view/', comment_view, name='comment_view'),
    path('comments/<int:comment_id>/edit/', comment_edit, name='comment_edit'),
    path('comments/<int:comment_id>/delete/',comment_delete, name='comment_delete'),
    path('admin_character_card', character_card_list, name='admin_character_card'),

]