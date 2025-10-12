"""
URL configuration for airline_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airline.api_views import (
    AirplaneViewSet, FlightViewSet, PassengerViewSet, ReservationViewSet,
    SeatLayoutViewSet, SeatTypeViewSet, SeatLayoutPositionViewSet,
    FlightHistoryViewSet, TicketViewSet
)

router = DefaultRouter()
router.register(r'airplanes', AirplaneViewSet)
router.register(r'flights', FlightViewSet)
router.register(r'passengers', PassengerViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'seatlayouts', SeatLayoutViewSet)
router.register(r'sealtypes', SeatTypeViewSet)
router.register(r'seatlayoutpositions', SeatLayoutPositionViewSet)
router.register(r'flighthistories', FlightHistoryViewSet)
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('airline.urls')),
    path('api/', include(router.urls)),
]
