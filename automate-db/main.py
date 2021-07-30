from toolsframe.models import Tool, Category, ToolViewsFunctions
import json


tools_doc_file = 'automate-db/tools-doc.json'

def read_file(location):
  with open(location, 'r') as f:
    data = f.read()

  if location.endswith('.json'):
    data = json.loads(data)

  return data

def write_file(location, data):
  if type(data) != str:
    data = json.dumps(data, indent=2)

  with open(location, 'w') as f:
    f.write(data)


class ToolCreator:
  def __init__(self, tool):
    self.tool = tool

  def get_or_create(self, model, **kwargs):
    obj = model.objects.filter(**kwargs).first()
    if not obj:
      obj = model.objects.create(**kwargs)
    return obj

  def create(self):
    tool_fields = {
      'name': self.tool.get('name'),
      'description': self.tool.get('description'),
      'app_type': self.tool.get('type'),
      'endpoints': self.tool.get('endpoints')
    }

    tool = Tool.objects.create(**tool_fields)

    categories = self.tool.get('category')
    for name in categories:
      category = self.get_or_create(Category, name=name)
      tool.category.add(category)

    return tool

  def update(self):
    tool = Tool.objects.get(tool_id=self.tool.get('tool_id'))

    tool.name = self.tool.get('name')
    tool.description = self.tool.get('description')
    tool.app_type = self.tool.get('type')
    tool.endpoints = self.tool.get('endpoints')

    tool.save()
    tool.category.clear()

    categories = self.tool.get('category')
    for name in categories:
      category = self.get_or_create(Category, name=name)
      tool.category.add(category)
    
    return tool


tools = read_file(tools_doc_file)

updated_tools = {}
print('## set tool docs ##')
for name, info in tools.items():
  print(name)

  is_changed = info.get('is_changed', True)
  if not is_changed:
    updated_tools.update({name: info})
    continue

  tool = ToolCreator({ **info, 'name': name })
  if info.get('tool_id'): 
    tool_obj = tool.update()
  else: 
    tool_obj = tool.create()
    info.update({ 'tool_id': tool_obj.tool_id })

  info.update({ 'is_changed': False })
  updated_tools.update({name: info})

write_file(tools_doc_file, updated_tools)

print('\n\n')
# set tool views
tools_views_names = [
  "get_my_ip",
  "get_my_proxy_anonimity",
  "get_my_request_headers",
  "analyze_my_machine_user_agent",
  "analyze_user_agent",
  "get_image_placeholder",
  "convert_username_to_profile_pic",
  "convert_image_to_thumbnail",
  "remove_image_meta_data",
  "convert_image_to_b64", "convert_b64_to_image",
  "generate_qrcode",
  "get_fb_user_id",
  "cors_proxy",
  "unshorten_url",
]
print('## set tool_views_functions ##')
for name in tools_views_names:
  print(name)
  if not ToolViewsFunctions.objects.filter(name=name).first():
    ToolViewsFunctions.objects.create(name=name)


## to run ##
# 1 # python manage.py shell
# 2 # exec(open('automate-db/main.py').read())
