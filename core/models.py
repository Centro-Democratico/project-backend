## Este archivo traduce el init.sql de Nael a modelos de Django, lo que nos permite interactuar con la base de datos usando el ORM de Django en lugar de escribir SQL directamente. Cada clase representa una tabla en la base de datos, y cada atributo de la clase representa una columna en esa tabla. Las relaciones entre tablas se manejan mediante campos como ForeignKey.

##El ORM se llama Django ORM y esta incluido con Django :p

##Revisar settings.py para ver que la base de datos esta configurada para postgresql y que la app core esta incluida en INSTALLED_APPS, lo que es necesario para que Django reconozca los modelos definidos en este archivo. (Ya lo hice pero es para que lo anoten en el tutorial)

from django.db import models

#para identificadores unicos para la BD
import uuid

class User(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username=models.CharField(max_length=100, unique=True)
    email=models.EmailField(max_length=100, unique=True)
    password_hash=models.TextField()
    is_admin=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='user'
        managed = True

class Hardware(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user=models.ForeignKey(User, on_delete=models.CASCADE)

    name=models.TextField(blank=True)
    cpu=models.CharField(max_length=255)
    gpu=models.CharField(max_length=255)
    gb_ram=models.IntegerField()
    storage_type=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='hardware'
        managed = True

class Videogame(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name=models.CharField(max_length=255)
    genre=models.CharField(max_length=255)
    developer=models.CharField(max_length=255)
    release_year=models.IntegerField(null=True, blank=True)

    class Meta:
        db_table='videogame'
        managed = True

class VideogameRequirement(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    video_game=models.ForeignKey(Videogame, on_delete=models.CASCADE)

    cpu=models.CharField(max_length=255)
    gpu=models.CharField(max_length=255)
    gb_ram=models.IntegerField(null=True, blank=True)
    target_fps=models.IntegerField(null=True, blank=True)
    resolution=models.CharField(max_length=50, null=True, blank=True)
    settings=models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table='videogame_requirement'
        managed = True

class Result(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    hardware=models.ForeignKey(Hardware, on_delete=models.CASCADE)

    benchmark_type=models.CharField(max_length=100, null=True, blank=True)
    score=models.FloatField()
    fps_avg=models.FloatField(null=True, blank=True)
    fps_min=models.IntegerField(null=True, blank=True)
    fps_max=models.IntegerField(null=True, blank=True)
    resolution=models.CharField(max_length=50, null=True, blank=True)
    settings=models.CharField(max_length=100, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='result'
        managed = True

class GameResult(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    hardware=models.ForeignKey(Hardware, on_delete=models.CASCADE)
    video_game=models.ForeignKey(Videogame, on_delete=models.CASCADE)

    fps_min=models.IntegerField(null=True, blank=True)
    fps_max=models.IntegerField(null=True, blank=True)
    fps_avg=models.FloatField(null=True, blank=True)
    resolution=models.CharField(max_length=50, null=True, blank=True)
    settings=models.CharField(max_length=100, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
            db_table='game_result'
            managed = True

# --- RF_9, RF_11, RF_13 (dvargaspa) ---

# RF_11: Catálogo global de componentes de hardware para el ranking.
# Entidad independiente de Hardware (que está ligado a un User).
# El admin puede agregar, editar y eliminar componentes desde el panel.
class HardwareComponent(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    brand=models.CharField(max_length=100)
    model=models.CharField(max_length=255)
    type=models.CharField(max_length=10)  # 'CPU' o 'GPU'
    base_specs=models.TextField(blank=True)  # descripción libre de specs base
    launch_year=models.IntegerField(null=True, blank=True)
    base_score=models.FloatField(null=True, blank=True)  # score de referencia para el ranking
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='hardware_component'
        managed=True

# RF_9, RF_13: Sesión de benchmark con métricas agregadas (promedio y máximo)
# de CPU, GPU, RAM y almacenamiento durante la prueba.
# is_anonymous=True indica que fue enviada como telemetría anónima (RF_9).
class BenchmarkSession(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    hardware=models.ForeignKey(Hardware, on_delete=models.CASCADE, null=True, blank=True)

    started_at=models.DateTimeField()
    ended_at=models.DateTimeField()

    # CPU
    cpu_avg=models.FloatField()
    cpu_max=models.FloatField()
    cpu_temp_avg=models.FloatField(null=True, blank=True)
    cpu_temp_max=models.FloatField(null=True, blank=True)

    # GPU
    gpu_avg=models.FloatField()
    gpu_max=models.FloatField()
    gpu_temp_avg=models.FloatField(null=True, blank=True)
    gpu_temp_max=models.FloatField(null=True, blank=True)

    # RAM
    ram_avg_gb=models.FloatField()
    ram_max_gb=models.FloatField()

    # Almacenamiento (MB/s)
    disk_read_avg=models.FloatField(null=True, blank=True)
    disk_write_avg=models.FloatField(null=True, blank=True)

    # Score general de la sesión
    score=models.FloatField(null=True, blank=True)

    # RF_9: True si fue enviada como telemetría anónima
    is_anonymous=models.BooleanField(default=False)

    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='benchmark_session'
        managed=True

# RF_13: Muestras individuales por intervalo de tiempo dentro de una sesión.
# Necesarias para generar la gráfica de rendimiento temporal del informe técnico.
class SessionSample(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session=models.ForeignKey(BenchmarkSession, on_delete=models.CASCADE, related_name='samples')

    timestamp_seconds=models.IntegerField()  # segundos desde el inicio de la sesión
    cpu_pct=models.FloatField()
    gpu_pct=models.FloatField()
    ram_gb=models.FloatField()
    cpu_temp=models.FloatField(null=True, blank=True)
    gpu_temp=models.FloatField(null=True, blank=True)
    disk_read=models.FloatField(null=True, blank=True)   # MB/s
    disk_write=models.FloatField(null=True, blank=True)  # MB/s

    class Meta:
        db_table='session_sample'
        managed=True
        ordering=['timestamp_seconds']

from django.db import models

# ========== MODELOS DE FPS Y HARDWARE ==========

class FPSSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # Métricas de Hardware
    cpu_avg = models.FloatField(null=True, blank=True)
    cpu_max = models.FloatField(null=True, blank=True)
    gpu_avg = models.FloatField(null=True, blank=True)
    gpu_max = models.FloatField(null=True, blank=True)
    ram_avg_gb = models.FloatField(null=True, blank=True)
    ram_max_gb = models.FloatField(null=True, blank=True)
    # Métricas de FPSQ
    fps_avg = models.FloatField(null=True, blank=True)
    fps_max = models.FloatField(null=True, blank=True)
    fps_min = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"FPSSession {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class FPSSample(models.Model):
    session = models.ForeignKey(FPSSession, on_delete=models.CASCADE, related_name='samples')
    timestamp = models.DateTimeField(auto_now_add=True)
    fps = models.FloatField()
    cpu_usage = models.FloatField(null=True, blank=True)
    gpu_usage = models.FloatField(null=True, blank=True)
    ram_usage_gb = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Sample FPS: {self.fps} (Session {self.session.id})"