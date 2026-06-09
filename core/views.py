import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Videogame, HardwareComponent, BenchmarkSession, SessionSample


# =============================================================================
# VIDEOGAMES (existente)
# =============================================================================

def _videogame_to_dict(game):
    return {
        'id': str(game.id),
        'name': game.name,
        'genre': game.genre,
        'developer': game.developer,
        'release_year': game.release_year,
    }

def _videogame_list_get(request):
    games = list(Videogame.objects.values('id', 'name', 'genre', 'developer', 'release_year'))
    for g in games:
        g['id'] = str(g['id'])
    return JsonResponse(games, safe=False)

def _videogame_list_create(request):
    data = json.loads(request.body)
    game = Videogame.objects.create(
        name=data['name'],
        genre=data['genre'],
        developer=data['developer'],
        release_year=data.get('release_year'),
    )
    return JsonResponse(_videogame_to_dict(game), status=201)

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def videogame_list(request):
    handlers = {
        'GET': _videogame_list_get,
        'POST': _videogame_list_create,
    }
    return handlers[request.method](request)

def _videogame_get(request, game):
    return JsonResponse(_videogame_to_dict(game))

def _videogame_update(request, game):
    data = json.loads(request.body)
    game.name = data.get('name', game.name)
    game.genre = data.get('genre', game.genre)
    game.developer = data.get('developer', game.developer)
    game.release_year = data.get('release_year', game.release_year)
    game.save()
    return JsonResponse(_videogame_to_dict(game))

def _videogame_delete(request, game):
    game.delete()
    return JsonResponse({'mensaje': 'Videogame Deleted'}, status=200)

@csrf_exempt
@require_http_methods(['GET', 'PUT', 'DELETE'])
def videogame_detail(request, pk):
    game = get_object_or_404(Videogame, pk=pk)
    handlers = {
        'GET': _videogame_get,
        'PUT': _videogame_update,
        'DELETE': _videogame_delete,
    }
    return handlers[request.method](request, game)


# =============================================================================
# RF_11 – GESTIONAR COMPONENTES DEL RANKING GLOBAL (dvargaspa)
# =============================================================================

def _component_to_dict(c):
    return {
        'id': str(c.id),
        'brand': c.brand,
        'model': c.model,
        'type': c.type,
        'base_specs': c.base_specs,
        'launch_year': c.launch_year,
        'base_score': c.base_score,
        'created_at': c.created_at.isoformat(),
        'updated_at': c.updated_at.isoformat(),
    }

def _is_admin(request):
    """Provisional hasta que el equipo implemente autenticación real."""
    return request.headers.get('X-User-Admin', '').lower() == 'true'

def _require_admin(request):
    if not _is_admin(request):
        return JsonResponse({'error': 'Forbidden: admin access required'}, status=403)
    return None

def _component_list_get(request):
    components = list(HardwareComponent.objects.all())
    return JsonResponse([_component_to_dict(c) for c in components], safe=False)

def _component_list_create(request):
    forbidden = _require_admin(request)
    if forbidden:
        return forbidden
    data = json.loads(request.body)
    component = HardwareComponent.objects.create(
        brand=data['brand'],
        model=data['model'],
        type=data['type'],
        base_specs=data.get('base_specs', ''),
        launch_year=data.get('launch_year'),
        base_score=data.get('base_score'),
    )
    return JsonResponse(_component_to_dict(component), status=201)

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def component_list(request):
    handlers = {
        'GET': _component_list_get,
        'POST': _component_list_create,
    }
    return handlers[request.method](request)

def _component_get(request, component):
    return JsonResponse(_component_to_dict(component))

def _component_update(request, component):
    forbidden = _require_admin(request)
    if forbidden:
        return forbidden
    data = json.loads(request.body)
    component.brand = data.get('brand', component.brand)
    component.model = data.get('model', component.model)
    component.type = data.get('type', component.type)
    component.base_specs = data.get('base_specs', component.base_specs)
    component.launch_year = data.get('launch_year', component.launch_year)
    component.base_score = data.get('base_score', component.base_score)
    component.save()
    return JsonResponse(_component_to_dict(component))

def _component_delete(request, component):
    forbidden = _require_admin(request)
    if forbidden:
        return forbidden
    component.delete()
    return JsonResponse({'mensaje': 'Component deleted'}, status=200)

@csrf_exempt
@require_http_methods(['GET', 'PUT', 'DELETE'])
def component_detail(request, pk):
    component = get_object_or_404(HardwareComponent, pk=pk)
    handlers = {
        'GET': _component_get,
        'PUT': _component_update,
        'DELETE': _component_delete,
    }
    return handlers[request.method](request, component)


# =============================================================================
# RF_9 – ALMACENAR RESULTADOS ANÓNIMOS PARA RANKING GLOBAL (dvargaspa)
# =============================================================================

def _recalculate_ranking(session):
    """Recalcula el base_score del HardwareComponent asociado al hardware
    de la sesión, promediando todos los scores anónimos registrados."""
    if not session.hardware:
        return
    cpu_name = session.hardware.cpu
    gpu_name = session.hardware.gpu

    for component_name, component_type in [(cpu_name, 'CPU'), (gpu_name, 'GPU')]:
        try:
            component = HardwareComponent.objects.get(model__iexact=component_name, type=component_type)
        except HardwareComponent.DoesNotExist:
            continue
        sessions = BenchmarkSession.objects.filter(
            is_anonymous=True,
            hardware__cpu=cpu_name,
            hardware__gpu=gpu_name,
            score__isnull=False,
        )
        if sessions.exists():
            avg_score = sum(s.score for s in sessions) / sessions.count()
            component.base_score = round(avg_score, 2)
            component.save()

@csrf_exempt
@require_http_methods(['POST'])
def telemetry_submit(request):
    data = json.loads(request.body)
    required = ['started_at', 'ended_at', 'cpu_avg', 'cpu_max',
                'gpu_avg', 'gpu_max', 'ram_avg_gb', 'ram_max_gb']
    missing = [f for f in required if f not in data]
    if missing:
        return JsonResponse({'error': f'Missing fields: {missing}'}, status=400)

    session = BenchmarkSession.objects.create(
        hardware_id=data.get('hardware_id'),
        started_at=data['started_at'],
        ended_at=data['ended_at'],
        cpu_avg=data['cpu_avg'],
        cpu_max=data['cpu_max'],
        cpu_temp_avg=data.get('cpu_temp_avg'),
        cpu_temp_max=data.get('cpu_temp_max'),
        gpu_avg=data['gpu_avg'],
        gpu_max=data['gpu_max'],
        gpu_temp_avg=data.get('gpu_temp_avg'),
        gpu_temp_max=data.get('gpu_temp_max'),
        ram_avg_gb=data['ram_avg_gb'],
        ram_max_gb=data['ram_max_gb'],
        disk_read_avg=data.get('disk_read_avg'),
        disk_write_avg=data.get('disk_write_avg'),
        score=data.get('score'),
        is_anonymous=True,
    )
    _recalculate_ranking(session)
    return JsonResponse({'id': str(session.id), 'status': 'received'}, status=201)


# =============================================================================
# RF_13 – GENERAR INFORME TÉCNICO DETALLADO DE SESIÓN (dvargaspa)
# =============================================================================

def _session_to_dict(session):
    return {
        'id': str(session.id),
        'score': session.score,
        'is_anonymous': session.is_anonymous,
        'started_at': session.started_at.isoformat(),
        'ended_at': session.ended_at.isoformat(),
        'created_at': session.created_at.isoformat(),
    }

def _session_to_report(session):
    duration_seconds = int((session.ended_at - session.started_at).total_seconds())
    samples = list(session.samples.values(
        'timestamp_seconds', 'cpu_pct', 'gpu_pct', 'ram_gb',
        'cpu_temp', 'gpu_temp', 'disk_read', 'disk_write',
    ))
    peak_events = [
        {'timestamp_seconds': s['timestamp_seconds'], 'type': 'CPU_PEAK', 'value': s['cpu_pct']}
        for s in samples if s['cpu_pct'] and s['cpu_pct'] >= 90
    ] + [
        {'timestamp_seconds': s['timestamp_seconds'], 'type': 'GPU_PEAK', 'value': s['gpu_pct']}
        for s in samples if s['gpu_pct'] and s['gpu_pct'] >= 90
    ]
    hardware_info = {}
    if session.hardware:
        hardware_info = {
            'cpu': session.hardware.cpu,
            'gpu': session.hardware.gpu,
            'gb_ram': session.hardware.gb_ram,
            'storage_type': session.hardware.storage_type,
        }
    return {
        'session_id': str(session.id),
        'generated_at': session.created_at.isoformat(),
        'started_at': session.started_at.isoformat(),
        'ended_at': session.ended_at.isoformat(),
        'duration_seconds': duration_seconds,
        'score': session.score,
        'hardware': hardware_info,
        'metrics': {
            'cpu': {'avg': session.cpu_avg, 'max': session.cpu_max,
                    'temp_avg': session.cpu_temp_avg, 'temp_max': session.cpu_temp_max},
            'gpu': {'avg': session.gpu_avg, 'max': session.gpu_max,
                    'temp_avg': session.gpu_temp_avg, 'temp_max': session.gpu_temp_max},
            'ram': {'avg_gb': session.ram_avg_gb, 'max_gb': session.ram_max_gb},
            'disk': {'read_avg': session.disk_read_avg, 'write_avg': session.disk_write_avg},
        },
        'timeline': samples,
        'peak_events': peak_events,
    }

@csrf_exempt
@require_http_methods(['GET'])
def session_list(request):
    sessions = BenchmarkSession.objects.order_by('-created_at')
    return JsonResponse([_session_to_dict(s) for s in sessions], safe=False)

@csrf_exempt
@require_http_methods(['GET'])
def session_report(request, pk):
    session = get_object_or_404(BenchmarkSession, pk=pk)
    return JsonResponse(_session_to_report(session))