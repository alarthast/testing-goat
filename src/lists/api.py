from django.http import HttpResponse


def single_list(request, list_id):
    return HttpResponse(content_type="application/json")
