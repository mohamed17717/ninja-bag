from django.http import HttpResponse, JsonResponse
import json
from PIL import Image
from toolsframe.models import Tool, UpcomingTool
from utils.handlers import ToolHandler
from toolsframe.forms import SuggestToolForm


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


def GenerateDefaultContext(request):
  is_authenticated = request.user.is_authenticated
  context = {
    'upcoming_tools': UpcomingTool.objects.get_active(),
    'is_limits_active': ToolHandler.is_limits_active,
    'is_authenticated': request.user.is_authenticated,
    'suggest_form': SuggestToolForm
  }

  if is_authenticated:
    user = request.user
    context.update({ 
      'account': user.user_account,
      'db_tools': Tool.objects.get_tools_that_has_db_for_aside_section(user)
    })

  return context

