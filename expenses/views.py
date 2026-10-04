from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from .models import Expense, ExpenseCategory
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

def is_admin(user):
    try:
        return user.userprofile.is_admin
    except:
        return False

@login_required
def expense_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    expenses = Expense.objects.select_related('category', 'created_by')
    
    if search_query:
        expenses = expenses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(vendor_name__icontains=search_query)
        )
    
    if category_filter:
        expenses = expenses.filter(category_id=category_filter)
    
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)
    
    # Calculate totals
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    categories = ExpenseCategory.objects.all()
    
    context = {
        'expenses': expenses[:100],  # Limit for performance
        'categories': categories,
        'total_expenses': total_expenses,
        'search_query': search_query,
        'category_filter': category_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'expenses/expense_list.html', context)

@login_required
@user_passes_test(is_admin)
def expense_create(request):
    if request.method == 'POST':
        try:
            expense = Expense.objects.create(
                title=request.POST.get('title'),
                category_id=request.POST.get('category'),
                amount=Decimal(request.POST.get('amount')),
                description=request.POST.get('description', ''),
                expense_date=request.POST.get('expense_date'),
                payment_method=request.POST.get('payment_method', 'cash'),
                vendor_name=request.POST.get('vendor_name', ''),
                receipt_number=request.POST.get('receipt_number', ''),
                is_recurring=bool(request.POST.get('is_recurring')),
                recurring_period=request.POST.get('recurring_period', ''),
                created_by=request.user
            )
            
            messages.success(request, f'Expense "{expense.title}" created successfully!')
            return redirect('expenses:expense_list')
            
        except Exception as e:
            messages.error(request, f'Error creating expense: {str(e)}')
    
    categories = ExpenseCategory.objects.all()
    return render(request, 'expenses/expense_form.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def expense_edit(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        try:
            expense.title = request.POST.get('title')
            expense.category_id = request.POST.get('category')
            expense.amount = Decimal(request.POST.get('amount'))
            expense.description = request.POST.get('description', '')
            expense.expense_date = request.POST.get('expense_date')
            expense.payment_method = request.POST.get('payment_method', 'cash')
            expense.vendor_name = request.POST.get('vendor_name', '')
            expense.receipt_number = request.POST.get('receipt_number', '')
            expense.is_recurring = bool(request.POST.get('is_recurring'))
            expense.recurring_period = request.POST.get('recurring_period', '')
            expense.save()
            
            messages.success(request, f'Expense "{expense.title}" updated successfully!')
            return redirect('expenses:expense_list')
            
        except Exception as e:
            messages.error(request, f'Error updating expense: {str(e)}')
    
    categories = ExpenseCategory.objects.all()
    return render(request, 'expenses/expense_form.html', {'expense': expense, 'categories': categories})

@login_required
def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    return render(request, 'expenses/expense_detail.html', {'expense': expense})

@login_required
@user_passes_test(is_admin)
@require_POST
def expense_delete(request):
    expense_id = request.POST.get('expense_id')
    try:
        expense = Expense.objects.get(id=expense_id)
        title = expense.title
        expense.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Expense "{title}" deleted successfully.'
        })
    except Expense.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Expense not found.'})

@login_required
@user_passes_test(is_admin)
def category_manage(request):
    categories = ExpenseCategory.objects.all().annotate(
        total_expenses=Sum('expenses__amount')
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description')
            
            if ExpenseCategory.objects.filter(name=name).exists():
                messages.error(request, 'Category name already exists.')
            else:
                ExpenseCategory.objects.create(name=name, description=description)
                messages.success(request, f'Category "{name}" created successfully.')
                return redirect('expenses:category_manage')
    
    return render(request, 'expenses/category_manage.html', {'categories': categories})

@login_required
def monthly_expenses(request):
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    
    # Current month expenses
    monthly_expenses = Expense.objects.filter(
        expense_date__gte=current_month_start,
        expense_date__lte=today
    )
    
    total_monthly = monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Category-wise breakdown
    category_breakdown = monthly_expenses.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Daily expenses for chart
    daily_expenses = []
    current_date = current_month_start
    while current_date <= today:
        day_total = monthly_expenses.filter(
            expense_date=current_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        daily_expenses.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total': float(day_total)
        })
        current_date += timedelta(days=1)
    
    context = {
        'monthly_expenses': monthly_expenses[:20],
        'total_monthly': total_monthly,
        'category_breakdown': category_breakdown,
        'daily_expenses': daily_expenses,
        'current_month': current_month_start.strftime('%B %Y'),
    }
    
    return render(request, 'expenses/monthly_expenses.html', context)
