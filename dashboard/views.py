from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from products.models import Product, Category
from sales.models import Sale, SaleItem, Customer
from expenses.models import Expense
from suppliers.models import Supplier
from authentication.models import UserProfile
import json

def landing(request):
    """Public home page for TrackCart"""
    return render(request, 'landing/home.html')

@login_required
def customer_list(request):
    if not request.user.userprofile.is_admin:
        return redirect('dashboard:dashboard')
    query = request.GET.get('q', '').strip()
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(name__icontains=query) | customers.filter(phone__icontains=query) | customers.filter(email__icontains=query)
    customers = customers.annotate(purchase_count=Count('sales'), total_spent=Sum('sales__total_amount'))
    return render(request, 'dashboard/customer_list.html', {'customers': customers, 'query': query})

@login_required
def customer_detail(request, customer_id):
    if not request.user.userprofile.is_admin:
        return redirect('dashboard:dashboard')
    customer = Customer.objects.get(id=customer_id)
    purchases = customer.sales.select_related('created_by').prefetch_related('items__product')
    summary = purchases.aggregate(total_spent=Sum('total_amount'), purchase_count=Count('id'))
    return render(request, 'dashboard/customer_detail.html', {
        'customer': customer, 'purchases': purchases,
        'total_spent': summary['total_spent'] or 0, 'purchase_count': summary['purchase_count'] or 0,
    })

@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    
    # Calculate total inventory value
    active_products = Product.objects.filter(is_active=True)
    inventory_val = sum(p.total_value for p in active_products)
    
    # Customer count from sale records
    total_customers = Customer.objects.count()
    
    # Basic statistics
    stats = {
        'total_products': active_products.count(),
        'low_stock_products': len([p for p in active_products if p.is_low_stock]),
        'total_suppliers': Supplier.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.count(),
        'inventory_value': inventory_val,
        'total_customers': total_customers,
    }
    
    # Sales statistics
    today_sales = Sale.objects.filter(created_at__date=today)
    monthly_sales = Sale.objects.filter(created_at__date__gte=current_month_start)
    
    sales_stats = {
        'today_sales': today_sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'today_transactions': today_sales.count(),
        'monthly_sales': monthly_sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'monthly_transactions': monthly_sales.count(),
    }
    
    # Expense statistics (admin only)
    expense_stats = {}
    if user_profile.is_admin:
        today_expenses = Expense.objects.filter(expense_date=today)
        monthly_expenses = Expense.objects.filter(expense_date__gte=current_month_start)
        
        expense_stats = {
            'today_expenses': today_expenses.aggregate(total=Sum('amount'))['total'] or 0,
            'monthly_expenses': monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0,
        }
        
        # Calculate profit
        monthly_profit = sales_stats['monthly_sales'] - expense_stats['monthly_expenses']
        expense_stats['monthly_profit'] = monthly_profit
    
    # Payment method breakdown for dashboard visualization
    payment_methods_qs = monthly_sales.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    )
    total_m_sales = sales_stats['monthly_sales'] or 1
    payment_breakdown = []
    for pm in payment_methods_qs:
        pct = round((pm['total'] / total_m_sales) * 100, 1) if total_m_sales > 0 else 0
        payment_breakdown.append({
            'method': pm['payment_method'].upper(),
            'total': float(pm['total']),
            'count': pm['count'],
            'percentage': pct
        })

    # Recent activities
    recent_sales = Sale.objects.select_related('created_by')[:8]
    recent_products = Product.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_expenses = Expense.objects.select_related('category', 'created_by')[:5] if user_profile.is_admin else []
    
    # Low stock alerts
    low_stock_products = [p for p in active_products if p.is_low_stock][:20]
    
    # Chart data for last 7 days
    chart_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        daily_sales = Sale.objects.filter(created_at__date=date).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        chart_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
    
    # Top selling products (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    top_products = SaleItem.objects.filter(
        sale__created_at__date__gte=thirty_days_ago
    ).values('product__name', 'product__category__name', 'product__sku').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_quantity')[:5]
    
    # Category-wise sales
    category_sales = list(SaleItem.objects.filter(
        sale__created_at__date__gte=thirty_days_ago
    ).values('product__category__name').annotate(
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')[:5])
    
    for item in category_sales:
        item['total_revenue'] = float(item['total_revenue']) if item['total_revenue'] is not None else 0.0
    
    context = {
        'user_profile': user_profile,
        'stats': stats,
        'sales_stats': sales_stats,
        'expense_stats': expense_stats,
        'payment_breakdown': payment_breakdown,
        'recent_sales': recent_sales,
        'recent_products': recent_products,
        'recent_expenses': recent_expenses,
        'low_stock_products': low_stock_products,
        'chart_data': json.dumps(chart_data),
        'top_products': top_products,
        'category_sales': category_sales,
        'category_sales_json': json.dumps(category_sales),
    }
    
    if user_profile.is_admin:
        return render(request, 'dashboard/admin_dashboard.html', context)
    else:
        return render(request, 'dashboard/staff_dashboard.html', context)


@login_required
def reports(request):
    """Generate various reports"""
    user_profile = request.user.userprofile
    
    if not user_profile.is_admin:
        return redirect('dashboard:dashboard')
    
    # Date range from request or default to current month
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    today = timezone.now().date()
    if not date_from:
        date_from = today.replace(day=1)
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = today
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Sales report
    sales_in_period = Sale.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    )
    
    sales_summary = {
        'total_sales': sales_in_period.aggregate(total=Sum('total_amount'))['total'] or 0,
        'total_transactions': sales_in_period.count(),
        'average_transaction': sales_in_period.aggregate(avg=Avg('total_amount'))['avg'] or 0,
    }
    
    # Expense report
    expenses_in_period = Expense.objects.filter(
        expense_date__gte=date_from,
        expense_date__lte=date_to
    )
    
    expense_summary = {
        'total_expenses': expenses_in_period.aggregate(total=Sum('amount'))['total'] or 0,
        'total_expense_entries': expenses_in_period.count(),
    }
    
    # Profit calculation
    profit = sales_summary['total_sales'] - expense_summary['total_expenses']
    
    # Product performance
    product_performance = SaleItem.objects.filter(
        sale__created_at__date__gte=date_from,
        sale__created_at__date__lte=date_to
    ).values('product__name', 'product__cost_price').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price'),
        total_cost=Sum('quantity') * Sum('product__cost_price')
    ).order_by('-total_revenue')[:10]
    
    # Payment method breakdown
    payment_methods = sales_in_period.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    )
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'sales_summary': sales_summary,
        'expense_summary': expense_summary,
        'profit': profit,
        'product_performance': product_performance,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'dashboard/reports.html', context)

@login_required
def analytics(request):
    """Advanced analytics page"""
    user_profile = request.user.userprofile
    
    # Basic analytics for all users, detailed for admin
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Sales trend (last 30 days)
    sales_trend = []
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        daily_total = Sale.objects.filter(
            created_at__date=date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'total': float(daily_total)
        })
    
    # Product categories performance
    category_performance = SaleItem.objects.filter(
        sale__created_at__date__gte=thirty_days_ago
    ).values('product__category__name').annotate(
        total_revenue=Sum('total_price'),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')
    
    # Hourly sales pattern
    hourly_pattern = []
    for hour in range(24):
        hourly_total = Sale.objects.filter(
            created_at__date__gte=thirty_days_ago,
            created_at__hour=hour
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        hourly_pattern.append(float(hourly_total))
    
    # Category JSON data for chart
    category_list = list(category_performance[:5])
    cat_labels = [c['product__category__name'] or 'Other' for c in category_list]
    cat_totals = [float(c['total_revenue'] or 0) for c in category_list]
    
    context = {
        'user_profile': user_profile,
        'sales_trend': json.dumps(sales_trend),
        'category_performance': category_performance,
        'cat_labels_json': json.dumps(cat_labels),
        'cat_totals_json': json.dumps(cat_totals),
        'hourly_pattern': json.dumps(hourly_pattern),
    }
    
    return render(request, 'dashboard/analytics.html', context)
