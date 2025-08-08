"""
Configuración de URL para el proyecto aerolinea_project.

La lista `urlpatterns` enruta las URLs a las vistas. Para más información, consulta:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language # Importa la vista para cambiar el idioma.

def trigger_error(request):
    division_by_zero = 1 / 0

# Definición de patrones de URL principales.
urlpatterns = [
    path('admin/', admin.site.urls), # URL para el panel de administración de Django.
    path('set_language/', set_language, name='set_language'), # URL para cambiar el idioma de la interfaz.
    path('login/', auth_views.LoginView.as_view(template_name='gestion/login.html'), name='login'), # URL para la página de inicio de sesión.
    path('logout/', auth_views.LogoutView.as_view(next_page='flight_list'), name='logout'), # URL para cerrar sesión, redirige a la lista de vuelos.
    path('sentry-debug/', trigger_error), # URL para probar la integración con Sentry.
]

# Patrones de URL que soportan internacionalización (i18n).
# Las URLs dentro de i18n_patterns tendrán un prefijo de idioma (ej. /es/, /en/).
urlpatterns += i18n_patterns(
    path('', include('gestion.urls')), # Incluye las URLs de la aplicación 'gestion'.
)



