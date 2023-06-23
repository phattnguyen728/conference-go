from django.http import JsonResponse
from .models import Presentation
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json
from events.api_views import ConferenceListEncoder, Conference

class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        # "status",
        "conference",
    ]
    encoders = {
        "conference": ConferenceListEncoder(),
    }
    def get_extra_data(self, o):
        return {"status": o.status.name}


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
    ]
    def get_extra_data(self, o):
        return { "status": o.status.name }


@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_presentation(request, id):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        Presentation.objects.filter(id=id).update(**content)
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder,
            safe=False,
        )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Conference id"},
                status=400,
            )
        presentation = Presentation.objects.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )



# def api_list_presentations(request, conference_id):
#     presentations = [
#         {
#             "title": p.title,
#             "status": p.status.name,
#             "href": p.get_api_url(),
#         }
#         for p in Presentation.objects.filter(conference=conference_id)
#     ]
#     return JsonResponse({"presentations": presentations})


# def api_show_presentation(request, id):
#     presentation = Presentation.objects.get(id=id)
#     return JsonResponse(
#         {
#             "presenter_name": presentation.presenter_name,
#             "company_name": presentation.company_name,
#             "presenter_email": presentation.presenter_email,
#             "title": presentation.title,
#             "synopsis": presentation.synopsis,
#             "created": presentation.created,
#             "status": presentation.status.name,
#             "conference": {
#                 "name": presentation.conference.name,
#                 "href": presentation.conference.get_api_url(),
#             }
#         }
#     )
