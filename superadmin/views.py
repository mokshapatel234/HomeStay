from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, AdminTermsAndpolicyForm, PropertyTermsForm
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *
from userapi.models import BookProperty
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
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


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
    try:
        admin_user = TermsandPolicy.objects.get(user=request.user)
    except TermsandPolicy.DoesNotExist:
        admin_user = None

    if request.method == 'POST':
        form = AdminTermsAndpolicyForm(request.POST, instance=admin_user)
        if form.is_valid():
            terms_policy = form.save(commit=False)
            terms_policy.user = request.user  # Assign the current user
            terms_policy.save()
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
                    return render(request, 'accounts/login.html', {'form': form, 'msg': 'Invalid Credentials'})
            except User.DoesNotExist:
                return render(request, 'accounts/login.html', {'form': form, 'msg': 'Invalid Credentials'})
        else:
            return render(request, 'accounts/login.html', {'form': form})


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

        if request.method=="GET":
            return render(request, 'home/add_state.html')
        

        if request.method == 'POST':
            name = request.POST.get('name')
            state = State(name=name)
            state.save()
            messages.success(request, 'State added successfully.')
            return redirect('list_state')
        else:
            messages.error(request, 'Error while adding state')

            return render(request, 'home/add_state.html')
                   
    except:
        return render(request, 'home/add_state.html')

        


def list_state(request):
    states  = State.objects.all()
    return render(request, 'home/list_state.html', {'states':states})


def update_state(request, id):
    try:
        state = State.objects.get(id=id)

        if request.method=="GET":
            return render(request, 'home/update_state.html', {"state":state})

        if request.method == 'POST':
            state.name = request.POST.get('name')
            state.status = request.POST.get('status')
            
            state.save()
            messages.success(request, 'State updated successfully.')

            return redirect('list_state')
        
        else:
                messages.error(request, 'Error while updating state')
                return render(request, 'home/update_state.html')
                   
    except Exception as e:
        print(e)
        return render(request, 'home/update_state.html', {'msg': 'Invalid Credentials'})

def delete_state(request, id):
    try:
        state = State.objects.get(id=id)
        state.delete()
        messages.error(request, 'State deleted successfully.')

        return redirect('list_state')
    except:
        messages.error(request, 'Error while deleting state')
        return render(request, 'home/list_state.html')

#City

def add_city(request):
    try:
        states = State.objects.all()

        if request.method == "GET":
            return render(request, 'home/add_city.html', {'states':states})


        if request.method == 'POST':
            name = request.POST.get('name')
            state_id = request.POST.get('state')
            state = State.objects.get(id=state_id)
            city = City(
                name=name,
                state=state,
            )
            city.save()
            messages.success(request, 'City added successfully.')

            return redirect('list_cities')
        else:
            messages.error(request, 'Invalid Credentials')

            return render(request, 'home/add_city.html')
                   
    except:
        return render(request, 'home/add_city.html')
        
 
        


def list_cities(request):
    cities = City.objects.all()
    states = State.objects.all()
    state_id = request.GET.get('state')
    selected_state = None

    if state_id:
        cities = cities.filter(state_id=state_id)
        selected_state = State.objects.get(id=state_id).name

    context = {
        'states': states,
        'cities': cities,
        'selected_state_id': state_id,
        'selected_state': selected_state,
    }

    return render(request, 'home/list_cities.html', context)

def update_city(request, id):
    try:
        city = City.objects.get(id=id)
        states = State.objects.all()
     
        if request.method == 'POST':
            state_id = request.POST.get('state')  
            state = State.objects.get(id=state_id)
            city.name = request.POST.get('name')
            city.status = request.POST.get('status')
            city.state = state
            
            city.save()
            messages.success(request, 'City updated successfully')
            return redirect('list_cities') 
    except Exception as e:
        print(e)
        messages.error(request, 'Invalid Credentials')
    return render(request, 'home/update_city.html', {"states": states, "city": city})


def delete_city(request, id):
    try:
        city = City.objects.get(id=id)
        city.delete()
        messages.error(request, 'City deleted successfully')
        return redirect('list_cities') 
    except:
        messages.error(request, 'Invalid Credentials')
        return render(request, 'home/list_state.html')
    

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
            messages.success(request, 'Area added successfully.')

            return redirect('list_areas')
        
    except Exception as e:
        messages.error(request, 'Invalid Credentials')

    return render(request, 'home/add_area.html', {'cities':cities})

def list_areas(request):
    areas = Area.objects.all()
    states = State.objects.all()
    cities = City.objects.all()
    state_id = request.GET.get('state')
    city_id = request.GET.get('city')
    selected_state = None
    selected_city = None

    if state_id:
        areas = areas.filter(city__state=state_id)
        cities = cities.filter(state_id=state_id)
        selected_state = State.objects.get(id=state_id).name

    if city_id:
        areas = areas.filter(city_id=city_id)
        selected_city = City.objects.get(id=city_id).name

    context = {
        'states': states,
        'cities': cities,
        'areas':areas,
        'selected_state': selected_state,
        'selected_city': selected_city,
        'selected_state_id': state_id,
        'selected_city_id': city_id,
    }

    return render(request, 'home/list_areas.html', context)


def update_area(request, id):
    try:
        area = Area.objects.get(id=id)
        cities = City.objects.all()

        if request.method == 'POST':
            city_id = request.POST.get('city')  
            city = City.objects.get(id=city_id)
            area.name = request.POST.get('name')
            area.status = request.POST.get('status')
            area.city = city
            
            area.save()
            messages.success(request, 'Area updated successfully.')
            return redirect('list_areas')
    except Exception as e:
        print(e)
        messages.error(request, 'Invalid Credentials')
    return render(request, 'home/update_area.html', {"cities": cities, "area": area})


def delete_area(request, id):
    try:
        area = Area.objects.get(id=id)
        area.delete()
        messages.error(request, 'Area deleted successfully.')
        return redirect('list_areas')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_areas')

def get_cities(request):
    state_id = request.GET.get('state_id')
    if state_id:
        cities = City.objects.filter(state_id=state_id).values('id', 'name')
        return JsonResponse(list(cities), safe=False)
    else:
        return JsonResponse([], safe=False)


def get_areas(request):
    city_id = request.GET.get('city_id')
    if city_id:
        areas = Area.objects.filter(city_id=city_id).values('id', 'name')
        return JsonResponse(list(areas), safe=False)
    else:
        return JsonResponse([], safe=False)




# Client 


def add_client(request):
    try:
        states = State.objects.all()
        cities = City.objects.all()
        areas = Area.objects.all()


        if request.method == 'POST':

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            profile_image = request.FILES.get('profile_image')
            contact_no = request.POST.get('contact_no')
            area_id = request.POST.get('area')  # Retrieve the selected area value

            try:
                area = Area.objects.get(id=area_id)  # Get the Area object based on the selected area value
            except Area.DoesNotExist:
                return HttpResponse('Invalid area')

            # Create the Client object with the retrieved values
            client = Client.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                profile_image=profile_image,
                area=area,  # Assign the retrieved Area object to the area field
                contact_no=contact_no,
                status='active'
            )
            messages.success(request, 'Client added successfully.')
            return redirect('list_clients')  
        
        if 'state_id' in request.GET:
            state_id = request.GET.get('state_id')
            cities = City.objects.filter(state_id=state_id)

        if 'city_id' in request.GET:
            city_id = request.GET.get('city_id')
            areas = Area.objects.filter(city_id=city_id)
        return render(request, 'home/add_client.html', {'segment': 'index', 'states': states, 'cities': cities, 'areas': areas})

    except Exception as e:
        print(e)
        messages.error(request, 'Invalid Credentials')
    return render(request, 'home/add_client.html', {'segment': 'index', 'states': states, 'cities': cities, 'areas': areas})


def list_clients(request):
    clients = Client.objects.all()
    states = State.objects.all()
    cities = City.objects.all()
    areas = Area.objects.all()

    state_id = request.GET.get('state')
    city_id = request.GET.get('city')
    area_id = request.GET.get('area')

    selected_state = None
    selected_city = None

    if state_id:
        clients = clients.filter(area__city__state=state_id)
        cities = cities.filter(state_id=state_id)
        selected_state = State.objects.get(id=state_id).name

    if city_id:
        clients = clients.filter(area__city=city_id)
        areas = areas.filter(city_id=city_id)
        selected_city = City.objects.get(id=city_id).name

    if area_id:
        clients = clients.filter(area=area_id)
    
    context = {
        'clients': clients,
        'states': states,
        'cities': cities,
        'areas': areas,
        'selected_state': selected_state,
        'selected_city': selected_city,
        'selected_state_id': state_id,
        'selected_city_id': city_id,
        'selected_area_id': area_id,
    }

    return render(request, 'home/list_clients.html', context)

def update_client(request, id):
    try:
        client = Client.objects.get(id=id)
        states = State.objects.all()
        cities = City.objects.all()
        areas  = Area.objects.all()

        if request.method == 'POST':
            selected_state_id = client.area.city.state.id
            selected_city_id = client.area.city.id
            client.first_name = request.POST.get('first_name')
            client.last_name = request.POST.get('last_name')
            client.email = request.POST.get('email')
            client.contact_no = request.POST.get('contact_no')

            profile_image = request.FILES.get('profile_image')
            if profile_image:
                client.profile_image = profile_image

            client.save()
            messages.success(request, 'Client updated successfully.')
            return redirect('list_clients') 
        else:
            
            
            return render(request, 'home/update_client.html',
                    {'client':client,
                        'segment':'index',
                        'states': states,
                        'cities': cities,
                        'areas': areas
                        
                })
    except Exception as e:
        print(e)
        messages.error(request, 'Invalid Credentials')
    return render(request, 'home/update_client.html',
                    {'client':client,
                        'segment':'index',
                        'states': states,
                        'cities': cities,
                        'areas': areas
                        
                })   


def delete_client(request, id):
    try:
        cli = Client.objects.get(id=id)
        cli.delete()
        messages.success(request, 'Client deleted successfully.')
        return redirect('list_clients')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_clients')


#Customer
 
     
def add_customer(request):
    try:
        states = State.objects.all()
        cities = City.objects.all()
        areas  = Area.objects.all()

        if request.method == 'POST':

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            profile_image = request.FILES.get('profile_image')
            contact_no = request.POST.get('contact_no')
            area_id = request.POST.get('area')  

            try:
                area = Area.objects.get(id=area_id)  
            except Area.DoesNotExist:
                return HttpResponse('Invalid area')

            # Create the Client object with the retrieved values
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                profile_image=profile_image,
                area=area,  
                contact_no=contact_no,
                status='active'
            )
            messages.success(request, 'User added successfully.')

            return redirect('list_customers')  


        if 'state_id' in request.GET:
            state_id = request.GET.get('state_id')
            cities = City.objects.filter(state_id=state_id)

        if 'city_id' in request.GET:
            city_id = request.GET.get('city_id')
            areas = Area.objects.filter(city_id=city_id)

        return render(request, 'home/add_customer.html', {'segment': 'add_customer', 'states': states, 'cities': cities, 'areas': areas})

    except Exception as e:
        print(e)
        messages.error(request, 'Invalid Credentials')
    return render(request, 'home/add_customer.html', {'segment': 'add_customer', 'states': states, 'cities': cities, 'areas': areas})


def list_customers(request):
    customers = Customer.objects.all()
    states = State.objects.all()
    cities = City.objects.all()
    areas  = Area.objects.all()


    state_id = request.GET.get('state')
    city_id = request.GET.get('city')
    area_id = request.GET.get('area')

    selected_state = None
    selected_city = None

    if state_id:
        customers = customers.filter(area__city__state=state_id)
        cities = cities.filter(state_id=state_id)
        selected_state = State.objects.get(id=state_id).name

    if city_id:
        customers = customers.filter(area__city=city_id)
        areas = areas.filter(city_id=city_id)
        selected_city = City.objects.get(id=city_id).name

    if area_id:
        customers = customers.filter(area=area_id)

    context = {
        'customers': customers,
        'states': states,
        'cities': cities,
        'areas': areas,
        'selected_state': selected_state,
        'selected_city': selected_city,
        'selected_state_id': state_id,
        'selected_city_id': city_id,
        'selected_area_id': area_id,
        'segment':'add_customer'
    }

    return render(request, 'home/list_customers.html', context)


def update_customer(request, id):
    customer = Customer.objects.get(id=id)
    states = State.objects.all()
    cities = City.objects.all()
    areas = Area.objects.all()
    if request.method == 'POST':
        selected_state_id = customer.area.city.state.id
        selected_city_id = customer.area.city.id
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.contact_no = request.POST.get('contact_no')

        profile_image = request.FILES.get('profile_image')
        if profile_image:
            customer.profile_image = profile_image

        customer.save()
        messages.success(request, 'User updated successfully.')

        return redirect('list_customers') 
    return render(request, 'home/update_customer.html', {'customer':customer, 'segment':'customer','states': states,
                    'cities': cities,
                    'areas': areas, })

def delete_customer(request, id):
    try:
        customer = Customer.objects.get(id=id)
        customer.delete()  
        messages.error(request, 'User deleted successfully.')
        return redirect('list_customers')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_customers')



#Property

def add_property(request):
    try:
        form = PropertyTermsForm(request.POST)
        clients = Client.objects.all()
        areas = Area.objects.all()
        states = State.objects.all()
        cities = City.objects.all()
        areas = Area.objects.all()

        if request.method == 'POST':
            form = PropertyTermsForm(request.POST)
            owner_id = request.POST.get('owner')
            owner = Client.objects.get(id=owner_id)
            area_id = request.POST.get('area')

            try:
                area = Area.objects.get(id=area_id)  # Get the Area object based on the selected area value
            except Area.DoesNotExist:
                area = None
                print('Invalid area')
                # Return an error message to the user or handle the invalid area case

            property_obj = Properties(
                name=request.POST.get('property_name'),
                price=request.POST.get('price'),
                root_image=request.FILES.get('root_image'),
                description=request.POST.get('description'),
                owner=owner,
                area_id=area,
                address=request.POST.get('address'),
                status='active',
            )
            property_obj.save()

            # Add Property images
            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=property_obj, image=image)

            # Add Property Videos
            videos = request.FILES.getlist('videos')
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
            messages.success(request, 'Property added successfully.')
            return redirect('list_properties')

        if 'state_id' in request.GET:
            state_id = request.GET.get('state_id')
            cities = City.objects.filter(state_id=state_id)

        if 'city_id' in request.GET:
            city_id = request.GET.get('city_id')
            areas = Area.objects.filter(city_id=city_id)

        return render(request, 'home/add_property.html', {'clients': clients, 'states': states, 'cities': cities, 'areas': areas, 'segment': 'property', 'form': form})

    except Exception as e:
        print(e)
        messages.error(request, 'Invalid Credentials')
    return render(request, 'home/add_property.html', {'clients': clients, 'states': states, 'cities': cities, 'areas': areas, 'segment': 'property', 'form': form})


def list_properties(request):
    properties = Properties.objects.all()
    states = State.objects.all()
    cities = City.objects.all()
    areas  = Area.objects.all()


    state_id = request.GET.get('state')
    city_id = request.GET.get('city')
    area_id = request.GET.get('area')

    selected_state = None
    selected_city = None

    if state_id:
        properties = properties.filter(area_id__city__state=state_id)
        cities = cities.filter(state_id=state_id)
        selected_state = State.objects.get(id=state_id).name

    if city_id:
        properties = properties.filter(area_id__city=city_id)
        areas = areas.filter(city_id=city_id)
        selected_city = City.objects.get(id=city_id).name

    if area_id:
        properties = properties.filter(area_id=area_id)

    context = {
        'properties': properties,
        'states': states,
        'cities': cities,
        'areas': areas,
        'selected_state': selected_state,
        'selected_city': selected_city,
        'selected_state_id': state_id,
        'selected_city_id': city_id,
        'selected_area_id': area_id,
    }

    return render(request, 'home/list_properties.html', context)

def delete_image(request, image_id):
    try:
        image = PropertyImage.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'status': 'success'})
    except PropertyImage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Image not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def delete_video(request, video_id):
    try:
        video = PropertyVideo.objects.get(id=video_id)
        video.delete()
        return JsonResponse({'status': 'success'})
    except PropertyVideo.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Video not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def update_property(request, id):
    try:
        property_obj = Properties.objects.get(id=id)
        clients = Client.objects.all()
        property_images = PropertyImage.objects.filter(property=property_obj)
        property_videos = PropertyVideo.objects.filter(property=property_obj)
        num_images = property_images.count()
        num_videos = property_videos.count()
        property_terms = PropertyTerms.objects.filter(property=property_obj).first()
        states = State.objects.all()
        cities = City.objects.all()
        areas = Area.objects.all()

        if request.method == 'POST':
            form = PropertyTermsForm(request.POST, instance=property_terms)
            selected_state_id = property_obj.area_id.city.state.id
            selected_city_id = property_obj.area_id.city.id
            owner_id = request.POST.get('owner')
            owner = None
            try:
                owner = Client.objects.get(id=owner_id)
            except Client.DoesNotExist:
                print('Client Not found')


            # Update property fields
            if 'property_name' in request.POST:
                property_obj.name = request.POST.get('property_name')
            if 'price' in request.POST:
                property_obj.price = request.POST.get('price')
            if 'root_image' in request.FILES:
                property_obj.root_image = request.FILES.get('root_image')
            if 'description' in request.POST:
                property_obj.description = request.POST.get('description')
            if 'owner' in request.POST:
                property_obj.owner = owner
            if 'address' in request.POST:
                property_obj.address = request.POST.get('address')
            if 'status' in request.POST:
                property_obj.status = request.POST.get('status')
            if 'area' in request.POST:
                area_id = request.POST.get('area')
                area = Area.objects.get(id=area_id)
                property_obj.area_id = area
                print(property_obj.area_id)
            property_obj.save()

            # Update property images
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image in images:
                    PropertyImage.objects.create(property=property_obj, image=image)

            # Update property videos
            if 'videos' in request.FILES:
                videos = request.FILES.getlist('videos')
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
            messages.success(request, 'Property updated successfully.')
            return redirect('list_properties')
        else:
            form = PropertyTermsForm(instance=property_terms)
            selected_state_id = property_obj.area_id.city.state.id
            selected_city_id = property_obj.area_id.city.id
            return render(
                request, 'home/update_property.html',
                {
                    'property': property_obj,
                    'property_images': property_images,
                    'property_videos': property_videos,
                    'clients': clients,
                    'segment': 'property',
                    'num_images': num_images,
                    'num_videos': num_videos,
                    'form': form,
                    'states': states,
                    'cities': cities,
                    'areas': areas,
                }
            )
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
                   'form': form,
                   "states": states, 'cities': cities, 'areas': areas,
                   })


def delete_property(request, id):
    try:
        property = Properties.objects.get(id=id)
        property.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('list_properties')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_properties')

        


def add_commission(request):
    try:
        clients = Client.objects.all()
        if request.method == 'POST':
            client_id = request.POST.get('client')
            commission_percent = request.POST.get('commission_percent')
            client = Client.objects.get(id=client_id)
            
            # Check if a commission already exists for the client
            existing_commission = Commission.objects.filter(client=client).exists()

            if existing_commission:
                commission = Commission.objects.get(client=client)
                commission.commission_percent = commission_percent
                commission.save()
                

            else:
                commission = Commission(client=client, commission_percent=commission_percent)
                commission.save()
            messages.success(request, 'Commission added successfully.')

            return redirect('list_commission')
    except Exception as e:
        messages.error(request, 'Invalid Credentials')
    
    return render(request, 'home/add_commission.html', {'clients': clients, 'segment': 'commission'})


def list_commission(request):
    commissions = Commission.objects.all()
    states = State.objects.all()
    cities = City.objects.all()
    areas = Area.objects.all()

    state_id = request.GET.get('state')
    city_id = request.GET.get('city')
    area_id = request.GET.get('area')

    selected_state = None
    selected_city = None

    if state_id:
        commissions = commissions.filter(client__area__city__state=state_id)
        cities = cities.filter(state_id=state_id)
        selected_state = State.objects.get(id=state_id).name

    if city_id:
        commissions = commissions.filter(client__area__city=city_id)
        areas = areas.filter(city_id=city_id)
        selected_city = City.objects.get(id=city_id).name

    if area_id:
        commissions = commissions.filter(client__area=area_id)

    context = {
        'commissions': commissions,
        'states': states,
        'cities': cities,
        'areas': areas,
        'selected_state': selected_state,
        'selected_city': selected_city,
        'selected_state_id': state_id,
        'selected_city_id': city_id,
        'selected_area_id': area_id,
    }
    
    return render(request, 'home/list_commission.html', context)

def update_commission(request, id):
    try:
        commission = Commission.objects.get(id=id)
        clients = Client.objects.all()

        if request.method == 'POST':
            commission_percent = request.POST.get('commission_percent')
            commission.commission_percent = commission_percent
            commission.save()
            messages.success(request, 'Commission updated successfully.')

            return redirect('list_commission')

    except Commission.DoesNotExist:
        messages.error(request, 'Invalid Credentials')

        return redirect('list_commission')

    return render(request, 'home/update_commission.html', {'commission': commission, 'clients': clients})

def delete_commission(request, id):
    try:
        commission = Commission.objects.get(id=id)
        commission.delete()
        messages.error = (request, "Commission deleted successfully")
        return redirect('list_commission')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_commission')


def list_bookings(request):
    try:
        bookings = BookProperty.objects.all()
        states = State.objects.all()
        cities = City.objects.all()
        areas = Area.objects.all()
        clients = Client.objects.all()


        state_id = request.GET.get('state')
        city_id = request.GET.get('city')
        area_id = request.GET.get('area')

        owner_id = request.GET.get('owner')

        if owner_id:
            bookings = bookings.filter(property__owner=owner_id)
        selected_state = None
        selected_city = None

        if state_id:
            bookings = bookings.filter(property__area_id__city__state=state_id)
            cities = cities.filter(state_id=state_id)
            selected_state = State.objects.get(id=state_id).name

        if city_id:
            commissions = commissions.filter(property__area_id__city=city_id)
            areas = areas.filter(city_id=city_id)
            selected_city = City.objects.get(id=city_id).name

        if area_id:
            commissions = commissions.filter(property__area_id=area_id)
        context = {
        'bookings': bookings,
        'states': states,
        'cities': cities,
        'areas': areas,
        'clients':clients,
        'selected_owner':owner_id,
        'selected_state': selected_state,
        'selected_city': selected_city,
        'selected_state_id': state_id,
        'selected_city_id': city_id,
        'selected_area_id': area_id,
    }
        return render(request, 'home/list_bookings.html', context)
    except Exception as e:
        print(e)
                      

