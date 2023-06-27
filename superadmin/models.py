from django.db import models
from djongo import models
from django.core.validators import FileExtensionValidator, RegexValidator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
import uuid
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField



class TermsandPolicy(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE )
    terms_and_condition = RichTextField()
    privacy_policy = RichTextField()

    
class ParanoidModelManager(models.Manager):
    def get_queryset(self):
        return super(ParanoidModelManager, self).get_queryset().filter(deleted_at__isnull=True)

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=40)
    profile_image = models.ImageField(blank=True, upload_to="client", validators=[FileExtensionValidator(['jpg','jpeg','png'])], height_field=None, width_field=None, max_length=None)
    contact_no = models.CharField(validators=[RegexValidator(regex=r"^\+?1?\d{10}$")], max_length=10, unique=True, null=True)
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
    def is_authenticated(self):
        return True  

    def is_anonymous(self):
        return False 


class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(("State"), max_length=50,unique=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True,null=True ,default=None)
    objects = ParanoidModelManager()   


    def delete(self, hard=False, **kwargs):
        if hard:
            super(State, self).delete()
        else:
            self.deleted_at = now()
            self.save()


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(("City"), max_length=50,unique=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="state")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True,null=True ,default=None)
    objects = ParanoidModelManager()   


    def delete(self, hard=False, **kwargs):
        if hard:
            super(City, self).delete()
        else:
            self.deleted_at = now()
            self.save()


class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(("Area"), max_length=50,unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="city")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True,null=True ,default=None)
    objects = ParanoidModelManager()   


    def delete(self, hard=False, **kwargs):
        if hard:
            super(Area, self).delete()
        else:
            self.deleted_at = now()
            self.save()
class Properties(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=40, null=True)
    root_image = models.ImageField(blank=True, upload_to="property", validators=[FileExtensionValidator(['jpg','jpeg','png'])], height_field=None, width_field=None, max_length=None)
    price = models.PositiveBigIntegerField()
    description = models.TextField()
    owner = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name="properties") 
    area_id = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="area")
    address = models.TextField()
    CHOICES = (('deactive','deactive'),('active','active'))
    status = models.CharField(("status"),choices=CHOICES, max_length=50,default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True,null=True ,default=None)
    objects = ParanoidModelManager() 

    def __str__(self):
        return f"{self.name}({self.price})"
    def delete(self, hard=False, **kwargs):
        if hard:
            super(Properties, self).delete()
        else:
            self.deleted_at = now()
            self.save()
            self.images.all().delete()
            self.videos.all().delete()

    
class PropertyImage(models.Model):
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="property", validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], verbose_name="images")

class PropertyVideo(models.Model):
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to="property", validators=[FileExtensionValidator(['mp4', 'mpeg4'])], verbose_name="videos" )

class PropertyTerms(models.Model):
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, related_name='terms')
    terms = RichTextField()

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=40, null=True)
    email = models.EmailField(default=None, max_length=250)
    profile_image = models.ImageField(blank=True, upload_to="customer", validators=[FileExtensionValidator(['jpg','jpeg','png'])], max_length=None, null=True)
    contact_no = models.CharField(validators=[RegexValidator(regex=r"^\+?1?\d{10}$")], max_length=10, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='user_are')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True,null=True ,default=None)
    objects = ParanoidModelManager() 

    def __str__(self):
        return f"{self.username}({self.password})"
    
    def delete(self, hard=False, **kwargs):
        if hard:
            super(Customer, self).delete()
        else:
            self.deleted_at = now()
            self.save()

    def is_authenticated(self):
        return True  

    def is_anonymous(self):
        return False 

    
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=20)
    message = models.TextField(max_length=70)
    SENT_CHOICES = [
        ('clients', 'Send to Clients'),
        ('users', 'Send to Customer'),
        ('both', 'Send to Both'),
    ]
    send_to = models.CharField(max_length=10, choices=SENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def send_notification(self):
        if self.send_to == 'clients' or self.send_to == 'both':
            # Send notification to all clients
            clients = Client.objects.all()
            for client in clients:
                send_mail(
                    self.title,
                    self.message,
                    settings.DEFAULT_FROM_EMAIL,
                    [client.email],
                    fail_silently=False
                )

        if self.send_to == 'customers' or self.send_to == 'both':
            # Send notification to all users
            customers = Customer.objects.all()
            for customer in customers:
                send_mail(
                    self.title,
                    self.message,
                    settings.DEFAULT_FROM_EMAIL,
                    [customer.email],
                    fail_silently=False
                )


