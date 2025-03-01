from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, AdminTermsAndpolicyForm, PropertyTermsForm
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *
from userapi.models import BookProperty
from django.contrib.auth import login, logout
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
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from clientapi.models import ClientNotification
from userapi.models import CustomerNotification
from .helper import send_push_notification
from django.contrib.auth import update_session_auth_hash

# Create your views here.



# class password_reset_request(View):

#     def get(self,request):
#          return render(request=request, template_name="home/password_reset.html")

def password_reset(request):
    if request.method == "GET":
        return render(request=request, template_name="home/password_reset.html")
    if request.method == "POST":
        email = request.POST.get('email')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        print(new_password, confirm_password)
        if new_password == confirm_password:
            
            user = User.objects.get(email=email)
            print(user)
            
            user.set_password(new_password)
            user.save()
            
            # You might not need to update the session auth hash for this case
            
            messages.success(request, f'Password for {user.username} has been successfully updated.')
            return redirect(reverse('login'))
        else:
            messages.error(request, 'Passwords do not match.')
            return render(request=request, template_name="home/password_reset.html")




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
                    messages.error(request, 'Invalid password.')
                    return render(request, 'accounts/login.html', {'form': form, 'msg': 'Invalid Credentials'})
            except User.DoesNotExist:
                messages.error(request, 'Invalid email.')
                return render(request, 'accounts/login.html', {'form': form, 'msg': 'Invalid Credentials'})
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'accounts/login.html', {'form': form})


class Logout(View):
   def get(self,request):
      logout(request)
      messages.success(request, 'Logged out!.')
      return redirect(reverse('login'))
   

@method_decorator(login_required, name='dispatch')
class Index(View):
    def get(self,request):
      client = Client.objects.all()
      num_client = client.count()
      customers= Customer.objects.all()
      num_customer = customers.count()
      properties = Properties.objects.all()
      num_property = properties.count()
      bookings = BookProperty.objects.filter(book_status__in=[True])
      num_booking = bookings.count()
      return render(request,'home/index.html', {
          "num_client":num_client, 
          "num_customer":num_customer,
          "num_property":num_property,
          "num_booking":num_booking})
    
@login_required
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

# State
@login_required
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

        

@login_required
def list_state(request):
    states  = State.objects.all()
    return render(request, 'home/list_state.html', {'states':states})

@login_required
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
@login_required
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
@login_required
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
        
 
        

@login_required
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


@login_required
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

@login_required
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
@login_required
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
@login_required
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

@login_required
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

@login_required
def delete_area(request, id):
    try:
        area = Area.objects.get(id=id)
        area.delete()
        messages.error(request, 'Area deleted successfully.')
        return redirect('list_areas')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_areas')
@login_required
def get_cities(request):
    state_id = request.GET.get('state_id')
    if state_id:
        cities = City.objects.filter(state_id=state_id).values('id', 'name')
        return JsonResponse(list(cities), safe=False)
    else:
        return JsonResponse([], safe=False)

@login_required
def get_areas(request):
    city_id = request.GET.get('city_id')
    if city_id:
        areas = Area.objects.filter(city_id=city_id).values('id', 'name')
        return JsonResponse(list(areas), safe=False)
    else:
        return JsonResponse([], safe=False)




# Client 

@login_required
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

@login_required
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
@login_required
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
            area_id = request.POST.get('area')
            area = Area.objects.get(id=area_id)
            client.area = area
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

@login_required
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
 
@login_required     
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

@login_required
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

@login_required
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
        area_id = request.POST.get('area')
        area = Area.objects.get(id=area_id)
        customer.area = area
        if 'profile_image' in request.FILES:
            customer.profile_image = request.FILES.get('profile_image')
        

        customer.save()
        messages.success(request, 'User updated successfully.')

        return redirect('list_customers') 
    return render(request, 'home/update_customer.html', {'customer':customer, 'segment':'customer','states': states,
                    'cities': cities,
                    'areas': areas, })
@login_required
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
@login_required
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

@login_required
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
@login_required
def delete_image(request, image_id):
    try:
        image = PropertyImage.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'status': 'success'})
    except PropertyImage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Image not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"})

@login_required
def delete_video(request, video_id):
    try:
        video = PropertyVideo.objects.get(id=video_id)
        video.delete()
        return JsonResponse({'status': 'success'})
    except PropertyVideo.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Video not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"})
@login_required
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
            

            # Update property fields
            if 'property_name' in request.POST:
                property_obj.name = request.POST.get('property_name')
            if 'price' in request.POST:
                property_obj.price = request.POST.get('price')
            if 'root_image' in request.FILES:
                property_obj.root_image = request.FILES.get('root_image')
            if 'description' in request.POST:
                property_obj.description = request.POST.get('description')
            
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

@login_required
def delete_property(request, id):
    try:
        property = Properties.objects.get(id=id)
        property.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('list_properties')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_properties')

        
@login_required
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

@login_required
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
@login_required
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
@login_required
def delete_commission(request, id):
    try:
        commission = Commission.objects.get(id=id)
        commission.delete()
        messages.error = (request, "Commission deleted successfully")
        return redirect('list_commission')
    except:
        messages.error(request, 'Invalid Credentials')
        return redirect('list_commission')

@login_required
def list_bookings(request):
        bookings = BookProperty.objects.filter(book_status__in=[True])
        states = State.objects.all()
        cities = City.objects.all()
        areas = Area.objects.all()
        clients = Client.objects.all()


        state_id = request.GET.get('state')
        city_id = request.GET.get('city')
        area_id = request.GET.get('area')

        owner_id = request.GET.get('owner')

        
        selected_state = None
        selected_city = None

        if state_id:
            bookings = bookings.filter(property__area_id__city__state=state_id)
            cities = cities.filter(state_id=state_id)
            clients = clients.filter(area__city__state_id=state_id)
            selected_state = State.objects.get(id=state_id).name

        if city_id:
            bookings = bookings.filter(property__area_id__city=city_id)
            areas = areas.filter(city_id=city_id)
            clients = clients.filter(area__city_id=city_id)
            selected_city = City.objects.get(id=city_id).name

        if area_id:
            clients = clients.filter(area_id=area_id)
            bookings = bookings.filter(property__area_id=area_id)
        if owner_id:
            bookings = bookings.filter(property__owner=owner_id)
            
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
    
                      
@login_required
def booking_detail(request, id):
    booking = BookProperty.objects.get(id=id)
    return render(request, 'home/booking_detail.html', {'booking':booking})


def add_notification_client(request):

    if request.method == 'POST':
        title = request.POST.get('title')

        message = request.POST.get('message')

        
        selected_clients = request.POST.getlist('client') 

        if title and message and selected_clients:
         
            for client_id in selected_clients:
                try:
                    client_notification = ClientNotification.objects.create(
                        client_id=client_id,
                        title=title,
                        message=message,
                        send_by="admin"
                    )
                except Exception as e:
                    print(f"Error creating ClientNotification: {e}")
    
            return redirect('list_bookings') 

    context = {'clients': Client.objects.all(),}
        
    return render(request, "home/add_notification_client.html", context)



def add_notification_customer(request):

    if request.method == 'POST':
        title = request.POST.get('title')

        message = request.POST.get('message')

        selected_customers = request.POST.getlist('customer')

        if title and message and selected_customers:
         
            
            customers = Customer.objects.filter(id__in=selected_customers)
            receivers = [customer.fcm_token for customer in customers if customer.fcm_token]
            if receivers:
                send_push_notification(receivers, message, title) 
                print(receivers)

                for customer_id in selected_customers:
                    try:
                        customer_notification = CustomerNotification.objects.create(
                            customer_id=customer_id,
                            title=title,
                            message=message,
                            send_by="admin"
                        )
                    except Exception as e:
                        print(f"Error creating CustomerNotification: {e}")
            
            return redirect('list_bookings') 

    context = {'customers': Customer.objects.all(),}
        
    return render(request, "home/add_notification_customer.html", context)




def list_notification(request):
    client_notifications = ClientNotification.objects.filter(send_by="admin")
    customer_notifications = CustomerNotification.objects.filter(send_by="admin")

    return render(request, 'home/list_notification.html', {'client_notifications':client_notifications, "customer_notifications":customer_notifications})