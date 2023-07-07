from django.db import models
from djongo import models
from superadmin.models import Client
import uuid
from django.utils.timezone import now

# Create your models here.
class ParanoidModelManager(models.Manager):
    def get_queryset(self):
        return super(ParanoidModelManager, self).get_queryset().filter(deleted_at__isnull=True)

class ClientrBanking(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='banking_details')
    account_number = models.CharField(max_length=16)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=11)
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
    