from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from .models import Supplier
from decimal import Decimal

def is_admin(user):
    try:
        return user.userprofile.is_admin
    except:
        return False

@login_required
def supplier_list(request):
    search_query = request.GET.get('search', '')
    city_filter = request.GET.get('city', '')
    status_filter = request.GET.get('status', '')
    
    suppliers = Supplier.objects.all()
    
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if city_filter:
        suppliers = suppliers.filter(city__icontains=city_filter)
    
    if status_filter == 'active':
        suppliers = suppliers.filter(is_active=True)
    elif status_filter == 'inactive':
        suppliers = suppliers.filter(is_active=False)
    
    # Get unique cities for filter
    cities = Supplier.objects.values_list('city', flat=True).distinct().order_by('city')
    
    context = {
        'suppliers': suppliers,
        'cities': cities,
        'search_query': search_query,
        'city_filter': city_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
@user_passes_test(is_admin)
def supplier_create(request):
    if request.method == 'POST':
        try:
            supplier = Supplier.objects.create(
                name=request.POST.get('name'),
                contact_person=request.POST.get('contact_person', ''),
                phone=request.POST.get('phone'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state', ''),
                pincode=request.POST.get('pincode', ''),
                gst_number=request.POST.get('gst_number', ''),
                pan_number=request.POST.get('pan_number', ''),
                bank_name=request.POST.get('bank_name', ''),
                account_number=request.POST.get('account_number', ''),
                ifsc_code=request.POST.get('ifsc_code', ''),
                credit_limit=Decimal(request.POST.get('credit_limit', '0')),
                credit_days=int(request.POST.get('credit_days', '0')),
                notes=request.POST.get('notes', ''),
                created_by=request.user
            )
            
            messages.success(request, f'Supplier "{supplier.name}" created successfully!')
            return redirect('suppliers:supplier_list')
            
        except Exception as e:
            messages.error(request, f'Error creating supplier: {str(e)}')
    
    return render(request, 'suppliers/supplier_form.html')

@login_required
@user_passes_test(is_admin)
def supplier_edit(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        try:
            supplier.name = request.POST.get('name')
            supplier.contact_person = request.POST.get('contact_person', '')
            supplier.phone = request.POST.get('phone')
            supplier.email = request.POST.get('email', '')
            supplier.address = request.POST.get('address')
            supplier.city = request.POST.get('city')
            supplier.state = request.POST.get('state', '')
            supplier.pincode = request.POST.get('pincode', '')
            supplier.gst_number = request.POST.get('gst_number', '')
            supplier.pan_number = request.POST.get('pan_number', '')
            supplier.bank_name = request.POST.get('bank_name', '')
            supplier.account_number = request.POST.get('account_number', '')
            supplier.ifsc_code = request.POST.get('ifsc_code', '')
            supplier.credit_limit = Decimal(request.POST.get('credit_limit', '0'))
            supplier.credit_days = int(request.POST.get('credit_days', '0'))
            supplier.notes = request.POST.get('notes', '')
            supplier.save()
            
            messages.success(request, f'Supplier "{supplier.name}" updated successfully!')
            return redirect('suppliers:supplier_list')
            
        except Exception as e:
            messages.error(request, f'Error updating supplier: {str(e)}')
    
    return render(request, 'suppliers/supplier_form.html', {'supplier': supplier})

@login_required
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    return render(request, 'suppliers/supplier_detail.html', {'supplier': supplier})

@login_required
@user_passes_test(is_admin)
@require_POST
def supplier_delete(request):
    supplier_id = request.POST.get('supplier_id')
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.is_active = False
        supplier.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Supplier "{supplier.name}" deactivated successfully.'
        })
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Supplier not found.'})

@login_required
@user_passes_test(is_admin)
@require_POST
def supplier_activate(request):
    supplier_id = request.POST.get('supplier_id')
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.is_active = True
        supplier.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Supplier "{supplier.name}" activated successfully.'
        })
    except Supplier.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Supplier not found.'})
