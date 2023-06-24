from django.http import JsonResponse
from .models import Conference, Location, State
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json
from .acls import get_photo, get_weather_data


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
        "starts",
        "ends",
        "description",
        "created",
        "updated",
        "max_presentations",
        "max_attendees",
        "location",
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
        "photo",
    ]

    def get_extra_data(self, o):
        return { "state": o.state.abbreviation }




@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
        )
    else:
        content = json.loads(request.body)
    try:
        location = Location.objects.get(id=content["location"])
        content["location"] = location
    except Location.DoesNotExist:
        return JsonResponse(
            {"message": "Invalid location id"},
            status=400,
        )
    conference = Conference.objects.create(**content)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, id):
    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        city = conference.location.city
        state = conference.location.state.abbreviation
        weather = get_weather_data(city, state)
        return JsonResponse(
            {"conference": conference, "weather": weather},
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        conference = Conference.objects.filter(id=id).update(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    if request.method == "GET":
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
                )
        Location.objects.filter(id=id).update(**content)
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
            )


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
                )
        photo = get_photo(content["city"], content["state"].abbreviation)
        content.update(photo)
        location = Location.objects.create(**content)
    return JsonResponse(
        location,
        encoder=LocationDetailEncoder,
        safe=False,
    )




# def api_list_locations(request):
#     response = []
#     locations = Location.objects.all()
#     for location in locations:
#         response.append(
#             {
#                 "name": location.name,
#                 "href": location.get_api_url(),
#             }
#         )
#     return JsonResponse({"location": response})


# def api_list_conferences(request):
#     response = []
#     conferences = Conference.objects.all()
#     for conference in conferences:
#         response.append(
#             {
#                 "name": conference.name,
#                 "href": conference.get_api_url(),
#             }
#         )
#     return JsonResponse({"conferences": response})


# def api_show_conference(request, id):
#     conference = Conference.objects.get(id=id)
#     return JsonResponse(
#         {
#             "name": conference.name,
#             "starts": conference.starts,
#             "ends": conference.ends,
#             "description": conference.description,
#             "created": conference.created,
#             "updated": conference.updated,
#             "max_presentations": conference.max_presentations,
#             "max_attendees": conference.max_attendees,
#             "location": {
#                 "name": conference.location.name,
#                 "href": conference.location.get_api_url(),
#             },
#         }
#     )



# def api_show_location(request, id):
#     location = Location.objects.get(id=id)
#     return JsonResponse(
#         {
#             "name": location.name,
#             "city": location.city,
#             "room_count": location.room_count,
#             "created": location.created,
#             "updated": location.updated,
#             "state": location.state.name,
#         }
#     )
