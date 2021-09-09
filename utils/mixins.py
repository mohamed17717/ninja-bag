from django.http import HttpResponse, JsonResponse
import json
from PIL import Image
from toolsframe.models import Tool, UpcomingTool
from utils.handlers import ToolHandler
from toolsframe.forms import SuggestToolForm
from django.core.exceptions import ValidationError
from io import BytesIO
import uuid
from django.core.files import File
from django.core.files.base import ContentFile

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

def GenerateRequestContext(request):
  context = {
    'request': request,
    'is_authenticated': request.user.is_authenticated,
    'is_light_mode': request.COOKIES.get('light-mode', False)
  }

  return context

def GenerateDefaultContext(request):
  context = {
    **GenerateRequestContext(request),
    'upcoming_tools': UpcomingTool.objects.get_active(),
    'is_limits_active': ToolHandler.is_limits_active,
    'suggest_form': SuggestToolForm,
  }

  if request.user.is_authenticated:
    user = request.user
    context.update({ 
      'account': user.user_account,
      'db_tools': Tool.objects.get_tools_that_has_db_for_aside_section(user)
    })

  return context


def OptimizeImageField(image_field, min_dimension):
  image = Image.open(image_field)

  width, height = image.size
  new_width = min_dimension
  new_height = new_width * height / width
  if new_height < min_dimension:
    new_height = min_dimension
    new_width = new_height * width / height
  size = new_width, new_height

  source_image = image.convert('RGB')
  source_image.thumbnail(size, Image.ANTIALIAS)  # Resize to size
  output = BytesIO()
  source_image.save(output, format='JPEG') # Save resize image to bytes
  output.seek(0)

  content_file = ContentFile(output.read())  # Read output and create ContentFile in memory
  img_file = File(content_file)

  random_name = f'{uuid.uuid4()}.jpeg'
  image_field.save(random_name, img_file, save=False)

class FormSaveMixin(object):
  form_class = None

  def get_form(self):
    post_data = ExtractPostRequestData(self.request)
    form = self.form_class(post_data)
    return form

  def save_form(self, form):
    try:
      obj = form.save(commit=False)
      obj = self.update_saved_object(self.request, obj, *self.args, **self.kwargs)
      obj.save()
    except:
      raise ValidationError('Unexpected error happened')

  def post(self, request, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs
    self.request = request

    form = self.get_form()
    if not form.is_valid():
      return HttpResponse(form.get_error_message(), status=400)

    self.save_form(form)
    return HttpResponse(status=201)

  def update_saved_object(self, request, obj, *args, **kwargs):
    return obj

