from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome'),
    path('home/', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('register/', views.register_view, name='register'),

    # Rutas para agregar, actualizar y eliminar productos
    path('product/add/', views.add_or_update_product, name='add_product'),  # Para agregar productos
    path('product/<int:product_id>/edit/', views.add_or_update_product, name='update_product'),  # Para actualizar productos
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),  # Para eliminar productos
  
    # Otras rutas relacionadas con productos
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),

    # Rutas relacionadas con carritos
    path('cart/view/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('carts/', views.view_carts, name='view_carts'),
    path('cart/<int:cart_id>/approve/', views.approve_cart, name='approve_cart'),
    path('cart/<int:cart_id>/reject/', views.reject_cart, name='reject_cart'),
    # path('reject_cart/<int:cart_id>/', views.reject_cart, name='reject_cart')


    # Rutas relacionadas con clientes
    path('customer/<int:customer_id>/info/', views.customer_info, name='customer_info'),
    
    # Ruta para el dashboard del staff
    path('staff/', views.staff_dashboard, name='staff_dashboard'),

    # Ruta para el historial de compras
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('cart_status/', views.cart_status, name='cart_status'),


    # Ruta para ver productos en el frontend del cliente
    path('view_products/', views.view_products, name='view_products'),
]
