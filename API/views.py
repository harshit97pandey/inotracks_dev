from django.shortcuts import render, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UpdateStatus
import json
from datetime import datetime, timedelta,date
from django.contrib.auth import authenticate
from Buses.models import *

from django.shortcuts import render

import pandas as pd



@csrf_exempt
def update_location_and_parameters(request):
    if request.method == "POST":
        post = json.loads(request.body.decode("utf-8"))
        print(post)
        response_data = {}
        if post.get("key") == "70b66a89929e93416d2ef535893ea14da331da8991cc7c74010b4f3d7fabfd62":
            bus_number = post['bus_number']
            time_recorded = datetime.strptime(post['time_recorded'], '%d/%m/%Y %H:%M:%S')
            if post['known_location'] == 'true':
                place_name = post['place_name']
                try:
                    Location.objects.create(bus_number=bus_number,
                                            place_name=place_name,
                                            known_location=True,
                                            time_recorded=time_recorded,
                                            )
                    response_data['status'] = 'Success'
                except Exception as e:
                    response_data['status'] =  str(e)
                    print(e)

            else:
                latitude = post['latitude']
                longitude = post['longitude']
                fuel = post['fuel']
                speed = post['speed']
                battery=post['battery']
                distance = post['distance']
                try:
                    location = Location.objects.create(bus_number=bus_number,
                                                        latitude=latitude,
                                                        longitude=longitude,
                                                        time_recorded=time_recorded,
                                                        )

                    Bp = BusParameter.objects.create(bus_number=bus_number,
                                                    speed=speed,
                                                    fuel=fuel,
                                                    battery=battery,
                                                    distance=distance,
                                                    time_recorded=time_recorded
                                                    )
                    bus = Bus.objects.get(bus_number=bus_number)
                    bus.location = location
                    bus.parameters = Bp
                    bus.save()

                    response_data['status'] = 'true'
                except Exception as e:
                    response_data['status'] = str(e)
                    print(e)

        else:
            response_data['status'] = 'Request Invalid'

        return HttpResponse(
            json.dumps(response_data),
            content_type = "application/json"
            )
    else:
        raise Http404("NOT ALLOWED")


@csrf_exempt
def get_bus_data_current_time(request):
    if request.method == "POST":
        response_data = {}
        try:
            post = json.loads(request.body.decode("utf-8"))
            if post.get("key") == '32c25a275fdf9df2668560732691af2a95c53429605c34ea989fd359':
                bus_number = post['bus_number']
                try:
                    bus = Bus.objects.get(bus_number=bus_number)
                    location = bus.location
                    bus_parameters = bus.parameters
                    location_data = {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                    }
                    response_data["location"] = location_data
                    response_data["time_recorded"] = str(location.time_recorded)
                    response_data["speed"] =  bus_parameters.speed
                    response_data["fuel"] = bus_parameters.fuel
                    response_data["battery"] = bus_parameters.battery
                    response_data["distance"] = bus_parameters.distance
                    response_data["status"] = "true"

                except Exception as e:
                    response_data["status"] = str(e)
                    print(e)

            else:
                response_data['status'] = 'Request Invalid'
        except Exception as e:
            response_data['error'] = e
        return HttpResponse(
            json.dumps(response_data),
                content_type = "application/json"
            )
    else:
        raise Http404("NOT ALLOWED")

@csrf_exempt
def get_bus_data_from_time(request):
    if request.method == "POST":
        response_data = {}
        try:
            post = json.loads(request.body.decode("utf-8"))
            if post.get("key") == 'bd0e7468203f76439a9d4cb3d29a2403cfe49e41e781813e0cdec392cf054dc9':
                bus_number = post['bus_number']
                from_time = datetime.strptime(post['from_time'], '%d/%m/%Y %H:%M:%S')
                to_time = datetime.strptime(post['to_time'], '%d/%m/%Y %H:%M:%S')
                try:
                    bus = Bus.objects.get(bus_number=bus_number)
                    total_locations = Location.objects.filter(bus_number=bus_number,
                                                                known_location=False,
                                                                time_recorded__gte=from_time,
                                                                  time_recorded__lte=to_time,
                                                                )
                    print(total_locations)
                    index = -1
                    locations = {}
                    for index, location in enumerate(total_locations):
                        data = {
                                "latitude": location.latitude,
                                "longitude": location.longitude,
                                "time_recorded": str(location.time_recorded),
                                }
                        locations[index] = data

                    response_data["locations"] = locations
                    response_data["number_of_locations"] = index + 1
                    total_known_locs = Location.objects.filter(bus_number=bus_number,
                                                                known_location=True,
                                                                time_recorded__gte=from_time,
                                                               time_recorded__lte=to_time,
                                                                )
                    locations = {}
                    for index, location in enumerate(total_known_locs):
                        data = {"place_name": location.place_name,
                                "time_recorded": str(location.time_recorded),
                                }
                        locations[index] = data
                    response_data["known_locations"] = locations
                    response_data["number_of_known_locations"] = index + 1
                    bus_parameters = BusParameter.objects.filter(bus_number=bus_number,
                                                                time_recorded__gte=from_time,
                                                                 time_recorded__lte=to_time,
                                                                )
                    speed_data, fuel_data , distance_data = {}, {}, {}
                    for index, bus_param in enumerate(bus_parameters):
                        time_recorded = bus_param.time_recorded
                        speed = {
                                "speed": bus_param.speed,
                                "time_recorded": str(time_recorded)
                            }
                        fuel = {
                                "fuel": bus_param.fuel,
                                "time_recorded": str(time_recorded)
                            }
                        battery = {
                                "battery": bus_param.battery,
                                "time_recorded": str(time_recorded)
                            }
                        distance = {
                                "distance": bus_param.distance,
                                "time_recorded": str(time_recorded)
                            }
                        speed_data[index] = speed
                        fuel_data[index] = fuel
                        distance_data[index] = distance
                    response_data["number_of_parameters"] = index + 1
                    response_data["speed_data"] = speed_data
                    response_data["fuel_data"] = fuel_data
                    response_data["battery"] = battery
                    response_data["distance_data"] = distance_data

                    response_data["status"] = "true"

                except Exception as e:
                    response_data["status"] = str(e)
                    print(e)
            else:
                response_data['status'] = 'Request Invalid'
        except Exception as e:
            response_data['error'] = e
        return HttpResponse(
            json.dumps(response_data),
                content_type = "application/json"
            )
    else:
        raise Http404("NOT ALLOWED")


@csrf_exempt
def get_bus_data_from_user(request):
    if request.method == "POST":
        response_data = {}
        try:
            post = json.loads(request.body.decode("utf-8"))
            if post.get("key") == '32c25a275fdf9df2668560732691af2a95c53429605c34ea989fd359':
                username = post['username']
                password = post['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    try:
                        buses = Bus.objects.filter(owner=user)
                        buss = {}
                        for index, bus in enumerate(buses):
                            data = {
                                    "bus_number": bus.bus_number,
                                    "driver": bus.driver.name,
                                    "latitude": bus.location.latitude,
                                    "longitude": bus.location.longitude,
                                    "time_recorded": str(bus.location.time_recorded),
                                    }
                            buss[index] = data

                        response_data["buses"] = buss


                    except Exception as e:
                        response_data["status"] = str(e)
                        print(e)
                else:
                    return HttpResponse("Invalid login details supplied.")

            else:
                response_data['status'] = 'Request Invalid'
        except Exception as e:
            response_data['error'] = e
        print(response_data)
        return HttpResponse(
            json.dumps(response_data),
                content_type = "application/json"
            )
    else:
        raise Http404("NOT ALLOWED")

@csrf_exempt
def update_stop_location(request):
    if request.method == "POST":
        post = json.loads(request.body.decode("utf-8"))
        print(post)
        response_data = {}
        if post.get("key") == "70b66a89929e93416d2ef535893ea14da331da8991cc7c74010b4f3d7fabfd62":
            bus_number = post['bus_number']
            latitude = post['latitude']
            longitude = post['longitude']
            arrival_time = datetime.strptime(post['arrival_time'], '%d/%m/%Y %H:%M:%S')
            departure_time = datetime.strptime(post['departure_time'], '%d/%m/%Y %H:%M:%S')
            try:
                location = Location.objects.create(bus_number=bus_number,
                                                        latitude=latitude,
                                                        longitude=longitude,
                                                        )
                stop = Stop.objects.create(location=location,
                                               arrival_time=arrival_time,
                                               departure_time=departure_time,
                                               )
                response_data['status'] = 'true'
            except Exception as e:
                response_data['status'] = str(e)
                print(e)

        else:
            response_data['status'] = 'Request Invalid'

        return HttpResponse(
            json.dumps(response_data),
            content_type = "application/json"
            )
    else:
        raise Http404("NOT ALLOWED")

@csrf_exempt
def get_stop_data_from_time(request):
    if request.method == "POST":
        response_data = {}
        try:
            post = json.loads(request.body.decode("utf-8"))
            if post.get("key") == 'bd0e7468203f76439a9d4cb3d29a2403cfe49e41e781813e0cdec392cf054dc9':
                bus_number = post['bus_number']
                from_time = datetime.strptime(post['from_time'], '%d/%m/%Y %H:%M:%S')
                to_time = datetime.strptime(post['to_time'], '%d/%m/%Y %H:%M:%S')
                try:
                    stops = Stop.objects.filter(arrival_time__gte=from_time,
                                                departure_time__lte=to_time,
                                                )
                    print(stops)
                    stops1 = {}
                    for index, stop in enumerate(stops):
                        location= stop.location
                        if location.bus_number == bus_number:
                            data = {
                                "latitude": stop.location.latitude,
                                "longtitude": stop.location.longitude,
                                "halt_time": str(stop.halt_time),
                                }
                        stops1[index] = data
                    response_data["stops"] = stops1
                except Exception as e:
                    response_data["status"] = str(e)
                    print(e)
            else:
                response_data['status'] = 'Request Invalid'
        except Exception as e:
            response_data['error'] = e
        return HttpResponse(json.dumps(response_data),
                content_type = "application/json")
    else:
        raise Http404("NOT ALLOWED")

@csrf_exempt

def update_status(request):
    if request.method == 'GET':
        template = 'update_status.html'
        return render(request, template, {})
    if request.method == 'POST':
        raise Http404("adasd")
        
def get_current_driver(request,pk=None):
    driver=UpdateStatus.objects.all
    current_driver=driver.new_driver
    last_driver=driver.previous_driver

    template='tabularview.html'
    return render(request,template,context={'current_driver':current_driver})

def get_json_from_csv(request):
    if request.method == "GET":
        path = request.GET.get('path')
        response_data = {}
        try:
            csv_from_path = pd.read_csv(str(path))
            json_from_csv = pd.DataFrame.to_json(csv_from_path)
            response_data = json_from_csv
        except Exception as e:
            response_data['status'] = str(e)
            print(e)
    else:
        response_data['status'] = 'Request Invalid'
    return HttpResponse(
        response_data,
        content_type='application/json'
)


from geopy.distance import geodesic
@csrf_exempt
def get_nearest_bus(request):
 if request.method == "POST":
  response_data = {}
  try:
   post = json.loads(request.body.decode("utf-8"))
   if post.get("key") == 'bd0e7468203f76439a9d4cb3d29a2403cfe49e41e781813e0cdec392cf054dc9':
    latitude = post['lat']
    longitude = post['long']
    latitude = float(latitude)
    longitude = float(longitude)
    user_location=[latitude,longitude]
    
    try:
     get_all_bus = Location.objects.all()
     list_bus_3km=[]
     list_bus_5km=[]
     for location in get_all_bus:
      bus_location=[location.latitude,location.longitude]   
      bus_num=location.bus_number
      bus_parameter=BusParameter.objects.get(bus_number=bus_num)
      dist=geodesic(user_location, bus_location)
      dist_km=dist.km
      
      count_3km=0
      count_5km=0
      print "BUS_LOC:MY_LOC",bus_location,user_location
      print "DISTANCE:",dist_km
      
      
      if(dist_km<4) :
       data={
       'distance_from_req_location':dist_km,
       'bus_number': bus_num,
       'speed': bus_parameter.speed,
       'fuel': bus_parameter.fuel,
       'battery': bus_parameter.battery,
       'distance': bus_parameter.distance,
       'time_recorded': str(bus_parameter.time_recorded)
        }
       list_bus_3km.append(data)
       count_3km += 1
      if(dist_km<6):
       if (dist_km>4):
        data={
        'distance_from_req_location':dist_km,
        'bus_number': bus_num,
        'speed': bus_parameter.speed,
        'fuel': bus_parameter.fuel,
        'battery': bus_parameter.battery,
        'distance': bus_parameter.distance,
        'time_recorded': str(bus_parameter.time_recorded)
         }
        count_5km += 1
        list_bus_5km.append(data)
      print list_bus_3km
      if (count_3km>0)or(count_5km>0):
       resp={
       'number_of_near_3km':count_3km,
       'number_of_near_5km':count_5km,
       'bus_near_3km':list_bus_3km,
       'bus_near_5km':list_bus_5km
        }
      else:
       resp={'message':'There is no bus'}
      response_data["resp"] = resp
    except Exception as e:
     response_data["status"] = str(e)
     print(e)
   else:
    response_data['status'] = 'Request Invalid'
  except Exception as e:
   response_data['error'] = e
  return HttpResponse(json.dumps(response_data),content_type = "application/json")

 else:
  raise Http404("NOT ALLOWED")



@csrf_exempt
def get_all_bus_data(request):
    if request.method == "POST":
        response_data = {}
        try:
            post = json.loads(request.body.decode("utf-8"))
            if post.get("key") == "70b66a89929e93416d2ef535893ea14da331da8991cc7c74010b4f3d7fabfd62":
                for bus in Bus.objects.all():
                    bus_data = {}
                    last_location = {
                        "latitude" : bus.location.latitude,
                        "longitude" : bus.location.longitude,
                        "place_name":bus.location.place_name,
                        "known_location":bus.location.known_location,
                        "time_recorded": str(bus.location.time_recorded),
                    }
                    
                    if post['from_time'] == "yesterday":
                        from_time=date.today()-timedelta(1)
                    elif post['from_time'] == "lastweek":
                        from_time = date.today()-timedelta(7)
                    elif post['from_time'] == "lastmonth":
                        today = date.today()
                        try:
                            from_time = today.replace(month=today.month-1)
                        except ValueError:
                            if today.month == 1:
                                from_time = today.replace(year=today.year-1,month=12)
                            else:
                                raise
                    else:
                        from_time = datetime.strptime(post["from_time"], '%d/%m/%Y %H:%M:%S')

                    #print(from_time)
                    count = Location.objects.filter(bus_number=bus.bus_number,
                                                                known_location=True,
                                                                time_recorded__gte=from_time,
                                                                ).count()
                    #print(count)
                    if count == 0:
                        start_location = "bus not moved after this time"
                    else:
                        location = Location.objects.filter(bus_number=bus.bus_number,
                                                                known_location=True,
                                                                time_recorded__gte=from_time,
                                                                ).order_by('time_recorded')[0]
                        #print(location)
                        start_location =   {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "place_name":location.place_name,
                            "time_recorded": str(location.time_recorded),
                        }
                    
                    bus_data = {
                        "driver":bus.driver,
                    }
                    bus_data["start_location"]=start_location
                    bus_data["last_location"] = last_location 
                    response_data[bus.bus_number] = bus_data
            else:
                response_data['status'] = 'Request Invalid'
        except Exception as e:
            response_data['error'] = e
        return HttpResponse(
            json.dumps(response_data),
                content_type = "application/json"
            )
    else:
        raise Http404("NOT ALLOWED")