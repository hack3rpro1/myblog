from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # User-related URLs
    path('register/', views.register, name='register'),  # User registration
    path('profile/', views.profile, name='profile'),  # User profile
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Optional logout route

    # Post-related URLs
    path('', views.post_list, name='post_list'),  # List of posts (both university-wide and college-specific)
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),  # View details of a post
    path('post/create/', views.post_create, name='post_create'),  # Create a new post (restricted to admin)
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),  # Edit an existing post (restricted to post author or admin)
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),  # Delete a post (restricted to post author or admin)
]
