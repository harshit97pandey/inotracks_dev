from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Buses.models import *
from users.models import *
from datetime import datetime, timedelta

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def IndexView(request):
    template = 'index.html'
    return render(request, template, {})

def LoginView(request):
    template = 'login.html'
    if request.user.is_authenticated():
        return redirect('/map')
    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        user = authenticate(username=username, password=password)
        print(username, password, user)
        if user is not None:
            if user.is_active:
                login(request, user)
                print(user)
                return redirect('/map')
        else:
            messages.warning(request,'Incorrect Credentials!', fail_silently=True)
            return redirect("/login")

    return render(request, template, {})

@login_required(login_url="/login")
def MapView(request):
    template = 'mapview.html'
    user = request.user
    context = {
        'name': user.name,
        'username': user.username
    }
    return render(request, template, context)

@login_required(login_url="/login")
@csrf_exempt
def TabularView(request):
    template = "tabularview.html"
    user = request.user
    
    #if the flag=1 the ajax request will be processed else the normal GET request will get processed
    flag=0
    if request.is_ajax():
       _id=request.GET.get('id',1)
       flag=1
       buss=Bus.objects.filter(id=_id)
       #print(_id)
       
    if flag==0: 
       buss=Bus.objects.filter(owner=user).order_by('running_status').reverse()

    for bus in buss:
        if not bus.location.known_location:
            base = "https://maps.googleapis.com/maps/api/geocode/json?"
            params = "latlng={lat},{lon}&key=AIzaSyCm24VQsd__wlG2Q3NnxernN67KMbvabas".format(
                lat = bus.location.latitude,
                lon = bus.location.longitude,
                sen = 'true',
                )
            # base="https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&accept-language=en".format(
            #     lat = bus.location.latitude,
            #     lon = bus.location.longitude,
                
            #     )

            url = "{base}{params}".format(base=base, params=params)
            # url = "{base}".format(base=base)
            # response = requests.get(url)
            # print(response.json()['results'][0])    
            # bus.location.place_name = response.json()['display_name']
            
            
            try:
                response = requests.get(url)
                
                bus.location.place_name = response.json()['results'][0]['formatted_address']

            except Exception as e:

                bus.location.place_name = response.json()['status']

            bus.location.save()

        from_time=int(datetime.now().strftime('%Y%m%d%H%M%S'))
        total_locations = Location.objects.filter(bus_number=bus.bus_number).last()
        
        '''last_t=int(total_locations.time_recorded.strftime('%Y%m%d%H%M%S'))

        if from_time-last_t<500 :
            bus.running_status=True
        else :
            bus.running_status=False'''

        bus.save()
    context = {
    'buses':buss,
    'name': user.name,
    'username': user.username,
    }
    return render(request, template, context)

@login_required(login_url="/login")
def TimeTableView(request):
    user = request.user
    template = "timetable.html"

    context = {
    'name': user.name,
    'username': user.username,
    'time_tables':[],
    }
    buses = Bus.objects.filter(owner=user)
    for bus in buses:
        context['time_tables'].extend(TimeTable.objects.filter(bus=bus))
    print(context)

    return render(request, template, context)

def LogoutView(request):
    logout(request)
    return redirect('/login')
def importdata(request):
    import xlrd
    user = request.user
    if user.is_authenticated():
        book = xlrd.open_workbook("/var/www/html/inotracks/DRIVER AND VEHICLE DETAIL.xlsx")

        sheet = book.sheet_by_name("DRIVER AND VEHICLE DETAIL")


        for r in range(1, sheet.nrows):
            print(sheet.cell(r,0).value)

            try:
                ph_no=int(sheet.cell(r,3).value)
            except ValueError:
                ph_no=None
            driver_=InoDriver.objects.create(name=sheet.cell(r,1).value,
                phone_number=ph_no,
                driving_licence=sheet.cell(r,2).value)
            driver_.save()
            location = Location.objects.create(bus_number=sheet.cell(r,0).value)
                                                            
                                                            

            Bp = BusParameter.objects.create(bus_number=sheet.cell(r,0).value,
                speed=0,
                fuel=0,
                distance=0)
                                            
                                            
            bus = Bus.objects.create(bus_number=sheet.cell(r,0).value,
                owner=user,
                driver=driver_,
                location=location,
                parameters=Bp
                )
            
            bus.save()

@login_required(login_url="/login")
def DataEntry(request):
    template = 'data_entry.html'
    user = request.user
    if request.method == "POST":
        name = request.POST.get('name', None)
        phone_number = request.POST.get('phone_number', None)
        driving_licence = request.POST.get('driving_licence', None)
        bus_number = request.POST.get('bus_number', None)

        print ("aaya",name)
        if name and phone_number and driving_licence and bus_number:
            driver_valid=InoDriver.objects.filter(name=name,
                )
            bus_valid = Bus.objects.filter(bus_number=bus_number,
                
                )
            
            if driver_valid :
                return HttpResponse("Driver allready exists!!!")
            if bus_valid :
                return HttpResponse("Bus allready exists!!!")
            driver_=InoDriver.objects.create(name=name,
                phone_number=phone_number,
                driving_licence=driving_licence
                )
            driver_.save()
            location = Location.objects.create(bus_number=bus_number)
                                                            
                                                            

            Bp = BusParameter.objects.create(bus_number=bus_number,
                speed=0,
                fuel=0,
                distance=0)
                                            
                                            
            bus = Bus.objects.create(bus_number=bus_number,
                owner=user,
                driver=driver_,
                location=location,
                parameters=Bp
                )
            
            bus.save()
            return HttpResponse("Successful submission!!!")
       

    return render(request, template)
