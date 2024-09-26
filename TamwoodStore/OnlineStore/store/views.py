from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Cart, CartItem, PurchaseHistory, PurchaseItem
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils import timezone
from django.db import transaction


def is_staff(user):
    return user.is_staff

def welcome_page(request):
    return render(request, 'index.html')

@login_required
def home(request):
    user = request.user
    if user.is_staff:
        return render(request, 'store/staff_home.html')
    else:
        return render(request, 'store/customer_home.html')

# Vistas para el personal (staff)
@login_required
@user_passes_test(is_staff)  # Solo el staff puede acceder
def add_or_update_product(request, product_id=None):
    product = get_object_or_404(Product, pk=product_id) if product_id else Product()

    if request.method == 'POST':
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.save()

        # Redirigir a la lista de productos después de agregar/actualizar
        return redirect('product_list')

    return render(request, 'store/add_or_update_product.html', {'product': product})

@login_required
@user_passes_test(is_staff)  # Solo el staff puede acceder
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return redirect('product_list')

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

@login_required
@user_passes_test(is_staff)
def view_carts(request):
    # Obtener todos los carritos que contienen productos pendientes
    carts = Cart.objects.filter(cartitem__status=CartItem.PENDING).distinct()

    # Para cada carrito, obtener solo los productos pendientes y calcular el total solo con los pendientes
    for cart in carts:
        # Filtrar solo los productos en estado "Pending"
        cart.items = CartItem.objects.filter(cart=cart, status=CartItem.PENDING)

        # Calcular el total del carrito solo con productos pendientes
        cart.total_price = sum(item.product.price * item.quantity for item in cart.items)

    return render(request, 'store/view_carts.html', {'carts': carts})


@staff_member_required
def approve_cart(request, cart_id):
    # Obtener el carrito por su ID
    cart = get_object_or_404(Cart, id=cart_id, is_approved=False)

    # Aprobar todos los productos pendientes en el carrito
    cart_items = CartItem.objects.filter(cart=cart, status=CartItem.PENDING)

    # Crear o actualizar el historial de compras del cliente
    purchase_history, created = PurchaseHistory.objects.get_or_create(
        customer=cart.customer,
        purchase_date=timezone.now(),  # Fecha de la compra
        defaults={'total_price': 0},
    )

    for item in cart_items:
        # Marcar el producto como aprobado
        item.status = CartItem.APPROVED
        item.save()

        # Agregar el producto al historial de compras
        PurchaseItem.objects.create(
            purchase=purchase_history,
            product=item.product,
            quantity=item.quantity
        )

        # Actualizar el precio total en el historial de compras solo con los productos aprobados
        purchase_history.total_price += item.product.price * item.quantity

    purchase_history.save()

    # Marcar el carrito como aprobado solo si todos los productos han sido aprobados
    cart.is_approved = True
    cart.save()

    messages.success(request, 'Cart approved and added to purchase history.')
    return redirect('view_carts')


@staff_member_required
def reject_cart(request, cart_id):
    # Obtener el carrito por su ID
    cart = get_object_or_404(Cart, id=cart_id)

    # Rechazar todos los productos pendientes en el carrito dentro de una transacción atómica
    with transaction.atomic():
        # Obtener los productos pendientes
        cart_items = CartItem.objects.filter(cart=cart, status=CartItem.PENDING)

        # Crear o actualizar el historial de compras del cliente con estado 'Denied'
        purchase_history, created = PurchaseHistory.objects.get_or_create(
            customer=cart.customer,
            status='Denied',  # Marcar como 'Denied' para los productos rechazados
            defaults={'total_price': 0},
        )

        if cart_items.exists():
            for item in cart_items:
                # Marcar el producto como rechazado
                item.status = CartItem.REJECTED
                item.save()

                # Agregar el producto rechazado al historial de compras
                PurchaseItem.objects.create(
                    purchase=purchase_history,
                    product=item.product,
                    quantity=item.quantity
                )

            # Marcar el carrito como rechazado
            cart.is_denied = True
            cart.save()

        purchase_history.save()

        messages.success(request, 'Cart rejected and added to purchase history.')

    return redirect('view_carts')



@login_required
@user_passes_test(is_staff)
def customer_info(request, customer_id):
    customer = get_object_or_404(User, pk=customer_id)
    purchase_history = PurchaseHistory.objects.filter(customer=customer)
    return render(request, 'store/customer_info.html', {'customer': customer, 'history': purchase_history})

# Vistas para los clientes
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(customer=request.user, is_approved=False)
    # Obtener la cantidad desde el formulario (si no hay, usar 1 como predeterminado)
    quantity = int(request.POST.get('quantity', 1))
    # Agregar el producto al carrito o incrementar la cantidad si ya está en el carrito
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity  # Solo incrementar si el producto ya estaba en el carrito
    else:
        cart_item.quantity = quantity  # Si es nuevo, asigna la cantidad desde el formulario
    cart_item.save()

    messages.success(request, f'Added {quantity} x {product.name} to your cart.')
    return redirect('view_products')


@login_required
def view_cart(request):
    # Obtener el carrito del usuario actual
    cart, created = Cart.objects.get_or_create(customer=request.user, is_approved=False)

    # Recuperar los items del carrito
    cart_items = CartItem.objects.filter(cart=cart)

    # Calcular el total solo con productos aprobados o pendientes
    total_cart_price = 0
    for item in cart_items:
        # Calcular el total por cada item (precio x cantidad)
        item.total_price = item.product.price * item.quantity
        total_cart_price += item.total_price  # Sumar el total al precio total del carrito

    return render(request, 'store/view_cart.html', {'cart_items': cart_items, 'cart': cart, 'total_cart_price': total_cart_price})




@login_required
def remove_from_cart(request, item_id):
    # Obtener el item del carrito que se desea eliminar
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    # Eliminar el item del carrito
    cart_item.delete()
    # Mensaje opcional para indicar que el producto fue eliminado
    messages.success(request, 'Product removed from cart successfully.')
    # Redirigir al carrito de nuevo
    return redirect('view_cart')

# @login_required
# def complete_purchase(request):
#     cart = Cart.objects.get(customer=request.user, is_approved=False)
#     total_price = cart.calculate_total()
#     purchase_history = PurchaseHistory.objects.create(
#         customer=request.user,
#         total_price=total_price
#     )
#     for product in cart.products.all():
#         purchase_history.products.add(product)
#     purchase_history.save()
#     cart.is_approved = True
#     cart.save()
#     return redirect('purchase_history')

@login_required
def purchase_history(request):
    # Obtener el historial de compras del usuario actual
    purchase_history = PurchaseHistory.objects.filter(customer=request.user).select_related('customer').prefetch_related('items__product')
    
    return render(request, 'store/purchase_history.html', {'history': purchase_history})


@login_required
def view_products(request):
    products = Product.objects.all()
    return render(request, 'store/view_products.html', {'products': products})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'store/register.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def staff_dashboard(request):
    customers = User.objects.filter(is_staff=False)
    return render(request, 'store/staff_home.html', {'customers': customers})

def logoutView(request):
    logout(request)
    return redirect('welcome')

def cart_status(request):
    customer = request.user
    basket_items = PurchaseHistory.objects.filter(customer=customer, status='Pending')
    return render(request, 'basket_status.html', {'basket_items': basket_items})

