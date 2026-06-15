from django.contrib import admin
from django.urls import path
from core.views import (
    videogame_list, videogame_detail,
    component_list, component_detail,
    telemetry_submit,
    session_list, session_report,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Videogames (existente)
    path('videogames/', videogame_list),
    path('videogames/<uuid:pk>/', videogame_detail),

    # RF_11 – Gestionar componentes del ranking global
    path('components/', component_list),
    path('components/<uuid:pk>/', component_detail),

    # RF_9 – Telemetría anónima
    path('telemetry/', telemetry_submit),

    # RF_13 – Historial e informe técnico de sesiones
    path('sessions/', session_list),
    path('sessions/<uuid:pk>/report/', session_report),
]