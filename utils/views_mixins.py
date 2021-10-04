from toolsframe.models import Tool, UpcomingTool
from toolsframe.forms import SuggestToolForm
from django.http import HttpResponse, JsonResponse
from PIL import Image



def GenerateRequestContext(request):
  context = {
    'request': request,
    'is_authenticated': request.user.is_authenticated,
    'is_light_mode': request.COOKIES.get('light-mode', False),
    'previous_url': request.META.get('HTTP_REFERER', '/')
  }

  return context

def GenerateDefaultContext(request):
  context = {
    **GenerateRequestContext(request),
    'upcoming_tools': UpcomingTool.objects.get_active(),
    'is_limits_active': False,
    'suggest_form': SuggestToolForm,
  }

  if request.user.is_authenticated:
    user = request.user
    context.update({ 
      'account': user.user_account,
      'db_tools': Tool.objects.get_tools_that_has_db_for_aside_section(user)
    })

  return context

def JsonResponseOverride(data):
  return JsonResponse(data, safe=False, json_dumps_params={'indent': 2})

def ImageResponse(image:Image) -> HttpResponse:
  image_type = 'png' if image.mode == 'RGBA' else 'jpeg'

  response = HttpResponse(content_type=f"image/{image_type}")
  image.save(response, image_type)

  return response

