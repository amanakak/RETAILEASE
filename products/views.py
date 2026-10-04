from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from .models import Product, Category, StockMovement
from decimal import Decimal
import json

def is_admin(user):
    try:
        return user.userprofile.is_admin
    except:
        return False

@login_required
def product_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    
    products = Product.objects.select_related('category').filter(is_active=True)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if stock_filter == 'low':
        products = [p for p in products if p.is_low_stock]
    elif stock_filter == 'out':
        products = products.filter(stock_quantity=0)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
    }
    
    return render(request, 'products/product_list.html', context)

@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            sku = request.POST.get('sku')
            barcode = request.POST.get('barcode')
            category_id = request.POST.get('category')
            description = request.POST.get('description')
            price = Decimal(request.POST.get('price'))
            cost_price = Decimal(request.POST.get('cost_price', '0'))
            stock_quantity = int(request.POST.get('stock_quantity', '0'))
            low_stock_threshold = int(request.POST.get('low_stock_threshold', '10'))
            unit = request.POST.get('unit', 'pcs')
            expiry_date = request.POST.get('expiry_date') or None
            
            category = get_object_or_404(Category, id=category_id)
            
            # Check if SKU already exists
            if Product.objects.filter(sku=sku).exists():
                messages.error(request, 'SKU already exists. Please use a different SKU.')
            else:
                product = Product.objects.create(
                    name=name,
                    sku=sku,
                    barcode=barcode,
                    category=category,
                    description=description,
                    price=price,
                    cost_price=cost_price,
                    stock_quantity=stock_quantity,
                    low_stock_threshold=low_stock_threshold,
                    unit=unit,
                    expiry_date=expiry_date
                )
                
                # Create initial stock movement
                if stock_quantity > 0:
                    StockMovement.objects.create(
                        product=product,
                        movement_type='in',
                        quantity=stock_quantity,
                        reference='Initial Stock',
                        created_by=request.user
                    )
                
                messages.success(request, f'Product "{name}" created successfully.')
                return redirect('products:product_list')
                
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'products/product_form.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            old_stock = product.stock_quantity
            
            product.name = request.POST.get('name')
            product.sku = request.POST.get('sku')
            product.barcode = request.POST.get('barcode')
            product.category_id = request.POST.get('category')
            product.description = request.POST.get('description')
            product.price = Decimal(request.POST.get('price'))
            product.cost_price = Decimal(request.POST.get('cost_price', '0'))
            new_stock = int(request.POST.get('stock_quantity', '0'))
            product.low_stock_threshold = int(request.POST.get('low_stock_threshold', '10'))
            product.unit = request.POST.get('unit', 'pcs')
            product.expiry_date = request.POST.get('expiry_date') or None
            
            product.save()
            
            # Create stock movement if quantity changed
            if new_stock != old_stock:
                movement_type = 'in' if new_stock > old_stock else 'out'
                quantity = abs(new_stock - old_stock)
                
                StockMovement.objects.create(
                    product=product,
                    movement_type=movement_type,
                    quantity=quantity,
                    reference='Manual Stock Update',
                    notes=f'Stock updated from {old_stock} to {new_stock}',
                    created_by=request.user
                )
                
                product.stock_quantity = new_stock
                product.save()
            
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('products:product_list')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'products/product_form.html', {'product': product, 'categories': categories})

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    stock_movements = product.stock_movements.all()[:20]  # Last 20 movements
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'stock_movements': stock_movements
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def product_delete(request):
    product_id = request.POST.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
        product.is_active = False
        product.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Product "{product.name}" deleted successfully.'
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'})

@login_required
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all().annotate(
        product_count=Sum('products__stock_quantity')
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description')
            
            if Category.objects.filter(name=name).exists():
                messages.error(request, 'Category name already exists.')
            else:
                Category.objects.create(name=name, description=description)
                messages.success(request, f'Category "{name}" created successfully.')
                return redirect('products:category_list')
    
    return render(request, 'products/category_list.html', {'categories': categories})

@login_required
def low_stock_alert(request):
    low_stock_products = [p for p in Product.objects.filter(is_active=True) if p.is_low_stock]
    
    return render(request, 'products/low_stock_alert.html', {'products': low_stock_products})
