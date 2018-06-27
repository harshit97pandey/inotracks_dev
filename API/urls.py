from django.conf.urls import url
from django.contrib import admin

from API.views import *
from API.web_view import *

urlpatterns = [
    url(r'^update_location_and_parameters/', update_location_and_parameters),
     url(r'^update_stop_location/', update_stop_location),
    url(r'^get_bus_data_current_time/', get_bus_data_current_time),
    url(r'^get_bus_data_from_time/', get_bus_data_from_time),
    url(r'^web/get_bus_locations/', get_bus_location_ajax),
    url(r'^web/marker_update/', marker_update),
    url(r'^web/get_fuel_data/', get_fuel_data),
    url(r'^get_bus_data_user/', get_bus_data_from_user),
    url(r'^get_stop_data_from_time/', get_stop_data_from_time),

    url(r'^update_status/', update_status),

    url(r'^get_json_from_csv/', get_json_from_csv),

    url(r'^get_bus_location_from_time/', get_bus_location_from_time),
    url(r'^get_all_bus_data/',get_all_bus_data),
]

