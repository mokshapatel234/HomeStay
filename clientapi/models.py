from django.db import models
from djongo import models
from superadmin.models import Client
import uuid
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils.timezone import now

# Create your models here.
class ParanoidModelManager(models.Manager):
    def get_queryset(self):
        return super(ParanoidModelManager, self).get_queryset().filter(deleted_at__isnull=True)

class ClientBanking(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='banking_details')
    email = models.EmailField(unique=True)
    phone = models.CharField(validators=[RegexValidator(regex=r"^\+?1?\d{10}$")], max_length=10, unique=True)
    type = models.CharField(max_length=100)
    legal_business_name = models.CharField(max_length=100)
    business_type = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    CHOICES = (('inactive','inactive'),('active','active'))
    status = models.CharField(("status"),choices=CHOICES, max_length=50,default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True,null=True ,default=None)
    objects = ParanoidModelManager() 
  
  
    def __str__(self):
        return f"{self.username}({self.password})"
    
    def delete(self, hard=False, **kwargs):
        if hard:
            super(Client, self).delete()
        else:
            self.deleted_at = now()
            self.save()
    


# class ClientBanking(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='banking_details')
#     # Other fields for banking details
    
#     def __str__(self):
#         return f"ClientBanking {self.id} - Account {self.account_id}"

