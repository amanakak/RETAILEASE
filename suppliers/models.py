from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True, help_text="GST Registration Number")
    pan_number = models.CharField(max_length=10, blank=True, null=True, help_text="PAN Number")
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Credit limit for this supplier")
    credit_days = models.IntegerField(default=0, help_text="Credit payment days")
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        address_parts = [self.address, self.city]
        if self.state:
            address_parts.append(self.state)
        if self.pincode:
            address_parts.append(self.pincode)
        return ', '.join(address_parts)
