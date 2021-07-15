import re, base64, qrcode # BytesIO


from io import BytesIO
from random import randint
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse


class MyImageHandler:
  @staticmethod
  def get_random_rgb_nums() -> tuple:
    return [randint(0, 255) for _ in range(3)]

  @staticmethod
  def get_random_color() -> str:
    random_rgb = MyImageHandler.get_random_rgb_nums()
    color = 'rgb({}, {}, {})'.format(*random_rgb)
    return color

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
  def handle_color(color, force=True):
    HEX_PATTERN = r'[a-fA-F0-9]{3,6}'
    cases = [
      (
        lambda c: c == None and force, 
        lambda c: MyImageHandler.get_random_color()
      ),
      
      (
        lambda c: re.fullmatch(HEX_PATTERN, c), 
        lambda c: f'#{c}'
      )
    ]

    handled_color =  color
    for condition, get_color in cases:
      if condition(color):
        handled_color = get_color(color)
        break

    return handled_color

  @staticmethod
  def image_response(image:Image) -> HttpResponse:
    image_type = 'png' if image.mode == 'RGBA' else 'jpeg'

    response = HttpResponse(content_type=f"image/{image_type}")
    image.save(response, image_type)

    return response

  # tools main functions
  @staticmethod
  def generate_placeholder_image(width, height, color):
    image = Image.new('RGB', (width, height), color)
    return image

  @staticmethod
  def generate_avatar_image(size, username, color):
    width = height = size
    user_letters = ''.join([name[0] for name in username.split(' ')[:2]]).upper()
    text_color = MyImageHandler.get_color_best_contrast_bw(color)

    image = MyImageHandler.generate_placeholder_image(width, height, color)
    draw = ImageDraw.Draw(image)

    fontsize = int(size * 2/4)
    font = ImageFont.truetype('./static/fonts/Nonserif.ttf', fontsize)
    # position text
    textwidth, textheight = draw.textsize(user_letters, font=font)
    x = (width - textwidth) / 2
    y = (height - textheight) / 2 - (size*20/400)
    # draw text
    draw.text((x, y), user_letters, fill=text_color, font=font)

    return image # maybe return draw -- i will test it


  @staticmethod
  def generate_thumbnail(image_file, new_width):
    image = Image.open(image_file)
    width, height = image.size
    new_height = new_width * height / width
    image.thumbnail((new_width, new_height), Image.ANTIALIAS)

    return image

  @staticmethod
  def generate_cleaned_image_form_exif(image_file):
    image = Image.open(image_file)

    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    return image_without_exif

  @staticmethod
  def generate_b64_from_image(image_file):
    image_name = image_file.name

    image_ext = 'jpeg'
    if '.' in image_name:
      image_ext = image_name.split('.')[-1]

    image_b64 = base64.b64encode(image_file.read())
    image_b64 = str(image_b64)[2:-1]

    prefix = f'data:image/{image_ext};base64,'
    b64 = prefix + image_b64

    return b64


  @staticmethod
  def generate_image_from_b64(b64):
    image_b64 = re.sub(r'^data:image/\w+?;base64,', '', image_b64)
    image = Image.open(BytesIO(base64.b64decode(image_b64)))

    return image

  @staticmethod
  def generate_qr_code(string):
    image = qrcode.make(string)
    return image