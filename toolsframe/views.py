from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Category, Tool
from decorators import require_http_methods

@require_http_methods(['GET'])
def index(request):
  context = {
    'categories': Category.objects.all(),
    'user': request.user
  }

  return render(request, 'homepage.html', context)


@require_http_methods(['GET'])
def get_tool_page(request, tool_id):
  context = {
    'tool': get_object_or_404(Tool, tool_id=tool_id)
  }
  return render(request, 'tool-explain.html', context)