import os
from bs4 import BeautifulSoup
import re

root = '../'
CLASSES_IN_JAVASCRIPT_FILES = 'bg-green-700 bg-red-700 bg-red-700 translate-x-full lds-ripple mb-2 mb-2 text-primary-700 bg-green-700 bg-yellow-700 bg-red-700 bg-blue-700 notification fixed py-3 px-5 text-center right-0 bottom-10 capitalize text-white font-bold opacity-70 transition transform translate-x-full z-10'.split(' ')

def load_files(root:str, ext:str) -> list:
  paths = []
  for path, dirs, files in os.walk(root):
    for f in files:
      if f.endswith(ext):
        paths.append(f'{path}/{f}')

  return paths

def load_html_files(root:str) -> list:
  return load_files(root, '.html')

def load_css_files(root:str) -> list:
  return load_files(root, '.min.css')

def read(path:str) -> str:
  with open(path) as f:
    data = f.read()

  return data

def write(path:str, data: str) -> None:
  with open(f'{path}.css', 'w') as f:
    f.write(data)

def append(path:str, data: str) -> None:
  with open(f'{path}', 'a') as f:
    f.write(data+'\n')

def get_html_classes(html:str) -> list:
  soup = BeautifulSoup(html, 'html.parser')
  elms = soup.find_all(class_=True)
  classes = []
  for elm in elms:
    classes.extend(elm['class'])

  return classes

def get_all_html_classes(htmls:list) -> list:
  classes = CLASSES_IN_JAVASCRIPT_FILES
  for html_path in htmls:
    html = read(html_path)
    classes.extend(get_html_classes(html))

  return tuple(set(classes))

def parse_css(css:str) -> dict:
  OPEN_BRACKET = '{'
  CLOSE_BRACKET = '}'
  BRACKET_STATUS = []

  selector = ''
  props = ''

  rules = {}
  start = -1

  for index, letter in enumerate(css):
    if letter == OPEN_BRACKET:
      BRACKET_STATUS.append(True)
      props += letter
    elif letter == CLOSE_BRACKET:
      BRACKET_STATUS.pop()
      props += letter
    elif len(BRACKET_STATUS) > 0:
      props += letter
    else:
      selector += letter
      if start < 0:
        start = index


    if selector and props and len(BRACKET_STATUS) == 0:
      end = index+1
      rules[selector.strip()] = {'props': props.strip(), 'start': start, 'end': end}
      selector = ''
      props = ''
      start = -1

  return rules

def remove_css_rule(css:str, info:dict) -> str:
  start = info['start']
  end = info['end']
  css = css.replace(css[start: end], ' ' * (end - start))
  return css

def replace_css_rule(css:str, info:dict, new_css_part:str) -> str:
  start = info['start']
  end = info['end']
  old = css[start: end]

  css = css.replace(old, new_css_part)
  return css

def clean_css_spaces(css:str) -> str:
  cleaners = [
    lambda css: re.sub(r' +', ' ', css),
    lambda css: re.sub(r'\n+', '\n', css),
    lambda css: css.strip(),
  ]

  for clean in cleaners:
    css = clean(css)

  return css


def clean_selector(selector:str) -> str:
  selector = selector.strip()

  concatinating_chars = ('>', '~', '+')
  for char in concatinating_chars:
    selector = selector.replace(char, ' ')

  # if they concats with ' ' then its depended 
  # else they concat with ',' then its independent
  selectors_splitter = (',', ' ')
  for splitter in selectors_splitter:
    if splitter in selector:
      return splitter.join([clean_selector(s) for s in selector.split(splitter) if s.strip()])

  if selector.startswith(':'):
    if '(' in selector and selector[-1] == ')':
      selector = selector.split('(')[-1][:-1]
      selector = clean_selector(selector)
    return selector

  # escape from pseudo class and functions
  if ':' in selector:
    escape_this_char = 'XXXXXXXXXXXXXXX'
    selector = selector.replace('\\:', escape_this_char)
    selector = re.sub(r'\:.+', '', selector)
    selector = selector.replace(escape_this_char, ':')

  escaped_chars = ['.', '/']
  for escape_char in escaped_chars:
    if f'\\{escape_char}' in selector:
      selector = selector.replace(f'\\{escape_char}', escape_char)

  return selector

def smart_split_css_syntax(string:str, splitter:str, starts=['[', '(', '{'], ends=[']', ')', '}'], togglers=('"', "'")):
  parts = []

  skip_quote = False
  last_toggler = None
  skip_bracket = []

  is_skip_splitter = lambda: bool(skip_bracket) or skip_quote

  part = ''
  for i in string:
    if i == splitter and not is_skip_splitter():
      parts.append(part)
      part = ''
      continue
    
    part += i

    if i in togglers and (i == last_toggler or last_toggler == None):
      skip_quote = not skip_quote
      if skip_quote:
        last_toggler = i
      else:
        last_toggler = None

    elif i in starts and not skip_quote:
      skip_bracket.append(True)
    elif i in ends and not skip_quote:
      skip_bracket.pop()

  if part:
    parts.append(part)
    part = ''
  return parts

def check_selector_used(selector:str, used_classes:list):
  selector = selector.strip()
  # print('SELECTOR:', selector)

  used = True
  if ',' in selector:
    selectors = selector.split(',')
    return any([check_selector_used(s, used_classes) for s in selectors if s.strip()])

  if ' ' in selector:
    selectors = smart_split_css_syntax(selector, ' ')
    # print('SMART_SPLIT:', selectors)
    return all([check_selector_used(s.replace(' ', ''), used_classes) for s in selectors if s.strip()])

  if selector.startswith('.'):
    used = selector.strip('.') in used_classes

  # print('SELECTOR:', selector, f'----- ({used})\n')
  return used

def remove_unused_css(css:str, used_classes:list) -> str:
  parsed = parse_css(css)

  for selector, info in parsed.items():
    if selector.startswith('@'): 
      if selector.startswith('@media'):
        css_in_media_query = info['props'][1:-1]
        css_in_media_query = remove_unused_css(css_in_media_query, used_classes)

        new_media = selector + '{' + css_in_media_query + '}'
        if not css_in_media_query.strip():
          new_media = ' ' * len(new_media)
        css = replace_css_rule(css, info, new_media)

      continue

    temp_selector = clean_selector(selector)
    used = check_selector_used(temp_selector, used_classes)

    if not used:
      # print(f'REMOVE: {selector}')
      css = remove_css_rule(css, info)

  return css


css_comment_regex = r'/\*(\n|.)+?\*/'
htmls = load_html_files(root)
csses = load_css_files(root)

html_classes = get_all_html_classes(htmls)


print(html_classes, '\n\n')

for css_path in csses:
  print('\n\nCSS_FILE: ', css_path)

  css = read(css_path)
  new_css = remove_unused_css(css, html_classes)
  new_css = clean_css_spaces(new_css)

  print('CSS_FILE: ', css_path, f'--- ({100 - round(len(new_css)/len(css) * 100, 2)}%) SMALLER \n')
  write(css_path, new_css)

