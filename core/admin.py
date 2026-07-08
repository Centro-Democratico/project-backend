from django.contrib import admin
from .models import FPSSession, FPSSample, BenchmarkSession

# Registramos los modelos para que aparezcan en el panel visual
admin.site.register(FPSSession)
admin.site.register(FPSSample)
admin.site.register(BenchmarkSession)