import json
from decimal import Decimal, InvalidOperation
from io import BytesIO
from urllib.parse import urlparse

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.middleware.csrf import get_token
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods
import qrcode
from qrcode.image.svg import SvgPathImage

from .models import Category, MenuItem, Restaurant, Table


User = get_user_model()


def parse_json(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode('utf-8'))


def json_error(message, status=400):
    return JsonResponse({'message': message}, status=status)


@require_GET
def health(_request):
    return JsonResponse({'status': 'ok'})


def require_admin_session(request):
    if not request.user.is_authenticated:
        return json_error('Unauthorized.', status=401)
    if not request.user.is_staff:
        return json_error('Staff access required.', status=403)
    return None


def serialize_admin(user):
    return {
        'id': user.id,
        'username': user.username,
        'name': user.get_full_name() or user.username,
    }


def serialize_category(category):
    return {
        'id': category.id,
        'name': category.name,
        'order': category.order,
    }


def serialize_menu_item(item):
    return {
        'id': item.id,
        'name': item.name,
        'category': item.category.name,
        'price': float(item.price),
        'description': item.description,
        'image': item.image,
        'available': item.available,
        'spicy': item.spicy,
        'featured': item.featured,
    }


def serialize_table(table):
    return {
        'id': table.id,
        'number': table.number,
        'label': table.label,
        'slug': table.slug,
        'path': '/',
    }


@ensure_csrf_cookie
@require_GET
def bootstrap(request):
    get_token(request)
    restaurant = Restaurant.objects.first()
    return JsonResponse(
        {
            'restaurant': {
                'name': restaurant.name,
                'tagline': restaurant.tagline,
                'currency': restaurant.currency,
                'heroMessage': restaurant.hero_message,
            }
            if restaurant
            else None,
            'categories': [serialize_category(item) for item in Category.objects.all()],
            'menuItems': [serialize_menu_item(item) for item in MenuItem.objects.select_related('category').all()],
            'tables': [serialize_table(item) for item in Table.objects.all()],
        }
    )


@require_GET
def table_qr(request, slug):
    try:
        table = Table.objects.get(slug=slug)
    except Table.DoesNotExist:
        return json_error('Table not found.', status=404)

    target = request.GET.get('target', '').strip()
    if not target:
        return json_error('QR target is required.')

    parsed_target = urlparse(target)
    if parsed_target.scheme not in {'http', 'https'} or not parsed_target.netloc:
        return json_error('QR target must be an absolute http or https URL.')
    if parsed_target.netloc != request.get_host():
        return json_error('QR target must stay on the current site.')

    qr = qrcode.QRCode(border=1, box_size=8)
    qr.add_data(target)
    qr.make(fit=True)

    image = qr.make_image(image_factory=SvgPathImage)
    output = BytesIO()
    image.save(output)
    svg = output.getvalue().decode('utf-8')

    response = HttpResponse(svg, content_type='image/svg+xml')
    response['Content-Disposition'] = f'inline; filename="{table.slug}-qr.svg"'
    return response


@require_http_methods(['POST'])
def auth_login(request):
    payload = parse_json(request)
    user = authenticate(
        request,
        username=payload.get('username', ''),
        password=payload.get('password', ''),
    )

    if not user:
        return json_error('Invalid username or password.', status=401)
    if not user.is_staff:
        return json_error('Staff access required.', status=403)

    login(request, user)
    return JsonResponse({'admin': serialize_admin(user)})


@require_GET
def auth_me(request):
    auth_error = require_admin_session(request)
    if auth_error:
        return auth_error
    return JsonResponse({'admin': serialize_admin(request.user)})


@require_http_methods(['POST'])
def auth_logout(request):
    logout(request)
    return HttpResponse(status=204)


@require_http_methods(['GET', 'POST'])
def menu_list(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        return JsonResponse({'menuItems': [serialize_menu_item(item) for item in items]})

    auth_error = require_admin_session(request)
    if auth_error:
        return auth_error

    payload = parse_json(request)
    category_name = str(payload.get('category', '')).strip()

    if not category_name:
        return json_error('Category is required.')

    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        return json_error('Choose a valid category before saving the item.')

    try:
        price = Decimal(str(payload.get('price')))
    except (InvalidOperation, TypeError):
        return json_error('Price must be a number.')

    item = MenuItem.objects.create(
        name=str(payload.get('name', '')).strip(),
        category=category,
        price=price,
        description=str(payload.get('description', '')).strip(),
        image=str(payload.get('image', '')).strip(),
        available=bool(payload.get('available')),
        spicy=bool(payload.get('spicy')),
        featured=bool(payload.get('featured')),
    )
    return JsonResponse({'menuItem': serialize_menu_item(item)}, status=201)


@require_http_methods(['PUT', 'DELETE'])
def menu_detail(request, item_id):
    auth_error = require_admin_session(request)
    if auth_error:
        return auth_error

    try:
        item = MenuItem.objects.select_related('category').get(id=item_id)
    except MenuItem.DoesNotExist:
        return json_error('Menu item not found.', status=404)

    if request.method == 'DELETE':
        item.delete()
        return HttpResponse(status=204)

    payload = parse_json(request)
    category_name = str(payload.get('category', '')).strip()

    try:
        category = Category.objects.get(name=category_name)
        price = Decimal(str(payload.get('price')))
    except Category.DoesNotExist:
        return json_error('Choose a valid category before saving the item.')
    except (InvalidOperation, TypeError):
        return json_error('Price must be a number.')

    item.name = str(payload.get('name', '')).strip()
    item.category = category
    item.price = price
    item.description = str(payload.get('description', '')).strip()
    item.image = str(payload.get('image', '')).strip()
    item.available = bool(payload.get('available'))
    item.spicy = bool(payload.get('spicy'))
    item.featured = bool(payload.get('featured'))
    item.save()

    return JsonResponse({'menuItem': serialize_menu_item(item)})


@require_http_methods(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        return JsonResponse({'categories': [serialize_category(item) for item in Category.objects.all()]})

    auth_error = require_admin_session(request)
    if auth_error:
        return auth_error

    payload = parse_json(request)
    name = str(payload.get('name', '')).strip()
    if not name:
        return json_error('Category name is required.')
    if Category.objects.filter(name__iexact=name).exists():
        return json_error('Category already exists.', status=409)

    last_order = Category.objects.order_by('-order').values_list('order', flat=True).first() or 0
    category = Category.objects.create(name=name, order=last_order + 1)
    categories = [serialize_category(item) for item in Category.objects.all()]
    return JsonResponse({'category': serialize_category(category), 'categories': categories}, status=201)


@require_http_methods(['PUT'])
def category_reorder(request):
    auth_error = require_admin_session(request)
    if auth_error:
        return auth_error

    payload = parse_json(request)
    category_ids = payload.get('categoryIds', [])
    categories = list(Category.objects.all())
    if len(category_ids) != len(categories):
        return json_error('A full category order is required.')

    for index, category_id in enumerate(category_ids, start=1):
        Category.objects.filter(id=category_id).update(order=index)

    return JsonResponse({'categories': [serialize_category(item) for item in Category.objects.all()]})


@require_http_methods(['PUT', 'DELETE'])
def category_detail(request, category_id):
    auth_error = require_admin_session(request)
    if auth_error:
        return auth_error

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return json_error('Category not found.', status=404)

    if request.method == 'DELETE':
        if category.menu_items.exists():
            return json_error('Move or remove menu items in this category first.')
        category.delete()
        return HttpResponse(status=204)

    payload = parse_json(request)
    next_name = str(payload.get('name', '')).strip()
    if not next_name:
        return json_error('Category name is required.')

    category.name = next_name
    category.save()
    return JsonResponse({'category': serialize_category(category), 'categories': [serialize_category(item) for item in Category.objects.all()]})
