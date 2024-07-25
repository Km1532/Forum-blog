from django.urls import path
from . import views
from blog.views import pageNotFound, save_draft
from .views import PostsByTag,category_posts,CategoryListView,CategoryCreateView,CategoryUpdateView,CategoryDeleteView,manage_tags

urlpatterns = [
    path('', views.BlogHome.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('addpage/', views.AddPage.as_view(), name='add_page'),
    path('save_draft/', views.save_draft, name='save_draft'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('post/<slug:post_slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:post_slug>/delete/', views.delete_post, name='delete_post'),
    path('category/<slug:cat_slug>/', views.WomenCategory.as_view(), name='category'),
    path('add_comment/<slug:post_slug>/', views.add_comment, name='add_comment'),
    path('add_like/<slug:post_slug>/', views.add_like, name='add_like'),
    path('post/<slug:post_slug>/like_comment/<int:comment_id>/', views.add_like_comment, name='add_like_comment'),
    path('post/<slug:post_slug>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('post/<slug:post_slug>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('soon/', views.soon_page, name='soon_page'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.UserProfile.as_view(), name='user_profile'),
    path('post/<slug:post_slug>/like/', views.toggle_like, name='toggle_like'),
    path('post/<slug:post_slug>/dislike/', views.toggle_dislike, name='toggle_dislike'),
    path('post/<slug:post_slug>/comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('post/<slug:post_slug>/comment/<int:comment_id>/dislike/', views.toggle_comment_dislike, name='toggle_comment_dislike'),
    path('drafts/', views.drafts, name='drafts'),
    path('draft/<int:pk>/delete/', views.delete_draft, name='delete_draft'),
    path('draft/<int:pk>/edit/', views.edit_draft, name='edit_draft'),
    path('tag/<slug:tag_slug>/', PostsByTag.as_view(), name='posts_by_tag'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('category/<int:pk>/posts/', category_posts, name='category_posts'),
    path('manage_tags/', manage_tags, name='manage_tags'),
]

handler404 = 'blog.views.pageNotFound'