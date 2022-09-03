from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from .models import FHostModel

from utils.views_mixins import JsonResponseOverride
from utils.mixins import ExtractPostRequestData
from utils.decorators import required_post_fields
from utils.helpers import Redirector

import youtube_dl
from pytube import YouTube

import urllib.parse


def nothing(request):
  return Redirector.go_home()




#--------------------- undescriped tools ---------------------#
def get_fhost(request, file_name):
  def get_domain(url):
    if not url:
      return 'Not Found Url'
    return '.'.join(url.split('://', 1)[-1].split('/', 1)[0].split('.')[-2:])

  obj = FHostModel.objects.get(file_name=file_name)
  origin_url = get_domain(request.META.get('HTTP_REFERER', None))

  if obj.is_public or origin_url in obj.allowed_origins:
    content_types = {'js': 'application/javascript', 'css': 'text/css', }
    default_content_type = 'text/plain'
    file_ext = file_name.split('.')[-1]
    file_type = content_types.get(file_ext, default_content_type)

    response = HttpResponse(obj.text)
    response['Content-Type'] = file_type
  else:
    response = HttpResponseForbidden()

  return response


@require_http_methods(['POST'])
@required_post_fields(['video_url'])
def convert_youtube_video_to_stream_audio(request):
  post_data = ExtractPostRequestData(request)
  video_url = post_data.get('video_url')

  def generate_url_with_proxy(url):
    base_url = "https://api.webscrapingapi.com/v1"

    params = {
      "api_key":"0qJn8jcUHl6LjxYsEbO7vgHJvEqk1ryl",
      "url": url,
      "device": "desktop",
      "proxy_type":"datacenter"
    }

    return base_url + '/?' + urllib.parse.urlencode(params)

  def read_from_dict(data, key):
    if '.' in key:
      parent, children = key.split('.', 1)
      return read_from_dict(data[parent], children)
    return {key: data.get(key, '')}

  def convert_video_url_to_audio_url_method1(video_url) -> str:
    options ={ 'format':'bestaudio/best', 'keepvideo':False, }

    with youtube_dl.YoutubeDL(options) as ydl:
      audio_info = ydl.extract_info(video_url, download=False)

    audio_url = audio_info['formats'][0]['url']
    return audio_url

  def convert_video_url_to_audio_url_method2(video_url) -> str:
    yt = YouTube(video_url, generate_url_with_proxy=generate_url_with_proxy)
    stream = yt.streams.get_audio_only()
    data = yt.vid_info['videoDetails']

    result = {'audio_url': stream.url}
    tuple(map(lambda key: result.update(read_from_dict(data, key)), [
      'videoId', 'title', 'lengthSeconds', 'keywords', 'channelId',
      'shortDescription', 'thumbnail.thumbnails', 'viewCount', 'author',
    ]))
    return result

  try:
    video_data = convert_video_url_to_audio_url_method2(video_url)
  except:
    return HttpResponseBadRequest('somthing went wrong, make sure you send a youtube url and try again.')

  return JsonResponseOverride(video_data)


