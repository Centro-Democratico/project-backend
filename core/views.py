from django.shortcuts import render
from .models import Videogame

def consult_videogames(request):
    videogames_db = Videogame.objects.all().values('id', 'name', 'genre', 'developer').order_by('id')
    videogames = [{"id": str(v['id']), "name": v['name'], "genre": v['genre'], "developer": v['developer']} for v in videogames_db]
    return render(request, "index.html", {"videogames": videogames})