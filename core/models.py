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
        managed = False

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
        managed = False
    
class Videogame(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name=models.CharField(max_length=255)
    genre=models.CharField(max_length=255)
    developer=models.CharField(max_length=255)
    release_year=models.IntegerField(null=True, blank=True)

    class Meta:
        db_table='videogame'
        managed = False

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
        managed = False

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
        managed = False

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
            managed = False
