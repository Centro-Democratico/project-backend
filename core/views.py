import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Videogame

# GET /videogames/  → listar todos
# POST /videogames/ → crear uno nuevo
@csrf_exempt
def videogame_list(request):
    if request.method == 'GET':
        games = list(Videogame.objects.values('id', 'name', 'genre', 'developer', 'release_year'))
        for g in games:
            g['id'] = str(g['id'])  # UUID → string
        return JsonResponse(games, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        game = Videogame.objects.create(
            name=data['name'],
            genre=data['genre'],
            developer=data['developer'],
            release_year=data.get('release_year')
        )
        return JsonResponse({'id': str(game.id), 'name': game.name, 'genre': game.genre,
                             'developer': game.developer, 'release_year': game.release_year}, status=201)

# GET /videogames/<id>/    → obtener uno
# PUT /videogames/<id>/    → actualizar
# DELETE /videogames/<id>/ → eliminar
@csrf_exempt
def videogame_detail(request, pk):
    try:
        game = Videogame.objects.get(pk=pk)
    except Videogame.DoesNotExist:
        return JsonResponse({'error': 'Videogame not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'id': str(game.id), 'name': game.name, 'genre': game.genre,
                             'developer': game.developer, 'release_year': game.release_year})

    elif request.method == 'PUT':
        data = json.loads(request.body)
        game.name = data.get('name', game.name)
        game.genre = data.get('genre', game.genre)
        game.developer = data.get('developer', game.developer)
        game.release_year = data.get('release_year', game.release_year)
        game.save()
        return JsonResponse({'id': str(game.id), 'name': game.name, 'genre': game.genre,
                             'developer': game.developer, 'release_year': game.release_year})

    elif request.method == 'DELETE':
        game.delete()
        return JsonResponse({'mensaje': 'Videogame Deleted'}, status=200)