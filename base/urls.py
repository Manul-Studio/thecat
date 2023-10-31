from django.urls import path
from . import views

urlpatterns =[ 
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('', views.home, name="home"),
    path('post/<str:pk>/', views.post, name="post"),
    # path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('profile/<str:pk>/', views.userProfile, name="profile"),
    path('profile-list/', views.listProfile, name="list-profile"),
    path('create-post/', views.createPost, name="create-post"),
    path('update-post/<str:pk>/', views.updatePost, name="update-post"),
    path('delete-post/<str:pk>/', views.deletePost, name="delete-post"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    path('like/', views.likePost, name="like-post"),



]