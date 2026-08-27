from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    RecipeListView, RecipeEditView,
    RecipeCreateView, RecipeDeleteView, RecipePrintView,PostCreate, PostEdit,
    PostDelete
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', views.logout_view, name="logout"),

    #Posts
    path('posts/', views.post_list, name="post_list"),
    path('post/create/', PostCreate.as_view(), name="post_create"),
    path('post/<slug:slug>/edit/', PostEdit.as_view(), name="post_edit"),
    path('post/<slug:slug>/delete/', PostDelete.as_view(), name="post_delete"),
    path('post/<slug:slug>/', views.post_detail, name="post_detail"),

    path('', RecipeListView.as_view(), name='recipe_list'),
    path('recipe/<int:pk>/edit/', RecipeEditView.as_view(), name='recipe_edit'),
    path('recipe/<int:pk>/view/delete', RecipeDeleteView.as_view(), name="recipe_delete"),
    path('recipe/<int:recipe_id>/print/', views.RecipePrintPDF,name='recipe_print_pdf'),
    path("recipe/<int:pk>/view/", RecipePrintView.as_view(), name="recipe_view"),


    path("ingredient/save/<int:recipe_id>/", views.save_ingredient, name="save_ingredient"),
    path("ingredient/delete/<int:ingredient_id>/", views.delete_ingredient, name = "delete_ingredient"),
    path('new/', RecipeCreateView.as_view(), name='recipe_create'),
    
    path('recipe/<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),
    path('photo/<int:photo_id>/delete', views.delete_photo, name = 'delete_photo'),
    path('about/', views.about_page, name="about"),
    path('profile/', views.profile_page, name="profile"),
    path('profile/edit/', views.profile_edit, name="profile_edit"),
    path("myrecipes/", views.recipe_list_user, name= "my_recipes"),
    
]