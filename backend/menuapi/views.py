import json
from decimal import Decimal, InvalidOperation
from io import BytesIO
from urllib.parse import urlparse
from uuid import uuid4

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.middleware.csrf import get_token
from django.http import HttpResponse, JsonResponse
from django.utils.text import get_valid_filename
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods
import qrcode
from qrcode.image.svg import SvgPathImage

from .models import Category, MenuItem, Restaurant, Table


User = get_user_model()
ALLOWED_IMAGE_TYPES = {'image/avif', 'image/gif', 'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_IMAGE_EXTENSIONS = {'avif', 'gif', 'jpeg', 'jpg', 'png', 'webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


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


def get_requested_restaurant(request):
    slug = request.GET.get('restaurant', '').strip()
    if request.method in {'POST', 'PUT', 'PATCH'} and not slug and request.content_type == 'application/json':
        try:
            slug = parse_json(request).get('restaurantSlug', '')
        except json.JSONDecodeError:
            slug = ''

    queryset = Restaurant.objects.all()
    if slug:
        return queryset.filter(slug=slug).first()
    return queryset.order_by('id').first()


def require_restaurant_admin(request, restaurant):
    auth_error = require_admin_session(request)
    if auth_error:
        return auth_error
    if not restaurant:
        return json_error('Restaurant not found.', status=404)
    if request.user.is_superuser:
        return None
    if not restaurant.admins.filter(id=request.user.id).exists():
        return json_error('You do not have access to this restaurant.', status=403)
    return None


def serialize_admin(user):
    return {
        'id': user.id,
        'username': user.username,
        'name': user.get_full_name() or user.username,
        'isSuperuser': user.is_superuser,
        'restaurants': [
            {'id': item.id, 'name': item.name, 'slug': item.slug}
            for item in (Restaurant.objects.all() if user.is_superuser else user.restaurants.all())
        ],
    }


def serialize_category(category):
    return {
        'id': category.id,
        'restaurantSlug': category.restaurant.slug,
        'name': category.name,
        'order': category.order,
    }


def serialize_menu_item(item):
    return {
        'id': item.id,
        'restaurantSlug': item.restaurant.slug,
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
        'restaurantSlug': table.restaurant.slug,
        'number': table.number,
        'label': table.label,
        'slug': table.slug,
        'path': f'/r/{table.restaurant.slug}',
    }


def build_media_url(path):
    return default_storage.url(path)


@ensure_csrf_cookie
@require_GET
def bootstrap(request):
    get_token(request)
    restaurant = get_requested_restaurant(request)
    if not restaurant:
        return json_error('Restaurant not found.', status=404)

    return JsonResponse(
        {
            'restaurant': {
                'id': restaurant.id,
                'name': restaurant.name,
                'slug': restaurant.slug,
                'tagline': restaurant.tagline,
                'currency': restaurant.currency,
                'heroMessage': restaurant.hero_message,
            },
            'categories': [serialize_category(item) for item in restaurant.categories.all()],
            'menuItems': [
                serialize_menu_item(item)
                for item in restaurant.menu_items.select_related('category').all()
            ],
            'tables': [serialize_table(item) for item in restaurant.tables.all()],
        }
    )


@require_GET
def table_qr(request, slug):
    try:
        table = Table.objects.select_related('restaurant').get(slug=slug)
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
def upload_menu_image(request):
    restaurant = get_requested_restaurant(request)
    auth_error = require_restaurant_admin(request, restaurant)
    if auth_error:
        return auth_error

    image = request.FILES.get('image')
    if not isinstance(image, UploadedFile):
        return json_error('Choose an image file to upload.')

    filename = get_valid_filename(image.name)
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if image.content_type not in ALLOWED_IMAGE_TYPES and extension not in ALLOWED_IMAGE_EXTENSIONS:
        return json_error('Upload an AVIF, JPG, PNG, WebP, or GIF image.')

    if image.size > MAX_IMAGE_SIZE:
        return json_error('Image must be 5 MB or smaller.')

    extension = extension or 'jpg'
    saved_path = default_storage.save(f'menu-items/{uuid4().hex}.{extension}', image)

    return JsonResponse({'imageUrl': build_media_url(saved_path)}, status=201)


@require_http_methods(['POST'])
def auth_login(request):
    payload = parse_json(request)
    restaurant_slug = str(payload.get('restaurantSlug', '')).strip()
    restaurant = Restaurant.objects.filter(slug=restaurant_slug).first() if restaurant_slug else None

    if restaurant_slug and not restaurant:
        return json_error('Restaurant not found. Check the restaurant slug in the URL.', status=404)

    user = authenticate(
        request,
        username=payload.get('username', ''),
        password=payload.get('password', ''),
    )

    if not user:
        return json_error('Invalid username or password.', status=401)
    if not user.is_staff:
        return json_error('Staff access required.', status=403)
    if restaurant and not user.is_superuser and not restaurant.admins.filter(id=user.id).exists():
        return json_error('This staff user is not assigned to this restaurant.', status=403)

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
    restaurant = get_requested_restaurant(request)
    if not restaurant:
        return json_error('Restaurant not found.', status=404)

    if request.method == 'GET':
        items = restaurant.menu_items.select_related('category').all()
        return JsonResponse({'menuItems': [serialize_menu_item(item) for item in items]})

    auth_error = require_restaurant_admin(request, restaurant)
    if auth_error:
        return auth_error

    payload = parse_json(request)
    category_name = str(payload.get('category', '')).strip()

    if not category_name:
        return json_error('Category is required.')

    try:
        category = restaurant.categories.get(name=category_name)
    except Category.DoesNotExist:
        return json_error('Choose a valid category before saving the item.')

    try:
        price = Decimal(str(payload.get('price')))
    except (InvalidOperation, TypeError):
        return json_error('Price must be a number.')

    item = MenuItem.objects.create(
        name=str(payload.get('name', '')).strip(),
        restaurant=restaurant,
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
    restaurant = get_requested_restaurant(request)
    auth_error = require_restaurant_admin(request, restaurant)
    if auth_error:
        return auth_error

    try:
        item = restaurant.menu_items.select_related('category').get(id=item_id)
    except MenuItem.DoesNotExist:
        return json_error('Menu item not found.', status=404)

    if request.method == 'DELETE':
        item.delete()
        return HttpResponse(status=204)

    payload = parse_json(request)
    category_name = str(payload.get('category', '')).strip()

    try:
        category = restaurant.categories.get(name=category_name)
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
    restaurant = get_requested_restaurant(request)
    if not restaurant:
        return json_error('Restaurant not found.', status=404)

    if request.method == 'GET':
        return JsonResponse({'categories': [serialize_category(item) for item in restaurant.categories.all()]})

    auth_error = require_restaurant_admin(request, restaurant)
    if auth_error:
        return auth_error

    payload = parse_json(request)
    name = str(payload.get('name', '')).strip()
    if not name:
        return json_error('Category name is required.')
    if restaurant.categories.filter(name__iexact=name).exists():
        return json_error('Category already exists.', status=409)

    last_order = restaurant.categories.order_by('-order').values_list('order', flat=True).first() or 0
    category = Category.objects.create(restaurant=restaurant, name=name, order=last_order + 1)
    categories = [serialize_category(item) for item in restaurant.categories.all()]
    return JsonResponse({'category': serialize_category(category), 'categories': categories}, status=201)


@require_http_methods(['PUT'])
def category_reorder(request):
    restaurant = get_requested_restaurant(request)
    auth_error = require_restaurant_admin(request, restaurant)
    if auth_error:
        return auth_error

    payload = parse_json(request)
    category_ids = payload.get('categoryIds', [])
    categories = list(restaurant.categories.all())
    if len(category_ids) != len(categories):
        return json_error('A full category order is required.')

    for index, category_id in enumerate(category_ids, start=1):
        restaurant.categories.filter(id=category_id).update(order=index)

    return JsonResponse({'categories': [serialize_category(item) for item in restaurant.categories.all()]})


@require_http_methods(['PUT', 'DELETE'])
def category_detail(request, category_id):
    restaurant = get_requested_restaurant(request)
    auth_error = require_restaurant_admin(request, restaurant)
    if auth_error:
        return auth_error

    try:
        category = restaurant.categories.get(id=category_id)
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
    return JsonResponse({
        'category': serialize_category(category),
        'categories': [serialize_category(item) for item in restaurant.categories.all()],
    })
