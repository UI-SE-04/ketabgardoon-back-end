import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from countries.models import Nationality

# — CRUD — #

@require_GET
def nationality_list(request):
    qs = Nationality.objects.all().order_by('country')
    data = [{'id': n.id, 'country': n.country, 'country_code': n.country_code} for n in qs]
    return JsonResponse({'results': data})


@require_GET
def nationality_detail(request, pk):
    try:
        n = Nationality.objects.get(pk=pk)
    except Nationality.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse({
        'id': n.id,
        'country': n.country,
        'country_code': n.country_code,
    })


@require_POST
def nationality_create(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    country = payload.get('country')
    code    = payload.get('country_code')
    if not country or not code:
        return JsonResponse({'error': 'country and country_code are required'}, status=400)

    n = Nationality.objects.create(country=country, country_code=code)
    return JsonResponse({'id': n.id}, status=201)


@require_http_methods(['PUT', 'PATCH'])
def nationality_update(request, pk):
    try:
        n = Nationality.objects.get(pk=pk)
    except Nationality.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    if 'country' in payload:
        n.country = payload['country']
    if 'country_code' in payload:
        n.country_code = payload['country_code']
    n.save()
    return JsonResponse({'status': 'updated'})


@require_http_methods(['DELETE'])
def nationality_delete(request, pk):
    try:
        n = Nationality.objects.get(pk=pk)
    except Nationality.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    n.delete()
    return JsonResponse({'status': 'deleted'})