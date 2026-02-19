"""
Views for Multi-Vendor Marketplace
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from .models import (
    Vendor, Category, Product, Order, OrderItem, Commission,
    Payout, Cart, CartItem, Review, Wishlist
)
from .forms import VendorRegistrationForm, ProductForm


class RegisterView(CreateView):
    model = User
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)


def home(request):
    categories = Category.objects.filter(is_active=True, parent=None)
    featured_products = Product.objects.filter(status='ACTIVE').order_by('-view_count')[:12]
    new_arrivals = Product.objects.filter(status='ACTIVE').order_by('-created_at')[:12]
    
    return render(request, 'marketplace/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
    })


def product_list(request):
    products = Product.objects.filter(status='ACTIVE')
    categories = Category.objects.filter(is_active=True)
    
    search = request.GET.get('q')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')
    
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if category:
        products = products.filter(category_id=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    products = products.order_by(sort)
    
    return render(request, 'marketplace/product_list.html', {
        'products': products,
        'categories': categories,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status='ACTIVE')
    product.view_count += 1
    product.save()
    
    related_products = Product.objects.filter(
        category=product.category,
        status='ACTIVE'
    ).exclude(id=product.id)[:8]
    
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    })


def vendor_store(request, store_slug):
    vendor = get_object_or_404(Vendor, store_slug=store_slug, is_approved=True, is_active=True)
    products = Product.objects.filter(vendor=vendor, status='ACTIVE')
    
    category_ids = products.values_list('category_id', flat=True).distinct()
    vendor_categories = Category.objects.filter(id__in=category_ids)
    
    return render(request, 'marketplace/vendor_store.html', {
        'vendor': vendor,
        'products': products,
        'vendor_categories': vendor_categories,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, status='ACTIVE')
    
    vendor_ids = products.values_list('vendor_id', flat=True).distinct()[:5]
    top_sellers = Vendor.objects.filter(id__in=vendor_ids)
    
    return render(request, 'marketplace/category.html', {
        'category': category,
        'products': products,
        'top_sellers': top_sellers,
    })


@require_POST
def cart_add(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login to add items to cart',
            'redirect': '/accounts/login/?next=' + request.path
        }, status=401)
    
    product = get_object_or_404(Product, id=product_id, status='ACTIVE')
    quantity = int(request.POST.get('quantity', 1))
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart!',
        'cart_total_items': cart.total_items,
        'cart_total_price': float(cart.total_price),
    })


@require_POST
@login_required
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'cart_total_items': cart_item.cart.total_items,
        'cart_total_price': float(cart_item.cart.total_price),
        'item_subtotal': float(cart_item.subtotal),
    })


@require_POST
@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart',
        'cart_total_items': cart_item.cart.total_items,
        'cart_total_price': float(cart_item.cart.total_price),
    })


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    subtotal = cart.total_price
    shipping_cost = Decimal('10.00') if subtotal < 100 else Decimal('0')
    tax = subtotal * Decimal('0.08')
    total = subtotal + shipping_cost + tax
    
    amount_for_free_shipping = Decimal('100.00') - subtotal if subtotal < 100 else Decimal('0')
    
    return render(request, 'marketplace/cart.html', {
        'cart': cart,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total': total,
        'amount_for_free_shipping': amount_for_free_shipping,
    })


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return redirect('cart_detail')
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        
        subtotal = cart.total_price
        shipping_cost = Decimal('10.00') if subtotal < 100 else Decimal('0')
        tax = subtotal * Decimal('0.08')
        total = subtotal + shipping_cost + tax
        
        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            billing_address=shipping_address,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total,
        )
        
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                vendor=item.product.vendor,
                quantity=item.quantity,
                price=item.product.current_price,
                subtotal=item.subtotal,
            )
            
            Commission.objects.create(
                order=order,
                vendor=item.product.vendor,
                order_item=OrderItem.objects.filter(order=order).last(),
                amount=item.subtotal * (item.product.vendor.commission_rate / 100),
                rate=item.product.vendor.commission_rate,
            )
        
        cart.items.all().delete()
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'marketplace/checkout.html', {'cart': cart})


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'marketplace/order_confirmation.html', {'order': order})


@login_required
def profile(request):
    return render(request, 'marketplace/profile.html', {'user': request.user})


@login_required
def profile_redirect(request):
    return redirect('profile')


@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user)
    return render(request, 'marketplace/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    return render(request, 'marketplace/order_detail.html', {
        'order': order,
        'order_items': order.items.all(),
    })


@login_required
def wishlist(request):
    return render(request, 'marketplace/wishlist.html', {'wishlist_items': request.user.wishlist.all()})


@require_POST
@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, status='ACTIVE')
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to wishlist!',
        'added': created,
    })


@require_POST
@login_required
def wishlist_remove(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return JsonResponse({
        'success': True,
        'message': 'Removed from wishlist',
    })


@login_required
def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save()
            return redirect('vendor_dashboard')
    else:
        form = VendorRegistrationForm()
    return render(request, 'marketplace/vendor_register.html', {'form': form})


@login_required
def vendor_dashboard(request):
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('vendor_register')
    
    total_products = Product.objects.filter(vendor=vendor).count()
    active_products = Product.objects.filter(vendor=vendor, status='ACTIVE').count()
    
    orders = OrderItem.objects.filter(vendor=vendor).values_list('order_id', flat=True)
    total_orders = Order.objects.filter(id__in=orders).count()
    
    earnings = OrderItem.objects.filter(vendor=vendor).aggregate(
        total=Sum('subtotal')
    )['total'] or Decimal('0')
    
    commissions = Commission.objects.filter(vendor=vendor, status='COMPLETED').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    recent_orders = OrderItem.objects.filter(vendor=vendor).select_related('order', 'product').order_by('-created_at')[:10]
    
    monthly_sales = OrderItem.objects.filter(
        vendor=vendor,
        order__created_at__month=timezone.now().month
    ).aggregate(total=Sum('subtotal'))['total'] or Decimal('0')
    
    return render(request, 'marketplace/vendor_dashboard.html', {
        'vendor': vendor,
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'earnings': earnings - commissions,
        'recent_orders': recent_orders,
        'monthly_sales': monthly_sales,
    })


@login_required
def vendor_products(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    products = Product.objects.filter(vendor=vendor)
    return render(request, 'marketplace/vendor_products.html', {'products': products})


@login_required
def vendor_product_create(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()
            return redirect('vendor_products')
    else:
        form = ProductForm()
    return render(request, 'marketplace/vendor_product_form.html', {'form': form})


@login_required
def vendor_product_update(request, pk):
    vendor = get_object_or_404(Vendor, user=request.user)
    product = get_object_or_404(Product, id=pk, vendor=vendor)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/vendor_product_form.html', {'form': form})


@login_required
def vendor_orders(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    order_items = OrderItem.objects.filter(vendor=vendor).select_related('order', 'product').order_by('-created_at')
    return render(request, 'marketplace/vendor_orders.html', {'order_items': order_items})


@login_required
def vendor_earnings(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    
    commissions = Commission.objects.filter(vendor=vendor)
    payouts = Payout.objects.filter(vendor=vendor)
    
    total_earnings = OrderItem.objects.filter(vendor=vendor).aggregate(
        total=Sum('subtotal')
    )['total'] or Decimal('0')
    
    total_commissions = commissions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_payouts = payouts.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    pending_balance = total_earnings - total_commissions - total_payouts
    
    return render(request, 'marketplace/vendor_earnings.html', {
        'vendor': vendor,
        'commissions': commissions,
        'payouts': payouts,
        'total_earnings': total_earnings,
        'total_commissions': total_commissions,
        'total_payouts': total_payouts,
        'pending_balance': pending_balance,
    })


@require_POST
@login_required
def vendor_request_payout(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    amount = Decimal(request.POST.get('amount', 0))
    
    if amount <= 0:
        return JsonResponse({'success': False, 'message': 'Invalid amount'})
    
    if amount > vendor.pending_balance:
        return JsonResponse({'success': False, 'message': 'Insufficient balance'})
    
    Payout.objects.create(
        vendor=vendor,
        amount=amount,
        method='bank_transfer',
        notes='Vendor requested payout',
    )
    
    return JsonResponse({'success': True, 'message': 'Payout request submitted'})


@user_passes_test(lambda u: u.is_superuser)
def admin_commissions(request):
    commissions = Commission.objects.all().select_related('order', 'vendor', 'order_item').order_by('-created_at')
    return render(request, 'marketplace/admin_commissions.html', {'commissions': commissions})


@user_passes_test(lambda u: u.is_superuser)
def admin_payouts(request):
    payouts = Payout.objects.all().select_related('vendor').order_by('-requested_at')
    return render(request, 'marketplace/admin_payouts.html', {'payouts': payouts})


@user_passes_test(lambda u: u.is_superuser)
def admin_vendors(request):
    vendors = Vendor.objects.all().order_by('-created_at')
    return render(request, 'marketplace/admin_vendors.html', {'vendors': vendors})


@user_passes_test(lambda u: u.is_superuser)
def approve_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.is_approved = True
    vendor.save()
    return redirect('admin_vendors')
