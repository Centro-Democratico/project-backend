from django.contrib import admin
from django.urls import path
from core import views

from core.views import (
    receive_fps_sample, videogame_list, videogame_detail,
    component_list, component_detail,
    telemetry_submit,
    session_list, session_report,
    session_compare,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # RF_10 – Gestionar videojuegos
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

    # RF_6 – Comparar resultados con dispositivos estándar
    path('sessions/<uuid:pk>/compare/', session_compare),

    path('api/benchmark/fps/', views.submit_fps_session, name='submit_fps_session'),
    path('api/fps-samples/', receive_fps_sample, name='receive_fps_sample'),
]