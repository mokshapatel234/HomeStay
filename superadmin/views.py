from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, AdminTermsAndpolicyForm, PropertyTermsForm
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import login


# Create your views here.



def add_terms_policy(request):
    admin_user = TermsandPolicy.objects.first() 

    if request.method == 'POST':
        form = AdminTermsAndpolicyForm(request.POST, instance=admin_user)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AdminTermsAndpolicyForm(instance=admin_user)
    
    return render(request, 'home/add_terms_policy.html', {'form': form})



class LoginView(View):

    def get(self,request):
      form = LoginForm
      return render(request,'accounts/login.html',{'form':form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    login(request, user)
                    return redirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'form': form, 'msg': 'Invalid Credentials'})
            except User.DoesNotExist:
                return render(request, 'login.html', {'form': form, 'msg': 'Invalid Credentials'})
        else:
            return render(request, 'login.html', {'form': form})


class Index(View):
    def get(self,request):
      client = Client.objects.all()
      num_client = client.count()
      customers= Customer.objects.all()
      num_customer = customers.count()
      properties = Properties.objects.all()
      num_property = properties.count()
      return render(request,'home/index.html', {"num_client":num_client, "num_customer":num_customer, "num_property":num_property})
    

# Client 


def add_client(request):
    try:
        if request.method == 'POST':
            data = {k:v[0]for k,v in dict(request.POST).items()}  
            
            data.pop('csrfmiddlewaretoken')
            
            # first_name = request.POST.get('first_name')
            # last_name = request.POST.get('last_name')
            # email = request.POST.get('email')
            # password = request.POST.get('password')
            profile_image = request.FILES.get('profile_image')
            # contact_no = request.POST.get('contact_no')

            client = Client(
                **data,
                profile_image=profile_image,
                
            )
            client.save()
        

            return redirect('all_clients')  
    except Exception as e:
        print(e)

    return render(request, 'home/add_client.html', {'segment':'index'})

def all_clients(request):
    clients = Client.objects.all()
    
    return render(request, 'home/list_clients.html', {"clients":clients})

def update_client(request, id):
    client = Client.objects.get(id=id)

    if request.method == 'POST':
        client.username = request.POST.get('username')
        client.first_name = request.POST.get('first_name')
        client.last_name = request.POST.get('last_name')
        client.email = request.POST.get('email')
        client.contact_no = request.POST.get('contact_no')

        profile_image = request.FILES.get('profile_image')
        if profile_image:
            client.profile_image = profile_image

        client.save()

        return redirect('all_clients') 
    return render(request, 'home/update_client.html', {'client':client,'segment':'index'})

def delete_client(request, id):
    cli = Client.objects.get(id=id)
    cli.delete()
    return redirect('all_clients')


#Customer
 
     
def add_customer(request):
    try:
        if request.method == 'POST':
            data = {k:v[0]for k,v in dict(request.POST).items()}  
            
            data.pop('csrfmiddlewaretoken')

            # username = request.POST.get('username')
            # first_name = request.POST.get('first_name')
            # last_name = request.POST.get('last_name')
            # email = request.POST.get('email')
            # password = request.POST.get('password')
            profile_image = request.FILES.get('profile_image')
            # contact_no = request.POST.get('contact_no')

            customer = Customer(
                **data,
                profile_image=profile_image,
                
            )
            customer.save()
        

            return redirect('all_customers')  
    except Exception as e:
        print(e)

    return render(request, 'home/add_customer.html', {'segment':'customer'})


def all_customers(request):
    customers = Customer.objects.all()
    return render(request, 'home/list_customers.html', {"customers":customers, "segment":'customer'})


def update_customer(request, id):
    customer = Customer.objects.get(id=id)

    if request.method == 'POST':
        customer.username = request.POST.get('username')
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.contact_no = request.POST.get('contact_no')

        profile_image = request.FILES.get('profile_image')
        if profile_image:
            customer.profile_image = profile_image

        customer.save()

        return redirect('all_customers') 
    return render(request, 'home/update_customer.html', {'customer':customer, 'segment':'customer'})

def delete_customer(request, id):
    customer = Customer.objects.get(id=id)
    customer.delete()
    return redirect('all_customers')


#Property


def add_property(request):
    try:
        form = PropertyTermsForm(request.POST)
        clients = Client.objects.all()
        try:
            if request.method == 'POST':
                form = PropertyTermsForm(request.POST)
                print(form)
                owner_id = request.POST.get('owner')
                owner = Client.objects.get(id=owner_id)
                
                # Add Property fields
                property = Properties(
                    name=request.POST.get('property_name'),
                    price=request.POST.get('price'),
                    root_image = request.FILES.get('root_image'),
                    description=request.POST.get('description'),
                    owner=owner,
                    address=request.POST.get('address'),
                    status='active',

                )
                property.save()
                
                # Add Property images
                images = request.FILES.getlist('images')
                for image in images:
                    PropertyImage.objects.create(property=property, image=image)
                
                # Add Property Videos
                videos = request.FILES.getlist('videos')
                for video in videos:
                    PropertyVideo.objects.create(property=property, video=video)


                try:
                    if form.is_valid():
                        property_terms = form.save(commit=False)
                        property_terms.property = property  
                        property_terms.save()
                    else:
                        print("Error")
                except Exception as e:
                    print(e)
                
                return redirect('all_properties')
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

    return render(request, 'home/add_property.html', {'clients': clients, 'segment':'property', 'form':form})


def all_properties(request):
    properties = Properties.objects.all()
    
    return render(request, 'home/list_properties.html', {"properties":properties, "segment":'property'})


def update_property(request,id):
    try:
        
        form = PropertyTermsForm(request.POST)
        property_obj = Properties.objects.get(id=id)
        clients = Client.objects.all()
        property_images = PropertyImage.objects.filter(property=property_obj)
        property_videos = PropertyVideo.objects.filter(property=property_obj)
        num_images = property_images.count()
        num_videos = property_videos.count()
        

        if request.method == 'POST':
            form = PropertyTermsForm(request.POST)

            owner_id = request.POST.get('owner')
            owner = Client.objects.get(id=owner_id)
            

            # Update property fields
            property_obj.name = request.POST.get('property_name')
            property_obj.price = request.POST.get('price')
            property_obj.root_image = request.FILES.get('root_image')
            property_obj.description = request.POST.get('description')
            property_obj.owner = owner
            property_obj.address = request.POST.get('address')
            property_obj.status = request.POST.get('status')
            property_obj.save()

            # Update property images
            images = request.FILES.getlist('images')
            PropertyImage.objects.filter(property=property_obj).delete()  
            for image in images:
                PropertyImage.objects.create(property=property_obj, image=image)

            # Update property videos
            videos = request.FILES.getlist('videos')
            PropertyVideo.objects.filter(property=property_obj).delete() 
            for video in videos:
                PropertyVideo.objects.create(property=property_obj, video=video)


            try:
                if form.is_valid():
                    property_terms = form.save(commit=False)
                    property_terms.property = property_obj  
                    property_terms.save()
                else:
                    print("Error")
            except Exception as e:
                print(e)

            return redirect('all_properties')
        else:
            form = PropertyTermsForm(request.POST, instance=property_terms)
    except Exception as e:
        print(e)

    return render(request, 'home/update_property.html',
                   {'property': property_obj,
                     'property_images': property_images, 
                     'property_videos': property_videos, 
                     'clients': clients, 
                     'segment': 'property', 
                     'num_images': num_images,
                     'num_videos': num_videos,
                     'form':form,
                     })



def delete_property(request, id):
    property = Properties.objects.get(id=id)
    property.delete()
    msg = (request, "Property deleted successfully")
    return redirect('all_properties')