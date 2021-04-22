from django.http import HttpResponse
import re
from random import randint
import PIL

class MyImageHandler:
  @staticmethod
  def get_random_rgb_nums() -> tuple:
    return [randint(0, 255) for _ in range(3)]

  @staticmethod
  def get_color_best_contrast_bw(color:str) -> str:
    white = (255,255,255)
    black = (0,0,0)

    if not color.startswith('rgb('):
      return black

    nums = list(map(int, color[4:-1].replace(' ', '').split(',')))
    avr = sum(nums) / len(nums)

    if avr <= 127.5: clr = white
    else: clr = black

    return clr

  @staticmethod
  def handle_user_color(color:str, force_get:bool=True) -> str:
    if color == None:
      random_rgb = MyImageHandler.get_random_rgb_nums()
      clr = 'rgb({}, {}, {})'.format(*random_rgb)

    elif re.fullmatch(r'[a-fA-F0-9]{3,6}', color): clr = f'#{color}'
    else: clr = color

    # elif re.fullmatch(r'[a-z]+', color) or color.startswith('rgb('):
    return clr

  @staticmethod
  def image_response(image:PIL.Image) -> HttpResponse:
    image_type = 'png' if image.mode == 'RGBA' else 'jpeg'

    response = HttpResponse(content_type=f"image/{image_type}")
    image.save(response, image_type)

    return response

