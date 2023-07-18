from django.db import models
from djongo import models
from superadmin.models import Client, Properties, Customer
import uuid
from django.core.validators import RegexValidator
from django.utils.timezone import now

# Create your models here.
class ParanoidModelManager(models.Manager):
    def get_queryset(self):
        return super(ParanoidModelManager, self).get_queryset().filter(deleted_at__isnull=True)

class BookProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, related_name='property_book')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_book' )
    order_id = models.CharField(max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount = models.FloatField()
    currency = models.CharField(max_length=3)
    book_status = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True,null=True ,default=None)
    objects = ParanoidModelManager() 
    
    def delete(self, hard=False, **kwargs):
        if hard:
            super(BookProperty, self).delete()
        else:
            self.deleted_at = now()
            self.save()


