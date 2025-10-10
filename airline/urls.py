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

    path('passengers/', views.passenger_list, name='passenger_list'),
    path('passengers/create/', views.passenger_create, name='passenger_create'),
    path('passengers/update/<int:pk>/', views.passenger_update, name='passenger_update'),
    path('passengers/delete/<int:pk>/', views.passenger_delete, name='passenger_delete'),
    path('passengers/<int:pk>/history/', views.passenger_flight_history, name='passenger_flight_history'),
]
