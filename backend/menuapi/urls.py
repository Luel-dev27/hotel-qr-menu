from django.urls import path

from .views import (
    auth_login,
    auth_logout,
    auth_me,
    bootstrap,
    category_detail,
    category_list,
    category_reorder,
    health,
    menu_detail,
    menu_list,
    table_qr,
    upload_menu_image,
)

urlpatterns = [
    path('health', health, name='health'),
    path('bootstrap', bootstrap, name='bootstrap'),
    path('tables/<slug:slug>/qr', table_qr, name='table-qr'),
    path('auth/login', auth_login, name='auth-login'),
    path('auth/me', auth_me, name='auth-me'),
    path('auth/logout', auth_logout, name='auth-logout'),
    path('menu', menu_list, name='menu-list'),
    path('menu/<int:item_id>', menu_detail, name='menu-detail'),
    path('menu/images', upload_menu_image, name='menu-image-upload'),
    path('categories', category_list, name='category-list'),
    path('categories/reorder', category_reorder, name='category-reorder'),
    path('categories/<int:category_id>', category_detail, name='category-detail'),
]
