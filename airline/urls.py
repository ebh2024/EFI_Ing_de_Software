from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='airline/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('register/', views.register, name='register'),

    path('flights/', views.flight_list, name='flight_list'),
    path('flights/create/', views.flight_create, name='flight_create'),
    path('flights/update/<int:pk>/', views.flight_update, name='flight_update'),
    path('flights/delete/<int:pk>/', views.flight_delete, name='flight_delete'),
]
