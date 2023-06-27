from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, AdminTermsAndpolicyForm, PropertyTermsForm
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail,BadHeaderError
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.http.response import HttpResponse
from django.contrib import messages



# Create your views here.



class password_reset_request(View):

    def get(self,request):
         password_reset_form = PasswordResetForm()
         return render(request=request, template_name="home/password_reset.html", context={"form":password_reset_form})
   
    def post(self,request):
        if request.method == "POST":
            password_reset_form = PasswordResetForm(request.POST)
            if password_reset_form.is_valid():
                data = password_reset_form.cleaned_data['email']
                associated_users = User.objects.filter(Q(email=data))
                if associated_users.exists():
                    for user in associated_users:
                        subject = "Password Reset Requested"
                        email_template_name = "password_reset_email.txt"
                        c = {
                        "email":user.email,
                        'domain':'shopfreeapp.herokuapp.com',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                        }
                        email = render_to_string(email_template_name, c)
                        try:
                            send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found.')
                        return redirect ("/password_reset/done/")
        
                else:
                    messages.error(request,'Sorry User Not Found')        
                    password_reset_form = PasswordResetForm()
                    return render(request=request, template_name="password_reset.html", context={"form":password_reset_form})




def is_authenticate(request):
    if request.session.get('enterprise_key'):
         return True
    return False




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
    
# State

def add_state(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            state = State(
                name=name,
            )
            state.save()
            return redirect('list_state')
        
    except Exception as e:
        print(e)
    return render(request, 'home/add_state.html')


def list_state(request):
    states  = State.objects.all()
    return render(request, 'home/list_state.html', {'states':states})


def update_state(request, id):
    try:
        state = State.objects.get(id=id)

        if request.method == 'POST':
            state.name = request.POST.get('name')
            state.status = request.POST.get('status')
            
            state.save()
            return redirect('list_state')
        
    except Exception as e:
        print(e)
    return render(request, 'home/update_state.html')


def delete_state(request, id):
    state = State.objects.get(id=id)
    state.delete()
    return redirect('list_state')

#City

def add_city(request):
    try:
        states = State.objects.all()
        if request.method == 'POST':
            name = request.POST.get('name')
            state_id = request.POST.get('state')
            state = State.objects.get(id=state_id)
            city = City(
                name=name,
                state=state,
            )
            city.save()
            return redirect('list_cities')
        
    except Exception as e:
        print(e)
    return render(request, 'home/add_city.html', {'states':states})


def list_cities(request):
    cities  = City.objects.all()
    return render(request, 'home/list_cities.html', {'cities':cities})


def update_city(request, id):
    try:
        city = City.objects.get(id=id)
        state = State.objects.all()
        if request.method == 'POST':
            state_id = request.POST.get('state')
            state = State.objects.get(id=state_id)
            city.name = request.POST.get('name')
            city.status = request.POST.get('status')
            city.state = state
            
            city.save()
            return redirect('list_cities')
        
    except Exception as e:
        print(e)
    return render(request, 'home/update_city.html', {"states":state})


def delete_city(request, id):
    city = City.objects.get(id=id)
    city.delete()
    return redirect('list_cities')


# Area

def add_area(request):
    try:
        cities = City.objects.all()

        if request.method == 'POST':
            name = request.POST.get('name')
            city_id = request.POST.get('city')
            city = City.objects.get(id=city_id)
            area = Area(
                name=name,
                city=city,
            )
            area.save()
            return redirect('list_areas')
        
    except Exception as e:
        print(e)
    return render(request, 'home/add_area.html', {'cities':cities})


def list_areas(request):
    areas  = Area.objects.all()
    return render(request, 'home/list_areas.html', {'areas':areas})


def update_area(request, id):
    try:
        area = Area.objects.get(id=id)
        city = City.objects.all()
        if request.method == 'POST':
            city_id = request.POST.get('city')
            city = City.objects.get(id=city_id)
            area.name = request.POST.get('name')
            area.status = request.POST.get('status')
            area.city = city
            
            area.save()
            return redirect('list_areas')
        
    except Exception as e:
        print(e)
    return render(request, 'home/update_area.html', {"cities":city})


def delete_area(request, id):
    area = Area.objects.get(id=id)
    area.delete()
    return redirect('list_areas')


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
        

            return redirect('list_clients')  
    except Exception as e:
        print(e)

    return render(request, 'home/add_client.html', {'segment':'index'})

def list_clients(request):
    clients = Client.objects.all()
    
    return render(request, 'home/list_clients.html', {"clients":clients})

def update_client(request, id):
    client = Client.objects.get(id=id)

    if request.method == 'POST':
        client.first_name = request.POST.get('first_name')
        client.last_name = request.POST.get('last_name')
        client.email = request.POST.get('email')
        client.contact_no = request.POST.get('contact_no')

        profile_image = request.FILES.get('profile_image')
        if profile_image:
            client.profile_image = profile_image

        client.save()

        return redirect('list_clients') 
    return render(request, 'home/update_client.html', {'client':client,'segment':'index'})

def delete_client(request, id):
    cli = Client.objects.get(id=id)
    cli.delete()
    return redirect('list_clients')


#Customer
 
     
def add_customer(request):
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

            customer = Customer(
                **data,
                profile_image=profile_image,
                
            )
            customer.save()
        

            return redirect('list_customers')  
    except Exception as e:
        print(e)

    return render(request, 'home/add_customer.html', {'segment':'customer'})


def list_customers(request):
    customers = Customer.objects.all()
    return render(request, 'home/list_customers.html', {"customers":customers, "segment":'customer'})


def update_customer(request, id):
    customer = Customer.objects.get(id=id)

    if request.method == 'POST':
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.contact_no = request.POST.get('contact_no')

        profile_image = request.FILES.get('profile_image')
        if profile_image:
            customer.profile_image = profile_image

        customer.save()

        return redirect('list_customers') 
    return render(request, 'home/update_customer.html', {'customer':customer, 'segment':'customer'})

def delete_customer(request, id):
    customer = Customer.objects.get(id=id)
    customer.delete()
    return redirect('list_customers')


#Property


def add_property(request):
    try:
        form = PropertyTermsForm(request.POST)
        clients = Client.objects.all()
        areas = Area.objects.all()
        try:
            if request.method == 'POST':
                form = PropertyTermsForm(request.POST)
                owner_id = request.POST.get('owner')
                owner = Client.objects.get(id=owner_id)
                area_id = request.POST.get('area')
                area = Area.objects.get(id=area_id)
                
                # Add Property fields
                property = Properties(
                    name=request.POST.get('property_name'),
                    price=request.POST.get('price'),
                    root_image = request.FILES.get('root_image'),
                    description=request.POST.get('description'),
                    owner=owner,
                    area_id=area,
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
                
                return redirect('list_properties')
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

    return render(request, 'home/add_property.html', {'clients': clients,'areas':areas, 'segment':'property', 'form':form})


def list_properties(request):
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
        property_terms = PropertyTerms.objects.filter(property=property_obj)
        print(property_terms)


        if request.method == 'POST':
            form = PropertyTermsForm(request.POST, instance=property_terms)

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

            return redirect('list_properties')
        else:
            form = PropertyTermsForm(instance=property_terms)
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
    return redirect('list_properties')