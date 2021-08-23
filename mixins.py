from django.http import HttpResponse, JsonResponse
import json
from PIL import Image


def JsonResponseOverride(data):
  return JsonResponse(data, safe=False, json_dumps_params={'indent': 2})


def ExtractPostRequestData(request):
  # may be sent from forms of ajax so i extract it either way
  return json.loads(request.body.decode('utf8')) or request.POST


def ImageResponse(image:Image) -> HttpResponse:
  image_type = 'png' if image.mode == 'RGBA' else 'jpeg'

  response = HttpResponse(content_type=f"image/{image_type}")
  image.save(response, image_type)

  return response
