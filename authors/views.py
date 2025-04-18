import json

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from authors.models import Author

# — CRUD — #

@require_GET
def author_detail(request, pk):
    try:
        author = Author.objects.get(pk=pk)
    except Author.DoesNotExist:
        return JsonResponse({'error': 'Author not found'}, status=404)
    data = {
        'id': author.id,
        'name': author.name,
        'birth_date': author.birth_date.isoformat() if author.birth_date else None,
        'nationality': author.nationality_id,
        'rating': author.rating,
        'total_sum_of_ratings': author.total_sum_of_ratings,
        'total_number_of_ratings': author.total_number_of_ratings,
        'bio': author.bio,
        'call_info': author.call_info,
        'author_photo_url': author.author_photo.url if author.author_photo else None,
        'created_at': author.created_at.isoformat(),
        'updated_at': author.updated_at.isoformat(),
    }
    return JsonResponse(data)


@require_POST
def author_create(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    # Required:
    name = payload.get('name')
    if not name:
        return JsonResponse({'error': 'Name is required'}, status=400)

    author = Author(name=name)
    # Optional fields:
    for field in ('birth_date', 'bio', 'call_info', 'total_sum_of_ratings', 'total_number_of_ratings', 'rating'):
        if field in payload:
            setattr(author, field, payload[field])
    if 'nationality' in payload:
        author.nationality_id = payload['nationality']
    author.save()

    return JsonResponse({'id': author.id}, status=201)


@require_http_methods(['PUT', 'PATCH'])
def author_update(request, pk):
    try:
        author = Author.objects.get(pk=pk)
    except Author.DoesNotExist:
        return JsonResponse({'error': 'Author not found'}, status=404)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    for field in ('name', 'birth_date', 'bio', 'call_info', 'total_sum_of_ratings', 'total_number_of_ratings', 'rating'):
        if field in payload:
            setattr(author, field, payload[field])
    if 'nationality' in payload:
        author.nationality_id = payload['nationality']

    author.save()
    return JsonResponse({'status': 'updated'})


@require_http_methods(['DELETE'])
def author_delete(request, pk):
    try:
        author = Author.objects.get(pk=pk)
    except Author.DoesNotExist:
        return JsonResponse({'error': 'Author not found'}, status=404)
    author.delete()
    return JsonResponse({'status': 'deleted'})


# — Search w/ pagination — #

@require_GET
def search_authors(request):
    name_q = request.GET.get('name', '')
    authors_qs = Author.objects.filter(name__icontains=name_q).order_by('name')

    # pagination params
    page     = request.GET.get('page', 1)
    per_page = request.GET.get('page_size', 10)
    paginator = Paginator(authors_qs, per_page)

    try:
        page_obj = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        return JsonResponse({'error': 'Invalid page'}, status=400)

    authors_list = []
    for a in page_obj:
        authors_list.append({'id': a.id, 'name': a.name, 'rating': a.rating})

    return JsonResponse({
        'results': authors_list,
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
    })


# — Rating recalculation — #

@require_POST
def recalc_author_rating(request, pk):
    try:
        author = Author.objects.get(pk=pk)
    except Author.DoesNotExist:
        return JsonResponse({'error': 'Author not found'}, status=404)

    if not author.total_number_of_ratings:
        return JsonResponse({'error': 'No ratings to recalc'}, status=400)

    author.update_rating()
    return JsonResponse({'id': author.id, 'new_rating': author.rating})


@require_POST
def recalc_all_ratings(request):
    updated = 0
    qs = Author.objects.exclude(total_number_of_ratings__in=[0, None])
    for author in qs:
        author.update_rating()
        updated += 1
    return JsonResponse({'updated_authors': updated})
