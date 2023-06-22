from django.http import JsonResponse
from .models import Conference, Location
from common.json import ModelEncoder


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
    ]

    def get_extra_data(self, o):
        return { "state": o.state.abbreviation }





def api_list_conferences(request):
    conferences = Conference.objects.all()
    return JsonResponse(
        {"conferences": conferences},
        encoder=ConferenceListEncoder,
    )


def api_show_conference(request, id):
    conference = Conference.objects.get(id=id)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )


def api_list_locations(request):
    response = []
    locations = Location.objects.all()
    for location in locations:
        response.append(
            {
                "name": location.name,
                "href": location.get_api_url(),
            }
        )
    return JsonResponse({"location": response})


def api_show_location(request, id):
    location = Location.objects.get(id=id)
    return JsonResponse(
        location,
        encoder=LocationDetailEncoder,
        safe=False,
    )
