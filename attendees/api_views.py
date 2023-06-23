from django.http import JsonResponse
from .models import Attendee
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
from events.models import Conference
import json
from events.api_views import ConferenceDetailEncoder


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name",
    ]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name",
        "email",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceDetailEncoder(),
    }

    def get_extra_data(self, o):
        return super().get_extra_data(o)


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
            )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )
        attendee = Attendee.objects.create(**content)
        return JsonResponse(attendee,
                            encoder=AttendeeDetailEncoder,
                            safe=False,
                            )

# def api_list_attendees(request, conference_id):
#     attendees = [
#         {
#             "name": a.name,
#             "href": a.get_api_url(),
#         }
#         for a in Attendee.objects.filter(conference=conference_id)
#     ]
#     return JsonResponse({"attendees": attendees})

@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_attendee(request, id):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            {"attendee": attendee},
            encoder=AttendeeDetailEncoder,
            )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count> 0})
    else:
        content = json.loads(request.body)
        Attendee.objects.filter(id=id).update(**content)
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


# def api_show_attendee(request, id):
    # attendee = Attendee.objects.get(id=id)
    # return JsonResponse(
        # {
            # "email": attendee.email,
            # "name": attendee.name,
            # "company_name": attendee.company_name,
            # "created": attendee.created,
            # "conference": {
                # "name": attendee.conference.name,
                # "href": attendee.conference.get_api_url(),
            # }
        # }
    # )
